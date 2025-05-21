import asyncio
import os
import yaml
from pathlib import Path
from pydantic import BaseModel
from agents import Agent, Runner
from dotenv import load_dotenv
from agents.extensions.models.litellm_model import LitellmModel

load_dotenv()

ANALYZER_INSTRUCTIONS = """
You are a test case generator for NextJS applications. You will analyze a JSON representation of a NextJS codebase and create test cases for critical application functionality.

When you receive the JSON data containing NextJS codebase information (routes, components, API endpoints, etc.), you should:

1. Analyze the application structure to identify key features and user flows
2. Generate 5 practical test cases covering essential functionality
3. Return a Python list of dictionaries, where each dictionary represents one test case

Your output should be a Python list structured as follows:

[
    {
        "name": "Basic Login Test",
        "task": "Verify that users can log in with valid credentials",
        "expected_result": "User should be successfully logged in and redirected to the dashboard",
        "steps": [
            "Navigate to login page",
            "Enter valid credentials",
            "Click login button",
            "Verify successful login"
        ]
        "page": "auth"
    },
    {
        "name": "Password Reset Functionality",
        "task": "Verify that users can reset their password",
        "expected_result": "User should receive a password reset email and be able to set a new password",
        "steps": [
            "Navigate to login page",
            "Click on 'Forgot password' link",
            "Enter registered email",
            "Submit request",
            "Verify success message"
        ],
        "page": "auth"
    }
]


Focus on testing these core areas:
- User authentication (sign-in, sign-up, password reset)
- Main application features identified from routes and components
- Admin functionality (if present)
- Form submissions and critical user workflows
- Page should be the first slug under pages folder. Do not invent it if you dont find it.
Make your test cases realistic, clear, and actionable. Each test should verify a specific, important functionality with 3-8 concrete steps that a tester could follow.

Return only the Python list of dictionaries with no additional text or explanation.
"""

USER_QUERY = """I Analyze the following NextJS codebase structure JSON and generate test cases based on the functionality it contains.
{codebase_json}
Based on this JSON structure representing a NextJS codebase, generate a list of 5 test cases for the most important functionality. Return the test cases as a Python list of dictionaries with the following structure:
"[
    {{
        "name": "Test Name", 
        "task": "Description of what is being tested",
        "expected_result": "Expected outcome of the test",
        "steps": ["Step 1", "Step 2", "Step 3", ...]
    }},
    // More test cases...
]
Focus on key functionality including authentication, admin features, organization/project management, and critical user workflows. """

def generate_test_query(codebase_json_content):
    """
    Generate the query string with the codebase JSON injected
    
    Args:
        codebase_json_content (str): JSON string containing the codebase structure
        
    Returns:
        str: Formatted query with codebase JSON injected
    """
    return USER_QUERY.format(codebase_json=codebase_json_content)

def load_codebase_json_from_file(file_path):
    """
    Load codebase JSON content from a file
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        str: JSON content as a string
    """
    import json
    from pathlib import Path
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return f.read()

def save_test_cases_as_yaml(test_cases):
    """
    Save test cases as individual YAML files
    
    Args:
        test_cases (list): List of TestCase objects
    """
    output_dir = Path("test_cases")
    output_dir.mkdir(exist_ok=True)
    
    for i, test_case in enumerate(test_cases):
        file_name = f"{i+1}_{test_case.name.lower().replace(' ', '_')}.yaml"
        file_path = output_dir / file_name
        
        # Convert the test case to a dictionary
        test_case_dict = test_case.dict()
        
        with open(file_path, 'w') as f:
            yaml.dump(test_case_dict, f, default_flow_style=False)
        
        print(f"Saved test case to {file_path}")

# Example of how to use these functions:
# json_content = load_codebase_json_from_file('path/to/codebase.json')
# query = generate_test_query(json_content)

class TestCase(BaseModel):
    name: str
    task: str
    expected_result: str
    steps: list[str]
    page: str


class TestCaseArray(BaseModel):
    test_cases: list[TestCase]


model = "anthropic/claude-3-7-sonnet-20250219"
api_key = os.getenv("ANTHROPIC_API_KEY")
analyzer_agent = Agent(
    name="Analyzer Agent",
    instructions=ANALYZER_INSTRUCTIONS,
    output_type=TestCaseArray,
    model=LitellmModel(model=model, api_key=api_key),
)

async def main():
    # Load the codebase JSON from the analysis.json file
    json_content = load_codebase_json_from_file('analysis.json')
    
    # Generate the query with the codebase JSON content
    formatted_query = generate_test_query(json_content)
    
    # Run the analyzer agent with the formatted query
    result = await Runner.run(analyzer_agent, formatted_query)
    print(result.final_output)
    
    # Save test cases as YAML files
    save_test_cases_as_yaml(result.final_output.test_cases)

if __name__ == "__main__":
    asyncio.run(main())
