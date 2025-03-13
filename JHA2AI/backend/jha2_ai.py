import os
import json
import logging
import subprocess
import requests
from typing import Any, Dict, List, Optional, Callable, Tuple
from pathlib import Path
from urllib.parse import urlparse

# Placeholder import for OpenRouterAPI, replace with the correct import for your setup
from backend.openrouter_api import OpenRouterAPI

class JHA2AI:
    """Autonomous AI assistant class."""

    def __init__(self,
                 config_file: str = "config.json",
                 callback: Optional[Callable] = None) -> None:
        try:
            # Set up logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)

            # Load configuration from the config.json file
            config_path = os.path.join(os.path.dirname(__file__), config_file)
            self.config = self.load_config(config_path)

            # Callback for user notifications
            self.callback = callback if callback else self.default_callback
            self.chat_history: List[Dict[str, Any]] = []
            self.tasks: List[str] = []  # List of autonomous tasks

            # Initialize OpenRouter API
            self.open_router_api = OpenRouterAPI()

            # Initialize state using config parameters
            self.state = {
                'model':
                self.config['default_model'],
                'persona':
                self.config.get('default_persona', 'autonomous assistant'),
                'available_personas':
                self.config.get('personas', {
                    "autonomous assistant":
                    "You are an advanced AI assistant."
                }),
                'last_code':
                None,
                'last_language':
                None,
                'history_types': [],
                'working_directory':
                self.config.get('working_directory', './jha2_workspace'),
                'allowed_commands':
                self.config.get('allowed_commands', [
                    'ls', 'pwd', 'cat', 'echo', 'mkdir', 'touch', 'rm', 'cp',
                    'mv', 'python', 'node', 'git', 'grep', 'find'
                ]),
                'functions': {},
                'dry_run_active':
                False,
                'preferences':
                self.load_preferences()
            }

            # Initialize workspace
            self._initialize_workspace()
            self.system_message = self.generate_system_message()
            self.commands = self.create_command_registry()

            # Load previous tasks if any
            self.load_tasks()

        except Exception as e:
            self.callback("error", f"Initialization error: {str(e)}")

    def _initialize_workspace(self) -> None:
        """Initialize and validate working directory."""
        try:
            work_dir = Path(self.state['working_directory'])
            work_dir.mkdir(parents=True, exist_ok=True)
            if not work_dir.is_dir():
                raise ValueError(
                    f"Working directory {work_dir} is not a valid directory")
        except Exception as e:
            self.callback("error", f"Failed to initialize workspace: {str(e)}")
            raise

    def process_input(self, user_input: str) -> None:
        """Process user input and generate a response."""
        try:
            if not user_input.strip():
                raise ValueError("Empty input")

            self.logger.info(f"User input: {user_input}")
            response = self.interpret_natural_language(user_input)
            if response:
                self.callback("message", response)
            else:
                raise ValueError("Failed to retrieve a valid response")

        except Exception as e:
            self.callback("error", f"Error processing input: {str(e)}")

    def interpret_natural_language(self, user_input: str) -> Optional[str]:
        """Interpret user input and decide on action."""
        if "run" in user_input:
            code_to_run = self.extract_code_from_input(user_input)
            return self.cmd_run(code_to_run)

        # Recognize other commands similarly
        if user_input.startswith("/"):
            command, *args = user_input.split()
            command_method = self.commands.get(command)
            if command_method:
                return command_method[0](args)

        return "Command not recognized."

    def extract_code_from_input(self, user_input: str) -> str:
        """Extract code or command from user input."""
        sections = user_input.split("run", 1)
        return sections[1].strip() if len(sections) > 1 else ""

    def default_callback(self, update_type: str, data: Any) -> None:
        """Default callback for local execution."""
        if update_type == "error":
            self.logger.error(data)
        elif update_type == "warning":
            self.logger.warning(data)
        else:
            self.logger.info(f"JHA: {data}")

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not os.path.exists(config_file):
            return self.create_default_config(config_file)
        with open(config_file, "r") as f:
            return json.load(f)

    def create_default_config(self, config_file: str) -> Dict[str, Any]:
        """Creates a default config file."""
        default_config = {
            "api_key":
            "YOUR_OPENROUTER_API_KEY",  # Placeholder API key
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
                'ls', 'pwd', 'cat', 'echo', 'mkdir', 'touch', 'rm', 'cp', 'mv',
                'python', 'node', 'git', 'grep', 'find'
            ]
        }
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=4)
        self.logger.info(
            "Default config.json created. Please edit it with your API keys.")
        exit(1)

    def load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from a file."""
        preferences_path = os.path.join(os.path.dirname(__file__),
                                        "preferences.json")
        if not os.path.exists(preferences_path):
            return self.create_default_preferences()
        with open(preferences_path, "r") as f:
            return json.load(f)

    def create_default_preferences(self) -> Dict[str, Any]:
        """Creates a default preferences file."""
        default_preferences = {
            "preferred_language": "python",
            "confirm_destructive": True
        }
        preferences_path = os.path.join(os.path.dirname(__file__),
                                        "preferences.json")
        with open(preferences_path, "w") as f:
            json.dump(default_preferences, f, indent=4)
        return default_preferences

    def generate_system_message(self) -> str:
        """Generate the system prompt based on current preferences and functions."""
        preferences_message = self.generate_preferences_message()
        function_descriptions = self.generate_function_descriptions()

        system_prompt = self.state['available_personas'].get(
            self.state['persona'], "You are an advanced AI assistant.")
        return (
            f"{system_prompt}\n{preferences_message}\n\n"
            f"You have access to the following functions:\n{function_descriptions}\n\n"
            "Examples:\n"
            "create_file(\"new_file.txt\", \"Hello\") >> read_file(\"new_file.txt\")\n"
            "/ls -l\n"
            "if [ -f data.txt ]; then read_file(\"data.txt\"); else create_file(\"data.txt\", \"Initial content\"); fi"
        )

    def generate_preferences_message(self) -> str:
        """Creates a message about current user preferences."""
        return (
            f"Current User Preferences:\n"
            f"- Preferred Language: {self.state['preferences'].get('preferred_language', 'python')}\n"
            f"- Confirm Destructive Actions: {self.state['preferences'].get('confirm_destructive', True)}"
        )

    def generate_function_descriptions(self) -> str:
        """Generates a description of registered functions."""
        return "\n".join([
            f"- {name}: {func.__doc__ or 'No description.'}"
            for name, func in self.state['functions'].items()
        ])

    def create_command_registry(self) -> Dict[str, Tuple[Callable, str]]:
        """Create a mapping of commands to their handler functions and descriptions."""
        return {
            "/help": (self.cmd_help, "Display this help message."),
            "/reset": (self.cmd_reset, "Clear the conversation history."),
            "/model": (self.cmd_model,
                       "Set the LLM model. Usage: /model <model_name>"),
            "/persona": (self.cmd_persona,
                         "Set the persona. Usage: /persona <persona_name>"),
            "/quit": (self.cmd_quit, "Exit the application."),
            "/edit": (self.cmd_edit, "Edit the last generated code."),
            "/run": (self.cmd_run, "Run code. Usage: /run [<code>]"),
            "/show":
            (self.cmd_show,
             "Prints the content of a file. Usage: /show <file_name>"),
            "/webget":
            (self.cmd_webget,
             "Gets the content of a webpage using HTTP GET. Usage: /webget <url>"
             ),
            "/webrequest":
            (self.cmd_webrequest,
             "Makes various web requests. Usage: /webrequest <method> <url> [data]"
             ),
            "/describe_image":
            (self.cmd_describe_image,
             "Describes an image from a URL. Usage: /describe_image <url>"),
            "/preferences":
            (self.cmd_preferences,
             "View or modify preferences. Usage: /preferences [key value]"),
            "/list":
            (self.cmd_list,
             "Lists available commands or personas. Usage: /list [commands|personas]"
             )
        }

    def cmd_help(self, args=None) -> None:
        """Display available commands."""
        help_text = "Available Commands:\n" + "\n".join(
            f"  {cmd}: {desc}" for cmd, (_, desc) in self.commands.items())
        self.callback("message", help_text)

    def cmd_reset(self, args=None) -> None:
        """Clear the conversation history."""
        self.chat_history = []
        self.state['history_types'] = []
        self.state['last_code'] = None
        self.state['last_language'] = None
        self.callback("message", "Chat history cleared.")

    def cmd_model(self, args) -> None:
        """Set the LLM model."""
        if args:
            self.state['model'] = args.strip()
            self.callback("message", f"Model set to {self.state['model']}.")
        else:
            self.callback("message", "Usage: /model <model_name>")

    def cmd_persona(self, args) -> None:
        """Set the persona."""
        if args:
            if args in self.state["available_personas"]:
                self.state['persona'] = args
            else:
                self.state['available_personas'][args] = args
                self.state['persona'] = args

            self.system_message = self.generate_system_message()
            self.callback("message",
                          f"Persona set to {self.state['persona']}.")
        else:
            self.callback("message", "Usage: /persona <persona_name>")

    def cmd_quit(self, args=None) -> None:
        """Exit the application."""
        self.callback("message", "Exiting...")
        exit(0)

    def cmd_edit(self, args=None) -> None:
        """Edit the last generated code."""
        if not self.state['last_code']:
            self.callback("message", "No code to edit.")
            return

        file_extension = {
            "python": ".py",
            "javascript": ".js",
            "bash": ".sh",
            "sql": ".sql",
        }.get(self.state['last_language'], ".txt")

        temp_file_path = f"temp_code{file_extension}"

        try:
            with open(temp_file_path, "w") as f:
                f.write(self.state['last_code'])

            self.open_file_in_editor(temp_file_path)
            self.callback("message",
                          "Press Enter in the terminal after editing...")
            input("Press Enter after editing...")

            with open(temp_file_path, "r") as f:
                self.state['last_code'] = f.read()
            os.remove(temp_file_path)  # Clean up temporary file

            self.callback("message",
                          "Code updated. You can now run it with /run.")

        except IOError as e:
            self.callback("error", f"Error while editing code: {str(e)}")

    def open_file_in_editor(self, file_path: str) -> None:
        """Open file in the system's default editor."""
        if os.name == 'nt':
            os.startfile(file_path)
        elif os.name == 'posix':
            editor = os.environ.get('EDITOR', 'vim')
            subprocess.call([editor, file_path])

    def cmd_run(self, args: Optional[str] = None) -> str:
        """Execute the provided code."""
        if args:
            code = args
            language = self.detect_language(code)
        elif self.state['last_code']:
            code = self.state['last_code']
            language = self.state['last_language']
        else:
            return "No code to run."

        if not language:
            return "Language not detected. Please specify."

        try:
            command = self.get_command(language, code)
            result = self.execute_command(command)
            self.callback("command_output", result)
            self.state['last_code'] = code
            self.state['last_language'] = language

            return result
        except Exception as e:
            return f"Error during code execution: {str(e)}"

    def detect_language(self, code: str) -> str:
        """Detect the programming language from code."""
        # This detection logic can be enhanced based on specific needs
        if code.strip().startswith("print") or "def" in code:
            return "python"
        elif code.strip().startswith("console.log"):
            return "javascript"
        return "unknown"

    def get_command(self, language: str, code: str) -> List[str]:
        """Return the appropriate command for the given code language."""
        if language == "python":
            return ["python", "-c", code]
        elif language == "javascript":
            return ["node", "-e", code]
        elif language == "bash":
            return ["bash", "-c", code]
        elif language == "sql":
            return ["echo", code]  # A stub for SQL command
        else:
            raise ValueError(f"Unsupported language '{language}'.")

    def execute_command(self, command: List[str]) -> str:
        """Execute a command and return its output."""
        try:
            process = subprocess.run(command,
                                     capture_output=True,
                                     text=True,
                                     timeout=25,
                                     cwd=self.state['working_directory'])
            combined_output = process.stdout + (process.stderr or "")

            if process.returncode != 0:
                raise RuntimeError(
                    f"Command failed with return code {process.returncode}")

            return combined_output.strip() or "No output generated."
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out (25 seconds)."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def cmd_show(self, file_path: str) -> None:
        """Show contents of a file."""
        if not file_path:
            self.callback("message", "Usage: /show <file_name>")
            return

        safe_path = secure_path(file_path, self)
        if not safe_path:
            return

        if not os.path.exists(safe_path):
            self.callback("message", f"Error: File '{file_path}' not found.")
            return

        try:
            with open(safe_path, 'r') as f:
                content = f.read()
            self.callback(
                "message",
                f"---- Content of {file_path} ----\n{content}\n---- End Content ----"
            )
        except Exception as e:
            self.callback("error", f"Error reading file: {str(e)}")

    def cmd_webget(self, url: str) -> None:
        """Fetch content from a web page."""
        if not url:
            self.callback("message", "Usage: /webget <url>")
            return

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            self.callback(
                "message",
                f"---- HTML Content of {url} ----\n{response.text[:1000]}\n---- End Content ----"  # Limited for readability
            )
        except requests.exceptions.RequestException as e:
            self.callback("error", f"Error fetching URL: {e}")

    def cmd_webrequest(self, args) -> None:
        """Make HTTP requests."""
        if not args:
            self.callback("message",
                          "Usage: /webrequest <method> <url> [data]")
            return

        parts = args.split(" ", 2)
        if len(parts) < 2:
            self.callback("message",
                          "Usage: /webrequest <method> <url> [data]")
            return

        method = parts[0].upper()
        url = parts[1]
        data = json.loads(parts[2]) if len(parts) > 2 else None

        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            self.callback(
                "message",
                "Error: Invalid HTTP method. Must be GET, POST, PUT, DELETE, or PATCH."
            )
            return

        try:
            response = requests.request(method, url, json=data, timeout=30)
            response.raise_for_status()
            self.callback(
                "message",
                response.json() if 'application/json' in response.headers.get(
                    'Content-Type', '') else response.text)
        except requests.exceptions.RequestException as e:
            self.callback("error", f"Error during web request: {e}")

    def cmd_describe_image(self, url: str) -> None:
        """Describe an image using an external API."""
        if not self.config.get("huggingface_api_key"):
            self.callback(
                "error",
                "Hugging Face API key is not configured. Image description unavailable."
            )
            return

        if not url or not self.validate_url(url):
            self.callback("error", "Error: Invalid URL format for image.")
            return

        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/your_model_name",
                headers={
                    "Authorization":
                    f"Bearer {self.config['huggingface_api_key']}"
                },
                json={"inputs": url},
                timeout=30)
            response.raise_for_status()
            result = response.json()
            caption = result[0].get(
                'generated_text',
                "Could not generate a description for the image.")
            self.callback("message", f"Image Description: {caption}")
        except requests.exceptions.RequestException as e:
            self.callback("error", f"Error describing image: {e}")

    def validate_url(self, url: str) -> bool:
        """Validate the given URL."""
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def cmd_preferences(self, args: Optional[List[str]] = None) -> None:
        """View or modify preferences."""
        if not args:
            current_preferences = json.dumps(self.state['preferences'],
                                             indent=2)
            self.callback("message",
                          f"Current Preferences:\n{current_preferences}")
            return

        # Example to set new preferences
        if len(args) == 2:
            key, value = args[0], args[1]
            self.state['preferences'][key] = value
            self.save_preferences()
            self.callback("message", f"Preference '{key}' set to '{value}'.")
        else:
            self.callback("message", "Usage: /preferences <key> <value>")

    def save_preferences(self):
        """Save preferences to file."""
        preferences_path = os.path.join(os.path.dirname(__file__),
                                        "preferences.json")
        with open(preferences_path, "w") as f:
            json.dump(self.state['preferences'], f, indent=4)

    def load_tasks(self) -> None:
        """Load previously stored tasks."""
        task_path = os.path.join(self.state['working_directory'], 'tasks.json')
        if os.path.exists(task_path):
            with open(task_path, 'r') as f:
                self.tasks = json.load(f)

    def save_tasks(self) -> None:
        """Save current tasks to a file."""
        task_path = os.path.join(self.state['working_directory'], 'tasks.json')
        with open(task_path, 'w') as f:
            json.dump(self.tasks, f, indent=4)

    def autonomously_execute_tasks(self) -> None:
        """Execute tasks autonomously based on some condition."""
        for task in self.tasks:
            # Here you can decide how to run tasks (for example based on time, conditions or other logic)
            pass  # Add logic to run each task

    def cmd_list(self, args: List[str]) -> None:
        """Lists available commands or personas."""
        if not args:
            self.callback("message", "Usage: /list [commands|personas]")
            return

        category = args[0]
        if category == "commands":
            self.callback("message", "\n".join(self.commands.keys()))
        elif category == "personas":
            self.callback("message",
                          "\n".join(self.state['available_personas'].keys()))
        else:
            self.callback("message",
                          "Invalid category. Use 'commands' or 'personas'.")


# This is where you would typically instantiate the JHA2AI class and start using it.
if __name__ == "__main__":
    ai = JHA2AI()
    # For the purpose of demonstration
    while True:
        user_input = input("You: ")
        ai.process_input(user_input)
