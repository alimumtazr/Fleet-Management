#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import webbrowser
import signal
import platform

# Constants
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
BACKEND_CMD = ["uvicorn", "main:app", "--reload"]
FRONTEND_CMD = ["npm", "start"]
FRONTEND_DIR = "frontend"

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.BOLD}{Colors.HEADER}========================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN} Fleet Management System Starter {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}========================================{Colors.ENDC}")
    print()

def initialize_db():
    print(f"{Colors.BLUE}Initializing the database...{Colors.ENDC}")
    try:
        subprocess.run([sys.executable, "init_db.py"], check=True)
        print(f"{Colors.GREEN}Database initialized successfully!{Colors.ENDC}")
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}Failed to initialize the database!{Colors.ENDC}")
        sys.exit(1)

def start_backend():
    print(f"{Colors.BLUE}Starting the backend server...{Colors.ENDC}")
    if platform.system() == "Windows":
        backend_process = subprocess.Popen(BACKEND_CMD, 
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        backend_process = subprocess.Popen(BACKEND_CMD)
    print(f"{Colors.GREEN}Backend server started at {BACKEND_URL}{Colors.ENDC}")
    return backend_process

def start_frontend():
    print(f"{Colors.BLUE}Starting the frontend server...{Colors.ENDC}")
    if platform.system() == "Windows":
        frontend_process = subprocess.Popen(FRONTEND_CMD, cwd=FRONTEND_DIR,
                                          creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        frontend_process = subprocess.Popen(FRONTEND_CMD, cwd=FRONTEND_DIR)
    print(f"{Colors.GREEN}Frontend server started at {FRONTEND_URL}{Colors.ENDC}")
    return frontend_process

def open_in_browser():
    print(f"{Colors.BLUE}Opening application in browser...{Colors.ENDC}")
    time.sleep(3)  # Give the servers a moment to start
    webbrowser.open(FRONTEND_URL)

def main():
    print_header()
    
    # Check if Python virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"{Colors.YELLOW}Warning: You are not in a Python virtual environment.{Colors.ENDC}")
        answer = input("Continue anyway? (y/n): ")
        if answer.lower() not in ['y', 'yes']:
            sys.exit(0)
    
    # Initialize the database
    initialize_db()
    
    # Start the backend and frontend servers
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    # Open the application in the browser
    open_in_browser()
    
    print(f"\n{Colors.YELLOW}Press Ctrl+C to stop the servers{Colors.ENDC}")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.BLUE}Stopping servers...{Colors.ENDC}")
        backend_process.terminate()
        frontend_process.terminate()
        print(f"{Colors.GREEN}Servers stopped!{Colors.ENDC}")

if __name__ == "__main__":
    main() 