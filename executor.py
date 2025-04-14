import subprocess
import tempfile
import os
from typing import Dict, Any, Tuple
import sys

def execute_command(step: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Execute a command based on its type.
    
    Args:
        step: Command step object with description, command, and type
        
    Returns:
        Tuple of (success, output/error message)
    """
    command_type = step.get("type", "shell")
    command = step.get("command", "")
    
    if not command:
        return False, "Empty command provided"
        
    try:
        if command_type == "shell":
            # Execute shell command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, f"Command failed with error: {result.stderr}"
                
        elif command_type == "python":
            # Execute Python code in a temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_filename = temp_file.name
                temp_file.write(command)
                
            try:
                # Run the Python script and capture output
                result = subprocess.run(
                    [sys.executable, temp_filename],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    return False, f"Python code execution failed: {result.stderr}"
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        else:
            return False, f"Unsupported command type: {command_type}"
            
    except Exception as e:
        return False, f"Error executing command: {str(e)}"