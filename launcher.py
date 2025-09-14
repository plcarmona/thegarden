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
    print("1. Web GUI (Recommended - works everywhere)")
    print("2. Desktop GUI (Tkinter - requires desktop environment)")
    print("3. Command Line Interface")
    print("4. Exit")
    print()

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\n🌐 Starting Web GUI...")
            print("This will open a web browser interface with canvas visualization")
            print("Access it at: http://localhost:5001")
            print("Press Ctrl+C to stop the server when done\n")
            
            try:
                # Import and run web GUI
                import web_gui
                web_gui.app.run(debug=False, host='0.0.0.0', port=5001)
            except KeyboardInterrupt:
                print("\n👋 Web GUI stopped")
            except ImportError:
                print("❌ Web GUI dependencies missing. Run: pip install flask flask-cors")
            
        elif choice == '2':
            print("\n🖥️ Starting Desktop GUI (Tkinter)...")
            try:
                # Import and run tkinter GUI
                from gui import main as gui_main
                if not gui_main():  # gui_main returns False on error
                    input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\n👋 Desktop GUI stopped")
            except ImportError as e:
                print(f"❌ Desktop GUI dependencies missing: {e}")
                input("Press Enter to continue...")
                
        elif choice == '3':
            print("\n💻 Starting Command Line Interface...")
            try:
                # Import and run CLI
                from main import main as cli_main
                cli_main()
            except KeyboardInterrupt:
                print("\n👋 CLI stopped")
            
        elif choice == '4':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")
        
        print()  # Empty line for readability

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")