import os
import subprocess
import logging
import time

def test_run_py():
    # Start the application server in a subprocess
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Starting the Flask application server...")

        # Run run.py
        process = subprocess.Popen(['python', 'JHA2AI/run.py'])
        time.sleep(5)  # Give the server some time to start

        # Assuming the server starts successfully, you can now proceed with further tests
        logging.info("Application server started successfully. Testing if it's reachable...")

        # You could perform an HTTP request check here (for example using requests library)
        # This part will require the requests library to be installed: pip install requests

        import requests

        response = requests.get('http://0.0.0.0:3000')  # Check if server is reachable
        if response.status_code == 200:
            logging.info("Server is reachable, response status: 200 OK")
        else:
            logging.error(f"Server is not reachable, response status: {response.status_code}")

        # Stop the server
        process.terminate()
        process.wait()

    except Exception as e:
        logging.error(f"An error occurred during testing: {e}")
        if process:
            process.terminate()

if __name__ == '__main__':
    test_run_py()