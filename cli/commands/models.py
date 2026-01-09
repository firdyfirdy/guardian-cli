"""
guardian models - List available AI models
"""

import typer
from rich.console import Console
from rich.table import Table

console = Console()

def list_models_command():
    """List available AI models and their sources"""
    
    table = Table(title="Available AI Models")
    
    table.add_column("Model Name", style="cyan", no_wrap=True)
    table.add_column("Provider", style="green")
    table.add_column("Source / Quota", style="magenta")
    table.add_column("Capabilities", style="white")

    # Gemini 3 Models (Antigravity Exclusive)
    table.add_row("gemini-3-pro", "Google", "Antigravity", "Reasoning, High Intelligence")
    table.add_row("gemini-3-flash", "Google", "Antigravity", "Reasoning, Speed")
    
    # Gemini 2.5 Models (Standard)
    table.add_row("gemini-2.5-pro", "Google", "Gemini CLI", "General Purpose, Stable")
    table.add_row("gemini-2.5-flash", "Google", "Gemini CLI", "Lower Latency, Cost Effective")
    
    # Claude Models (Proxied via Antigravity)
    table.add_row("claude-sonnet-4-5", "Anthropic", "Antigravity", "Advanced Reasoning, Coding")
    table.add_row("claude-opus-4-5", "Anthropic", "Antigravity", "Maximum Capability")
    
    table.add_section()
    table.add_row("Note:", "", "", "Antigravity models use internal quotas.")

    console.print(table)
