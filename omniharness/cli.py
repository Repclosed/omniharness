"""OmniHarness Command Line Interface.

Provides terminal commands for token compression and agent memory management.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from omniharness import __version__
from omniharness.compressor import compress, estimate_tokens
from omniharness.memory import MemoryEngine

console = Console()

def main() -> None:
    parser = argparse.ArgumentParser(
        description="OmniHarness: Token optimization harness and persistent memory engine for AI agents."
    )
    parser.add_argument("--version", action="version", version=f"omniharness {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init subcommand
    subparsers.add_parser("init", help="Initialize workspace memory and harness environment")

    # Compress subcommand
    compress_parser = subparsers.add_parser("compress", help="Compress text or log output to save tokens")
    compress_parser.add_argument("file", nargs="?", help="File to compress (reads from stdin if omitted)")
    compress_parser.add_argument("-s", "--strategy", default="auto", choices=["auto", "dedup", "traceback", "diff", "trim"], help="Compression strategy")
    compress_parser.add_argument("-m", "--max-tokens", type=int, help="Maximum token budget limit")
    compress_parser.add_argument("--stats", action="store_true", help="Show token estimation stats")

    # Memory subcommand
    memory_parser = subparsers.add_parser("memory", help="Manage persistent agent memories")
    memory_subparsers = memory_parser.add_subparsers(dest="memory_command", help="Memory actions")

    # Memory add
    mem_add = memory_subparsers.add_parser("add", help="Add or update a memory")
    mem_add.add_argument("name", help="Memory slug/name")
    mem_add.add_argument("description", help="Short description")
    mem_add.add_argument("content", help="Memory content markdown")
    mem_add.add_argument("-t", "--type", default="project", choices=["project", "user", "feedback", "reference"], help="Memory type")

    # Memory get
    mem_get = memory_subparsers.add_parser("get", help="Get a memory by name")
    mem_get.add_argument("name", help="Memory name")

    # Memory list
    memory_subparsers.add_parser("list", help="List all stored memories")

    # Memory search
    mem_search = memory_subparsers.add_parser("search", help="Search memories")
    mem_search.add_argument("query", help="Search query")

    # Memory delete
    mem_del = memory_subparsers.add_parser("delete", help="Delete a memory")
    mem_del.add_argument("name", help="Memory name")

    # Status subcommand
    subparsers.add_parser("status", help="Show OmniHarness status and stats")

    args = parser.parse_args()

    if args.command == "init":
        engine = MemoryEngine()
        engine.rebuild_index()
        console.print(Panel(
            f"[bold green]OmniHarness Initialized Successfully![/bold green]\n"
            f"Memory Directory: {engine.memory_dir}\n"
            f"Index File: {engine.memory_dir / 'MEMORY.md'}",
            title="OmniHarness Init",
            border_style="green"
        ))

    elif args.command == "compress":
        if args.file:
            path = Path(args.file)
            if not path.exists():
                console.print(f"[red]Error: File not found: {args.file}[/red]")
                sys.exit(1)
            raw_text = path.read_text(encoding="utf-8")
        else:
            raw_text = sys.stdin.read()

        orig_tokens = estimate_tokens(raw_text)
        compressed_text = compress(raw_text, strategy=args.strategy, max_tokens=args.max_tokens)
        comp_tokens = estimate_tokens(compressed_text)

        console.print(compressed_text)

        if args.stats:
            savings = max(0, orig_tokens - comp_tokens)
            pct = (savings / orig_tokens * 100) if orig_tokens > 0 else 0.0
            console.print(Panel(
                f"[bold cyan]Original Tokens:[/bold cyan] {orig_tokens}\n"
                f"[bold green]Compressed Tokens:[/bold green] {comp_tokens}\n"
                f"[bold yellow]Tokens Saved:[/bold yellow] {savings} ({pct:.1f}%)",
                title="OmniHarness Compression Stats",
                border_style="blue"
            ))

    elif args.command == "memory":
        engine = MemoryEngine()
        if args.memory_command == "add":
            path = engine.add_memory(args.name, args.description, args.content, memory_type=args.type)
            console.print(f"[green]Successfully saved memory to {path}[/green]")
        elif args.memory_command == "get":
            mem = engine.get_memory(args.name)
            if mem:
                console.print(Panel(mem["content"], title=f"Memory: {mem['name']} ({mem['description']})", border_style="green"))
            else:
                console.print(f"[red]Memory not found: {args.name}[/red]")
                sys.exit(1)
        elif args.memory_command == "list":
            mems = engine.list_memories()
            if not mems:
                console.print("[yellow]No memories stored yet.[/yellow]")
            else:
                table = Table(title="Stored Agent Memories")
                table.add_column("Name", style="cyan")
                table.add_column("Description", style="green")
                table.add_column("File", style="dim")
                for m in mems:
                    table.add_row(m["name"], m["description"], m["file"])
                console.print(table)
        elif args.memory_command == "search":
            results = engine.search_memories(args.query)
            if not results:
                console.print(f"[yellow]No memories matching '{args.query}' found.[/yellow]")
            else:
                console.print(f"[bold green]Found {len(results)} matching memories:[/bold green]")
                for r in results:
                    console.print(f" - [cyan]{r['name']}[/cyan]: {r['description']} ([dim]{r['file']}[/dim])")
        elif args.memory_command == "delete":
            success = engine.delete_memory(args.name)
            if success:
                console.print(f"[green]Deleted memory: {args.name}[/green]")
            else:
                console.print(f"[red]Memory not found: {args.name}[/red]")
                sys.exit(1)
        else:
            memory_parser.print_help()

    elif args.command == "status":
        engine = MemoryEngine()
        mems = engine.list_memories()
        console.print(Panel(
            f"[bold]OmniHarness v{__version__}[/bold]\n"
            f"Status: [green]Active & Ready[/green]\n"
            f"Memory Directory: {engine.memory_dir}\n"
            f"Stored Memories: {len(mems)}",
            title="OmniHarness Status",
            border_style="cyan"
        ))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
