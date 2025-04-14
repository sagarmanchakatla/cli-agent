import sys
import time
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt
from rich import print as rprint
import aiService
import executor

console = Console()

def execute_plan(plan: List[Dict[str, Any]]) -> bool:
    """Execute each step in the plan and return overall success status."""
    overall_success = True
    
    for i, step in enumerate(plan):
        console.print(f"\n[bold cyan]Executing Step {i+1}:[/bold cyan] {step['description']}")
        console.print(f"[dim]Command ({step['type']}): {step['command']}[/dim]")
        print(step)
        with console.status(f"[bold green]Running...[/bold green]"):
            success, output = executor.execute_command(step)
        
        if success:
            console.print(Panel.fit(
                output.strip() if output.strip() else "Command executed successfully (no output)",
                title="✅ Success",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                output,
                title="❌ Error",
                border_style="red"
            ))
            overall_success = False
            break
    
    return overall_success

def display_plan(plan: List[Dict[str, Any]]):
    """Display the generated plan to the user."""
    console.print(Panel.fit(
        Markdown("# Execution Plan\n\n" + "\n".join([
            f"## Step {i+1}: {step['description']}\n"
            f"```{step['type']}\n{step['command']}\n```"
            for i, step in enumerate(plan)
        ])),
        title="📋 Generated Plan",
        border_style="green"
    ))

def main():
    console.print(Panel.fit("[bold blue]Task Agent[/bold blue]\n"
        "An AI-powered assistant that helps you execute tasks on your computer.\n"
        "Enter a task description, and I'll generate and execute a plan for you.",
        title="🤖 Welcome",
        border_style="blue"))
    
    task_description = Prompt.ask("\n[bold]Enter the task you want to perform[/bold]")


    while True:
        with console.status("[bold green]Generating task plan...[/bold green]"):
            plan = aiService.generate_task_plan(task_description)
            
        display_plan(plan)
        
        if not Confirm.ask("\n[bold]Do you approve this plan?[/bold]"):
            console.print("[yellow]Plan rejected. Exiting.[/yellow]")
            sys.exit(0)
            
        # Execute the plan
        success = execute_plan(plan)
        
        # Check if the task was successful
        if success:
            task_successful = Confirm.ask("\n[bold]Was the task completed successfully?[/bold]")
            if task_successful:
                console.print("[bold green]Task completed successfully! Exiting.[/bold green]")
                break
            else:
                # Get feedback for refinement
                feedback = Prompt.ask("\n[bold]Please describe what went wrong or what needs improvement[/bold]")
                with console.status("[bold green]Refining task plan...[/bold green]"):
                    plan = aiService.refine_task(task_description, feedback)
                console.print("[yellow]Generated a refined plan based on your feedback.[/yellow]")
        else:
            # Task execution failed
            feedback = Prompt.ask("\n[bold]Would you like to refine the task and try again? If yes, please provide details about what went wrong[/bold]")
            if not feedback or feedback.lower() in ["no", "n", "exit", "quit"]:
                console.print("[yellow]Exiting without completing the task.[/yellow]")
                break
                
            with console.status("[bold green]Refining task plan...[/bold green]"):
                plan = aiService.refine_task(task_description, feedback)
            console.print("[yellow]Generated a refined plan based on your feedback.[/yellow]")
            
            
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user. Exiting.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {str(e)}")
        sys.exit(1)