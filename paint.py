# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
#import win32gui
#import win32con
import time
#from win32api import GetSystemMetrics
import subprocess
import pyautogui
import smtplib
import json
from rich.console import Console
from rich.panel import Panel
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()

# instantiate an MCP server client
#mcp = FastMCP("Calculator")
mcp = FastMCP("Custom")

# DEFINE TOOLS


@mcp.tool()
def show_reasoning(steps: list) -> TextContent:
    """Show the step-by-step reasoning process"""
    console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(steps, 1):
        console.print(Panel(
            f"{step}",
            title=f"Step {i}",
            border_style="cyan"
        ))
    return TextContent(
        type="text",
        text="Reasoning shown"
    )

@mcp.tool()
def verify(expression: str, expected: float) -> TextContent:
    """Verify if a calculation is correct"""
    console.print("[blue]FUNCTION CALL:[/blue] verify()")
    console.print(f"[blue]Verifying:[/blue] {expression} = {expected}")
    try:
        actual = float(eval(expression))
        is_correct = abs(actual - float(expected)) < 1e-10
        
        if is_correct:
            console.print(f"[green]✓ Correct! {expression} = {expected}[/green]")
        else:
            console.print(f"[red]✗ Incorrect! {expression} should be {actual}, got {expected}[/red]")
            
        return TextContent(
            type="text",
            text=str(is_correct)
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )

#addition tool
# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """CALCULATE:Add two numbers"""
#     print("CALLED: add(a: int, b: int) -> int:")
#     return int(a + b)


@mcp.tool()
def add(text: str) -> int:
    """CALCULATE:Add two numbers"""
    print("CALLED: add(text: str) -> int:")
    return int(text)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
# @mcp.tool()
# def multiply(param1: int, param2: int) -> int:
#     """Multiply two numbers."""
#     logger.info(f"TEST MESSAGE")
#     logger.debug(f"CALLED: multiply(param1={param1}, param2={param2})")
#     try:
#         result = param1 * param2
#         logger.debug(f"Multiplying {param1} and {param2} to get {result}")
#         return result
#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}")
#         return None


@mcp.tool()
def multiply(step: dict) -> int:
    """Multiply two numbers from fa JSON string"""
    logger.info(f"TEST MESSAGE")
    #logger.debug(f"CALLED: multiply(json_object: dict) -> int:" + json_object)
    try:
        #data = json.loads(json_object)
        a = int(step['params']['param1'])
        b = int(step['params']['param2'])
        result = int(a * b)
        logger.debug(f"Multiplying {a} and {b} to get {result}")
        return result
    except json.JSONDecodeError as e:
        #print(f"Error decoding JSON: {e}")
        logger.error(f"Error decoding JSON: {e}")
        return None  # Or raise an exception, depending on your error handling strategy
    except KeyError as e:
        #print(f"Missing key in JSON: {e}")
        logger.error(f"Missing key in JSON: {e}")
        return None # Or raise an exception
    except Exception as e:
        #print(f"An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}")
        return None
    
# # multiplication tool
# @mcp.tool()
# def multiply(json_string: str) -> int:
#     """Multiply two numbers from a JSON string"""
#     print("CALLED: multiply(json_string: str) -> int:")
#     try:
#         data = json.loads(json_string)
#         a = int(data['a'])
#         b = int(data['b'])
#         result = int(a * b)
#         print(f"Multiplying {a} and {b} to get {result}")
#         return result
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON: {e}")
#         return None  # Or raise an exception, depending on your error handling strategy
#     except KeyError as e:
#         print(f"Missing key in JSON: {e}")
#         return None # Or raise an exception
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return None

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def draw_rectangle():
    """Draw a rectangle in Paint """

    global paint_pid
    try:

        pyautogui.moveTo(842, 146)  # Example position of the rectangle tool
        pyautogui.click()
        time.sleep(0.5)
        
        # Click on the Rectangle tool using the correct coordinates 
        
        #time.sleep(2)
        pyautogui.moveTo(800, 500)  # Starting point
        pyautogui.mouseDown()  # Press down the mouse button to start drawing
        time.sleep(0.1)  # Short delay to ensure the mouse is down

        # Move to the end point of the rectangle
        pyautogui.moveTo(1500, 400)  # End point
        pyautogui.mouseUp()
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"this is my code :Rectangle is drawn"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
#async def add_text_in_paint(json_string: str) -> dict:
async def add_text_in_paint(json_string: dict) -> dict:
    """Add text in Paint from a JSON string"""
    global paint_pid
    try:
        # data = json.loads(json_string)
        # text = data['text']
        text = json_string['text']

        if not paint_pid:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window using the process ID
        paint_window = Application().connect(process=paint_pid).window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(10)
        
        time.sleep(0.5)  # Wait for the rectangle to be drawn
        pyautogui.moveTo(565, 155)  # Adjust coordinates for the text tool
        pyautogui.click()  # Click to select the text tool
        time.sleep(0.5)

        # Step 5: Click inside the rectangle to place the text box
        pyautogui.moveTo(1000, 450)  # Adjust to a position inside the rectangle
        pyautogui.click()  # Click to place the text box
        time.sleep(0.5)

        # Step 6: Type the text
        pyautogui.typewrite(f"{text}")  # Type the text inside the rectangle

        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'the final answer is {text}' added successfully"
                )
            ]
        }
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error decoding JSON: {str(e)}"
                )
            ]
        }
    except KeyError as e:
        print(f"Missing key in JSON: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Missing key in JSON: {str(e)}"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint maximized on my monitor"""
    global paint_pid
    try:
        p = subprocess.Popen('mspaint')
        paint_pid = p.pid
        time.sleep(2)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully and maximized"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }
# DEFINE RESOURCES
@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email"""
    print("CALLED: send_email(to: str, subject: str, body: str) -> dict:")
    
    # Load email configuration from JSON file
    with open('config.json') as config_file:
        config = json.load(config_file)
    
    email = config['email']
    password = config['password']
    
    # Create the email headers
    message = f"Subject: {subject}\n\n{body}"  # Format the email with subject and body
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, to, message)  # Send the email with the formatted message
    server.quit()
    
#    return "Email sent successfully"

# Call the function
#send_email(to="labjuno2022@gmail.com", subject="Tested2 Email Subject", body="The2 is the body of the email.")

    return {
        "content": [
            TextContent(
                 type="text",
                    text="Email sent successfully"
                )
            ]
        }

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
