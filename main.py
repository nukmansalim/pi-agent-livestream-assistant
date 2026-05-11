#!/usr/bin/env python3
"""
Pi Agent - Main Entry Point

Usage:
    python main.py telegram   # Run Telegram bot interface
    python main.py            # Show menu
"""

import sys
import os

def show_menu():
    """Show available interfaces."""
    menu = """
🎬 Pi Agent - YouTube Manager

This project serves as a YouTube skill provider for Pi Agent CLI.
The skill is exposed via the REST API.

Usage:
  python pi_agent_rest_api.py   # Run the REST API server
  python main.py --help         # Show help
"""
    print(menu)

def main_cli():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        show_menu()
        return
    
    command = sys.argv[1].lower()
    
    if command in ["--help", "-h", "help"]:
        show_menu()
    else:
        print(f"❌ Unknown command: {command}")
        print("\nUse: python main.py --help")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main_cli()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
