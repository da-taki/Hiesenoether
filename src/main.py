#!/usr/bin/env python3
"""
Hiesenoether Language Runner

Usage:
    python main.py <file.hn>
    python main.py --repl
"""

import sys
from pathlib import Path
from runtime import run_program


def run_file(filepath: str):
    """Run a Hiesenoether program from a file"""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    if not path.suffix == '.hn':
        print(f"Warning: File '{filepath}' does not have .hn extension")
    
    source = path.read_text()
    
    print(f"## Running {filepath}")
    print("=" * 50)
    run_program(source)
    print("=" * 50)


def repl():
    """Start an interactive REPL"""
    from src.runtime import Runtime
    from src.parser import parse
    
    runtime = Runtime()
    print("Hiesenoether REPL")
    print("Type 'exit' to quit, 'help' for help")
    print("=" * 50)
    
    # Start with default energy
    runtime.energy.set_initial_energy(100)
    
    while True:
        try:
            line = input(">>> ")
            
            if line.strip() == 'exit':
                break
            
            if line.strip() == 'help':
                print("Commands:")
                print("  exit - Exit the REPL")
                print("  help - Show this help")
                print("  energy - Show current energy")
                continue
            
            if line.strip() == 'energy':
                print(f"Energy: {runtime.energy.get_energy()}/{runtime.energy.get_max_energy()}")
                continue
            
            if not line.strip():
                continue
            
            # Parse and execute
            ast = parse(line)
            runtime.run(ast)
            
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py <file.hn>")
        print("  python main.py --repl")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == '--repl':
        repl()
    else:
        run_file(arg)


if __name__ == '__main__':
    main()