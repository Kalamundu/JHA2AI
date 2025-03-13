import os
import json
import subprocess


def install_requirements():
    """Install required packages from requirements.txt."""
    try:
        subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing requirements: {e}")


def create_config():
    """Create a default config.json file if it doesn't exist."""
    config_path = os.path.join('backend', 'config.json')

    if not os.path.exists(config_path):
        config = {
            "api_key":
            "YOUR_OPENROUTER_API_KEY",
            "huggingface_api_key":
            "YOUR_HUGGINGFACE_API_KEY",
            "default_model":
            "mistralai/mistral-7b-instruct",
            "default_persona":
            "autonomous assistant",
            "personas": {
                "autonomous assistant": "You are an advanced AI assistant."
            },
            "working_directory":
            "./jha2_workspace",
            "allowed_commands": [
                "ls", "pwd", "cat", "echo", "mkdir", "touch", "rm", "cp", "mv",
                "python", "node", "git", "grep", "find"
            ]
        }

        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        print("Config file created at:", config_path)
    else:
        print("Config file already exists.")


def run_application():
    """Run the Flask application."""
    try:
        subprocess.Popen(
            ['python', '-m', 'flask', 'run', '--host=0.0.0.0', '--port=3000'])
        print("Application is running on http://0.0.0.0:3000/")
    except Exception as e:
        print(f"An error occurred while starting the application: {e}")


if __name__ == "__main__":
    install_requirements()
    create_config()
    run_application()
