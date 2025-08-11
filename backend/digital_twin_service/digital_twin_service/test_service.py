from src.main import app
import threading
import time
import requests
import json

def test_service():
    print("Starting Digital Twin Service test...")
    
    # Start server in background
    def run_server():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Test health endpoint
    try:
        print("Testing health endpoint...")
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        print(f'Health check status: {response.status_code}')
        print(f'Health check response: {response.text}')
        
        if response.status_code == 200:
            print("✅ Digital Twin Service is working correctly!")
        else:
            print("❌ Service returned non-200 status")
            
    except requests.exceptions.RequestException as e:
        print(f'❌ Connection error: {e}')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')

if __name__ == "__main__":
    test_service()
