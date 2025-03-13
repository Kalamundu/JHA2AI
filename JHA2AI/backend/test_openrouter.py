import logging
from openrouter_api import OpenRouterAPI

def test_openrouter_api():
    # Initialize the OpenRouterAPI
    try:
        open_router_api = OpenRouterAPI()

        # Sample user input to send to the API
        user_input = "What is the capital of France?"

        # Send the message to the API and receive the response
        response = open_router_api.send_message(user_input)

        # Log the response received from the API
        logging.info(f"Response from OpenRouter API: {response}")

    except Exception as e:
        logging.error(f"An error occurred while testing OpenRouterAPI: {e}")

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Run the test
    test_openrouter_api()