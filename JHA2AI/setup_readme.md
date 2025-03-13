Instructions to Use the Setup Script

    Place the Script: Save the above code in a file called 

within your JHA2AI/ directory.

Run the Script: Execute the script using the following command in your terminal:

    python setup.py

Summary

The script will:

    Install necessary dependencies defined in 

.
Create a default

    file in the JHA2AI/backend directory if it does not already exist.
    Start your Flask application, binding it to 0.0.0.0 on port 3000 to make it accessible to users.

Modify the "YOUR_OPENROUTER_API_KEY" and "YOUR_HUGGINGFACE_API_KEY" placeholders in the script to use your actual API keys before running it.