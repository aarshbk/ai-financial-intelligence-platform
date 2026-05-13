"""
Startup Helper Script
Initializes and starts the application
"""
import os
import subprocess
import sys
import time


def print_banner():
    """Print welcome banner"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  🚀 AI Financial Intelligence Platform                    ║
    ║     Powered by FastAPI + Streamlit + ML Models             ║
    ╚════════════════════════════════════════════════════════════╝
    """)


def check_dependencies():
    """Check if all dependencies are installed"""
    print("✓ Checking dependencies...")
    try:
        import fastapi
        import streamlit
        import pandas
        import plotly
        import pdfplumber
        print("✓ All dependencies installed!")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nRun: pip install -r requirements.txt")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n✓ Creating directories...")
    dirs = ["uploads", "data"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  ✓ {d}/")


def start_backend():
    """Start backend API"""
    print("\n" + "="*60)
    print("Starting Backend API...")
    print("="*60)
    print("\nBackend will run on: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop backend\n")
    
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n✓ Backend stopped")


def start_frontend():
    """Start frontend dashboard"""
    print("\n" + "="*60)
    print("Starting Frontend Dashboard...")
    print("="*60)
    print("\nDashboard will run on: http://localhost:8501")
    print("Make sure the backend (port 8000) is running in another terminal!")
    print("\nPress Ctrl+C to stop dashboard\n")
    
    cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n✓ Frontend stopped")


def main():
    """Main startup routine"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Choose mode
    print("\n" + "="*60)
    print("Choose startup mode:")
    print("="*60)
    print("\n1. Start Backend Only (API)")
    print("2. Start Frontend Only (Dashboard)")
    print("3. Start Both (recommended)")
    print("\n(Note: For mode 3, you'll need 2 terminal windows)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
    elif choice == "3":
        print("\n⚠️  Note: You need 2 terminal windows for mode 3")
        print("\nWindow 1: Starting Backend...")
        input("Press Enter to confirm, then open another terminal for frontend")
        start_backend()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
