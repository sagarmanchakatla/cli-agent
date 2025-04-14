import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize the Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Create a client with the API key
client = Groq(api_key=GROQ_API_KEY)

# Set the default model to use (Mistral)
DEFAULT_MODEL = "llama3-70b-8192"

def generate_task_plan(task_description: str) -> List[Dict[str, Any]]:
    """
    Generate a plan of commands to execute the given task using Mistral via Groq.
    
    Args:
        task_description: Description of the task to perform
        
    Returns:
        List of command steps to execute
    """
    prompt = f"""
    You are an assistant that helps users execute tasks on their computer.
    Given the task description, generate a step-by-step plan of commands to execute.
    
    Format your response as a JSON array of command objects. Each object should have:
    - "description": A human-readable description of what this step does
    - "command": The actual command to run (or code to execute)
    - "type": Either "shell" for shell commands or "python" for Python code
    
    Task description: {task_description}
    
    Respond ONLY with the JSON array, no other text. Example format:
    [
        {{
            "description": "Create a directory for the project",
            "command": "mkdir -p my_project",
            "type": "shell"
        }},
        {{
            "description": "Create a Python file with a simple Hello World program",
            "command": "print('Hello, World!')",
            "type": "python"
        }}
    ]
    """
    
    try:
        # Request completion from Groq
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates executable command plans. Always respond with valid JSON in the requested format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more deterministic outputs
            max_tokens=2000
        )
        
        # Extract response text
        text_response = response.choices[0].message.content
        
        # Extract JSON from response if there's any extra text
        start_idx = text_response.find('[')
        end_idx = text_response.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = text_response[start_idx:end_idx]
            return json.loads(json_str)
        
        # If proper markers not found, try loading the whole response
        return json.loads(text_response)
    except Exception as e:
        print(f"Error generating task plan: {e}")
        # Return a simple error message as a step
        return [{"description": "Error generating plan", "command": "echo 'Error generating plan'", "type": "shell"}]

def refine_task(task_description: str, error_message: str) -> List[Dict[str, Any]]:
    """
    Refine the task plan based on error feedback using Mistral via Groq.
    
    Args:
        task_description: Original task description
        error_message: Error message or user feedback
        
    Returns:
        Updated list of command steps
    """
    prompt = f"""
    You are an assistant that helps users execute tasks on their computer.
    A previous plan for the following task failed:
    
    Task description: {task_description}
    
    Error/Feedback: {error_message}
    
    Generate an improved step-by-step plan that addresses the issues.
    Format your response as a JSON array of command objects. Each object should have:
    - "description": A human-readable description of what this step does
    - "command": The actual command to run (or code to execute)
    - "type": Either "shell" for shell commands or "python" for Python code
    
    Respond ONLY with the JSON array, no other text.
    """
    
    try:
        # Request completion from Groq
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates executable command plans. Always respond with valid JSON in the requested format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more deterministic outputs
            max_tokens=2000
        )
        
        # Extract response text
        text_response = response.choices[0].message.content
        
        # Extract JSON from response if there's any extra text
        start_idx = text_response.find('[')
        end_idx = text_response.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = text_response[start_idx:end_idx]
            return json.loads(json_str)
        
        # If proper markers not found, try loading the whole response
        return json.loads(text_response)
    except Exception as e:
        print(f"Error refining task plan: {e}")
        # Return a simple error message as a step
        return [{"description": "Error refining plan", "command": "echo 'Error refining plan'", "type": "shell"}]