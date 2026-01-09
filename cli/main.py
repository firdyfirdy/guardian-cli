"""
Guardian CLI - Main entry point
AI-Powered Penetration Testing Automation Tool
"""

import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from pathlib import Path
import sys

# Import command groups
from cli.commands import init, scan, recon, analyze, report, workflow, ai_explain

# Initialize Typer app
app = typer.Typer(
    name="guardian",
    help="🔐 Guardian - AI-Powered Penetration Testing CLI Tool",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()

# Register command groups
app.command(name="init")(init.init_command)
app.command(name="scan")(scan.scan_command)
app.command(name="recon")(recon.recon_command)
app.command(name="analyze")(analyze.analyze_command)
app.command(name="report")(report.report_command)  
app.command(name="workflow")(workflow.workflow_command)
app.command(name="ai")(ai_explain.explain_command)

# Register Antigravity Auth commands
try:
    from antigravity_auth.cli.main import auth_app as antigravity_auth_app
    app.add_typer(antigravity_auth_app, name="auth", help="🔐 Manage Antigravity Authentication")
except ImportError:
    console.print("[yellow]Warning: Antigravity Auth library not found. Auth commands disabled.[/yellow]")


@app.callback()
def callback():
    """
    Guardian - AI-Powered Penetration Testing CLI Tool
    
    Leverage Google Gemini AI to orchestrate intelligent penetration testing workflows.
    """
    pass


def version_callback(value: bool):
    """Print version and exit"""
    if value:
        console.print("[bold green]Guardian[/bold green] v0.1.0")
        console.print("AI-Powered Penetration Testing Tool")
        raise typer.Exit()


@app.command()
def version(
    show: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True
    )
):
    """Show Guardian version"""
    pass


def main():
    """Main entry point"""
    try:
        # Display banner
        banner = """
╔═══════════════════════════════════════════╗
║   🔐 GUARDIAN - AI Pentest Automation    ║
║   Powered by Google Gemini & LangChain   ║
╚═══════════════════════════════════════════╝
"""
        console.print(banner, style="bold cyan")
        
        # Run app
        app()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if logged in before running
    try:
        from antigravity_auth import AntigravityService, NoAccountsError
        service = AntigravityService(quiet_mode=True)
        if not service.get_accounts():
             console.print("[yellow]⚠️  No Antigravity accounts found.[/yellow]")
             console.print("[yellow]   Please run 'guardian auth login' to authenticate before using AI features.[/yellow]\n")
    except ImportError:
        pass
    except Exception:
        pass

    main()
