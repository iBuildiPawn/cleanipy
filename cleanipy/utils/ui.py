"""
Terminal UI utilities for CleanIPy.
"""
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm
from rich.panel import Panel
from rich.text import Text


# Create a console instance
console = Console()


def print_header(text: str) -> None:
    """
    Print a header with the given text.

    Args:
        text: Header text
    """
    console.print(f"\n[bold blue]{text}[/bold blue]")
    console.print("=" * len(text))


def print_subheader(text: str) -> None:
    """
    Print a subheader with the given text.

    Args:
        text: Subheader text
    """
    console.print(f"\n[bold cyan]{text}[/bold cyan]")
    console.print("-" * len(text))


def print_success(text: str) -> None:
    """
    Print a success message.

    Args:
        text: Success message
    """
    console.print(f"[bold green]✓ {text}[/bold green]")


def print_warning(text: str) -> None:
    """
    Print a warning message.

    Args:
        text: Warning message
    """
    console.print(f"[bold yellow]⚠ {text}[/bold yellow]")


def print_error(text: str) -> None:
    """
    Print an error message.

    Args:
        text: Error message
    """
    console.print(f"[bold red]✗ {text}[/bold red]")


def print_info(text: str) -> None:
    """
    Print an info message.

    Args:
        text: Info message
    """
    console.print(f"[bold white]ℹ {text}[/bold white]")


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Ask for confirmation before performing an action.

    Args:
        prompt: Confirmation prompt
        default: Default value if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    return Confirm.ask(prompt, default=default)


def create_table(title: str, columns: List[str]) -> Table:
    """
    Create a table with the given title and columns.

    Args:
        title: Table title
        columns: List of column names

    Returns:
        Rich Table object
    """
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    return table


def display_table(table: Table) -> None:
    """
    Display a table.

    Args:
        table: Rich Table object
    """
    console.print(table)


def create_progress_bar(description: str = "Processing") -> Progress:
    """
    Create a progress bar.

    Args:
        description: Description of the task

    Returns:
        Rich Progress object
    """
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn()
    )


def display_menu(title: str, options: List[str]) -> int:
    """
    Display a menu and get user selection.

    Args:
        title: Menu title
        options: List of menu options

    Returns:
        Index of selected option (0-based)
    """
    print_header(title)

    for i, option in enumerate(options, 1):
        console.print(f"[cyan]{i}.[/cyan] {option}")

    console.print("\n[bold]Enter your choice (1-{}):[/bold] ".format(len(options)), end="")

    while True:
        try:
            choice = int(input())
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                console.print("[bold red]Invalid choice. Please try again:[/bold red] ", end="")
        except ValueError:
            console.print("[bold red]Please enter a number:[/bold red] ", end="")


def display_panel(title: str, content: str) -> None:
    """
    Display content in a panel.

    Args:
        title: Panel title
        content: Panel content
    """
    panel = Panel(Text(content), title=title)
    console.print(panel)
