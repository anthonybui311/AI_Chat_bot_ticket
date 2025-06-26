import subprocess
import webbrowser
import time
import os
import signal
import sys

def run_fastapi():
    """Run the FastAPI server"""
    api_process = subprocess.Popen(
        ["uvicorn", "working.backend.api_part.api_routes:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return api_process

def run_streamlit():
    """Run the Streamlit server"""
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "working/frontend/app.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return streamlit_process

def main():
    try:
        print("Starting AI Ticket Support Chatbot...")
        
        # Start FastAPI server
        print("Starting FastAPI server...")
        api_process = run_fastapi()
        
        # Wait a bit for FastAPI to start
        time.sleep(2)
        
        # Start Streamlit server
        print("Starting Streamlit frontend...")
        streamlit_process = run_streamlit()
        
        # Wait a bit for Streamlit to start
        time.sleep(3)
        
        # Open web browser
        print("Opening web browser...")
        webbrowser.open("http://localhost:8501")  # Streamlit UI
        print("\nAPI Documentation available at: http://localhost:8000/docs")
        
        print("\n✨ Application is running!")
        print("📝 Streamlit UI: http://localhost:8501")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the application...")
        
        # Keep the main process running
        api_process.wait()
        streamlit_process.wait()
        
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        # Kill both processes
        api_process.terminate()
        streamlit_process.terminate()
        
        # Wait for processes to terminate
        api_process.wait()
        streamlit_process.wait()
        
        print("Servers stopped successfully!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\nError: {e}")
        # Ensure processes are terminated in case of error
        try:
            api_process.terminate()
            streamlit_process.terminate()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()