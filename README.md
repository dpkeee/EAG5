# Talk2MCP: AI Agent for Task Automation with Model Context Protocol (MCP)

## Overview

This project demonstrates how to:

- Create MCP tools for different functions.
- Call the MCP tools using structured prompting.
- Pass data to tools in JSON.
- Use Google's Gemini model to interpret natural language requests

## Requirements

-   Python 3.9+
-   `python-dotenv`
-   `mcp` (for MCP client and server functionality)
-   `google-generativeai`
-   `pywinauto` (for automating Windows applications like Paint)
-   `pyautogui` (for controlling the mouse and keyboard)
-   `asyncio`
-   `concurrent.futures`
-   `rich` (for formatted console output)
-   `PIL` (Pillow - for image manipulation)

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/dpkeee/EAG5.git
      ```

2.  **Install the dependencies:**

    ```bash
    pip install python-dotenv mcp google-generativeai pywinauto pyautogui rich Pillow
    ```

3.  **Configure environment variables:**

    -   Create a `.env` file in the project root (or the `Assignment` directory, depending on where you want to keep it).
    -   Add your Gemini API key:

    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```
  

4.  **Start the MCP server ( `paint.py`):**

    ```bash
    python paint.py  # This script acts as the MCP server
    ```

5.  **Run the main application:**

    ```bash
    python talk2mcp1.py
    ```

## Usage

1.  **Start the MCP server (`paint.py`), which exposes the tools for the AI agent to use and handles contextual information.  Ensure Paint is closed before running.**
2.  **Run the `talk2mcp1.py` script to initiate the AI agent and connect to the MCP server.**
3.  **The AI agent will:**
    *   Connect to the MCP server.
    *   Receive a query (currently hardcoded in `talk2mcp1.py`).
    *   Use the Gemini AI model to determine the steps needed to answer the query.
    *   Call the appropriate MCP tools (e.g., `multiply`, `open_paint`, `draw_rectangle`, `add_text_in_paint`).
    *   Automate Microsoft Paint to visually represent the answer.
    

## Code Structure

-   `talk2mcp1.py`: Main script that drives the AI agent. It:
    *   Connects to the MCP server.
    *   Retrieves available tools.
    *   Uses the Gemini AI model to generate a plan.
    *   Calls MCP tools to execute the plan.
    *   Handles the overall workflow and error handling.
-   `paint.py`: A server script that acts as an **MCP server** and exposes the following tools:
    *   `multiply`: Multiplies two numbers.
    *   `open_paint`: Opens Microsoft Paint.
    *   `draw_rectangle`: Draws a rectangle in Paint.
    *   `add_text_in_paint`: Adds text inside the rectangle in Paint.
    *   `send_email`: Sends an email with the result.
    *   It also defines resources like `get_greeting` and prompts like `review_code` and `debug_error`.


