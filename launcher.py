"""
Portfolio Analyzer - Portable Launcher
Runs with Supabase cloud database
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("  Portfolio Analyzer - Supabase Edition")
    print("="*60 + "\n")
    
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys.executable).parent
    else:
        # Running as script
        app_dir = Path(__file__).parent
    
    os.chdir(app_dir)
    
    # Check for .env file
    env_file = app_dir / ".env"
    if not env_file.exists():
        print("❌ ERROR: .env file not found!")
        print("\nPlease create a .env file with your Supabase connection.")
        print("Template: .env.example")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("✅ Found .env configuration")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # Test database connection
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from sqlalchemy import create_engine, text
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in .env")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print("✅ Connected to Supabase successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nCheck your .env file and internet connection.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Start API server
    print("\n🚀 Starting FastAPI backend...")
    backend_dir = app_dir / "backend"
    
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", 
         "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir),
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    time.sleep(3)
    
    # Start Streamlit UI
    print("🎨 Starting Streamlit UI...")
    ui_dir = app_dir / "ui"
    
    ui_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app_wealth.py",
         "--server.port", "8501", "--server.headless", "true"],
        cwd=str(ui_dir),
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    # Wait for services to start
    print("\n⏳ Waiting for services to start...")
    time.sleep(8)
    
    # Open browser
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:8501")
    
    print("\n" + "="*60)
    print("  ✅ Portfolio Analyzer is Running!")
    print("="*60)
    print("\n  UI:  http://localhost:8501")
    print("  API: http://localhost:8000/docs")
    print("  DB:  Supabase Cloud")
    print("\n  Close this window to stop all services.\n")
    
    try:
        # Keep running and monitor processes
        while True:
            time.sleep(5)
            if api_process.poll() is not None or ui_process.poll() is not None:
                print("\n⚠️  A service stopped unexpectedly!")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    
    # Cleanup
    api_process.terminate()
    ui_process.terminate()
    
    try:
        api_process.wait(timeout=5)
        ui_process.wait(timeout=5)
    except:
        api_process.kill()
        ui_process.kill()
    
    print("✅ Services stopped.\n")

if __name__ == "__main__":
    main()
