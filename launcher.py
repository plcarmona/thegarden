#!/usr/bin/env python3
"""
Launcher script for The Garden GUI
Provides easy access to both CLI and GUI interfaces
"""

import sys
import os

def show_menu():
    print("🌱 The Garden - Interface Selection")
    print("=" * 40)
    print("Choose an interface:")
    print("1. Web GUI (Recommended)")
    print("2. Command Line Interface")
    print("3. Exit")
    print()

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n🌐 Starting Web GUI...")
            print("This will open a web browser interface with canvas visualization")
            print("Press Ctrl+C to stop the server when done\n")
            
            try:
                # Import and run web GUI
                from web_gui import main as web_main
                web_main()
            except KeyboardInterrupt:
                print("\n👋 Web GUI stopped")
            except ImportError:
                print("❌ Web GUI dependencies missing. Run: pip install flask flask-cors")
            
        elif choice == '2':
            print("\n💻 Starting Command Line Interface...")
            try:
                # Import and run CLI
                from main import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                print("\n👋 CLI stopped")
            
        elif choice == '3':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-3.")
        
        print()  # Empty line for readability

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")