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
    print("1. FastAPI GUI (Recommended - Modern web interface)")
    print("2. Command Line Interface")
    print("3. Exit")
    print()

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n🚀 Starting FastAPI GUI...")
            print("This will open a modern web browser interface with advanced features")
            print("Access it at: http://localhost:5002")
            print("API docs available at: http://localhost:5002/docs")
            print("Press Ctrl+C to stop the server when done\n")
            
            try:
                # Import and run FastAPI GUI
                import fastapi_gui
                fastapi_gui.app.run(debug=False, host='0.0.0.0', port=5002)
            except KeyboardInterrupt:
                print("\n👋 FastAPI GUI stopped")
            except ImportError:
                print("❌ FastAPI GUI dependencies missing. Run: pip install fastapi uvicorn")
            except AttributeError:
                # Handle the fact that FastAPI apps don't have a .run() method like Flask
                try:
                    import uvicorn
                    uvicorn.run(fastapi_gui.app, host='0.0.0.0', port=5002)
                except Exception as e:
                    print(f"❌ Error starting FastAPI GUI: {e}")
                    
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