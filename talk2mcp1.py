import os
import logging
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
#client = genai.Client(api_key=api_key)
client = genai.Client(api_key="AIzaSyAXJ-CEwKh_POvrp5dcL5BYfwoqBZfA68s")

max_iterations = 1

last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    logger.debug("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        logger.debug("LLM generation completed")
        return response
    except TimeoutError:
        logger.error("LLM generation timed out!")
        raise
    except Exception as e:
        logger.error(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main():
    reset_state()  # Reset at the start of main
    logger.info("Starting main execution...")
    try:
        logger.info("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["paint.py"]
        )

        async with stdio_client(server_params) as (read, write):
            logger.info("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                logger.info("Session created, initializing...")
                await session.initialize()
                
                logger.info("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                logger.info(f"Successfully retrieved {len(tools)} tools")

                logger.info("Creating system prompt...")
                logger.info(f"Number of tools: {len(tools)}")
                
                try: 
                    tools_description = []
                    for i, tool in enumerate(tools):
                        try:
                            params = tool.inputSchema
                            desc = getattr(tool, 'description', 'No description available')
                            name = getattr(tool, 'name', f'tool_{i}')
                            
                            if 'properties' in params:
                                param_details = []
                                for param_name, param_info in params['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ', '.join(param_details)
                            else:
                                params_str = 'no parameters'

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                            logger.debug(f"Added description for tool: {tool_desc}")
                        except Exception as e:
                            logger.error(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")
                
                    tools_description = "\n".join(tools_description)
                    logger.info("Successfully created tools description")
                
                except Exception as e:
                    print(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"

                logger.info("Created system prompt...")
                system_prompt = f"""You are an AI agent designed to solve the user's query through step-by-step reasoning, using available tools if needed. Your task is to solve the query, verify the solution, and then open a paint application, draw a rectangle and Add text the final answer inside the rectangle.

Available tools: {tools_description}
Respond only in valid JSON with the following keys: steps, fallback_response, step_number, tool_name ,params, param1, param2, ...  
For each step, use the following structure:

step_number: integer

tool_name: string

params: an object (not a string), containing any needed parameters for the tool.
If the tool does not require parameters, use an empty object {{}} for params.

Example Response:

{{
  "steps": [
    {{
      "step_number": 1,
      "tool_name": "multiply",
      "params": {{
        "param1": 45,
        "param2": 55
      }}
    }},
    {{
      "step_number": 2,
      "tool_name": "open_paint",
      "params": {{}}
    }}
  ],
  "fallback_response": "Your direct response if no tools are needed"
}}

// ❌ Incorrect
"params": {{
  "json_object": "{{\\"a\\": 45, \\"b\\": 55}}"
}}

// ✅ Correct
"params": {{
  "param1": 45,
  "param2": 55
}}

Important:

*   The LLM response MUST be a valid JSON RESPONSE.
*   The `steps` array should contain objects, each representing a step.
*   Each step object MUST have a `step_number`, a `tool_name`, and a `params` object.
*   The `params` object should contain the parameters for the tool as key-value pairs.
*   Do NOT include any additional text, explanations, or formatting.
*   Do NOT include code block indicators such as ```json or ```.
*   After each step, verify the results before moving forward. If the answer seems off, recheck the calculation or reasoning.
*   If the tools are unavailable or you are unsure of the answer, provide a fallback response with suggestions for the next steps.
*   If further clarification is needed from the user, request it and update the context accordingly.

"""
             
                # query = "what is the sum of 45 and 55"
                query = "multiply 45 and 55"
                logger.info("Starting iteration loop...")
                
                global iteration, last_response
                
                while iteration < max_iterations:
                    logger.info(f"\n--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    logger.debug("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        logger.debug(f"LLM Response is this deepika: {response_text}")
                        logger.debug(f"type of response_text: {type(response_text)}")
                        #print('type of response_text', type(response_text))
                    except Exception as e:
                        logger.error(f"Failed to get LLM response: {e}")
                        break

                    if response_text:  # Check if response_text is not empty
                        logger.debug(f"Raw response string: {response_text}")

                        # Remove the code block indicators if present
                        if response_text.startswith("```json"):
                            logger.debug("Found ```json at the beginning")
                            response_text = response_text[7:].strip()  # Remove the ```json part
                            logger.debug(f"Response after removing ```json: {response_text}")
                        if response_text.endswith("```"):
                            logger.debug("Found ``` at the end")
                            response_text = response_text[:-3].strip()  # Remove the ending ```
                            logger.debug(f"Response after removing ending ```: {response_text}")

                        # Check if the response is empty after stripping
                        if not response_text:
                            logger.error("Received an empty response from the LLM.")
                            continue  # Skip to the next iteration or handle the error appropriately

                        try:
                            # Directly parse the JSON response
                            logger.debug(f"type of response_text1: {type(response_text)}")
                            response_json = json.loads(response_text)  # Parse the JSON string

                            for individual_step in response_json['steps']:
                                tool_name = individual_step['tool_name']
                                params = individual_step.get('params', {})  # Extract the 'params' dictionary
                                logger.debug(f"Type of step content: {type(individual_step)}")
                                logger.debug(f"step content: {(individual_step)}")
                                logger.debug(f"Params before calling tool {tool_name}: {params}")
                                logger.debug(f"Type of params: {type(params)}")

                                # Validate required parameters (example)
                                required_params = {
                                    "multiply": ["param1", "param2"],
                                    "open_paint": [],
                                    "draw_rectangle": [],
                                    #"add_text_in_paint": ["text"],
                                    "verify": ["expression", "expected"]
                                }
                                
                                if tool_name in required_params:
                                    missing_params = [param for param in required_params[tool_name] if param not in params]
                                    if missing_params:
                                        logger.error(f"Missing required parameters for tool {tool_name}: {missing_params}")
                                        continue  # Skip to the next iteration or handle the error appropriately

                                # Pass the parameters dictionary if it exists
                                try:
                                    if params:
                                        if tool_name == "multiply":
                                            data = individual_step
                                            wrapped_data = {'step': data}
                                            wrapped_data_dict = dict(wrapped_data)
                                            result = await session.call_tool(tool_name, arguments=wrapped_data_dict)
                                        else:
                                            result = await session.call_tool(tool_name, arguments=params)
                                    else:
                                        result = await session.call_tool(tool_name)  # Call the tool without parameters

                                    # Handle the result as needed
                                    logger.debug(f"Result from {tool_name}: {result}")

                                except ValueError as ve:
                                    logger.error(f"ValueError during tool execution for {tool_name}: {ve}")
                                except TypeError as te:
                                    logger.error(f"TypeError during tool execution for {tool_name}: {te}")
                                except Exception as e:
                                    logger.error(f"An error occurred while processing the LLM response: {e}")

                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode JSON from response: {e}")
                        except Exception as e:
                            logger.error(f"An error occurred while processing the LLM response: {e}")

                        iteration += 1

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        reset_state()  # Reset at the end of main

if __name__ == "__main__":
    asyncio.run(main())
    
    
