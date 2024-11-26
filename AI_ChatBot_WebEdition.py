from flask import Flask, render_template, request, session
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Secret key for managing sessions
app.secret_key = "your_secret_key"  # Replace with a secure random string in production

@app.route('/')
def index():
    # Initialize session for storing chat history
    if "messages" not in session:
        session["messages"] = []
    return render_template('index.html', messages=session["messages"])

@app.route('/chat', methods=['POST'])
def chat():
    role = request.form.get("role")  # Chatbot role
    user_message = request.form.get("prompt")  # User's input message

    try:
        # Retrieve the conversation history from the session
        messages = session.get("messages", [])

        # Add user input to the conversation
        messages.append({"role": "user", "content": user_message})

        # Send conversation history to OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Replace with "gpt-4" or another model
            messages=[
                {"role": "system", "content": f"You are a {role}."},
                *messages
            ]
        )

        # Get chatbot's response
        chatbot_message = response.choices[0].message.content

        # Add chatbot's response to the conversation
        messages.append({"role": "assistant", "content": chatbot_message})

        # Save updated messages back to the session
        session["messages"] = messages

    except Exception as e:
        # Handle errors gracefully
        chatbot_message = f"An error occurred: {str(e)}"
        session["messages"].append({"role": "assistant", "content": chatbot_message})

    # Render the updated conversation
    return render_template('index.html', messages=session["messages"])

@app.route('/reset', methods=['POST'])
def reset():
    """Clear the conversation history."""
    session.pop("messages", None)
    return render_template('index.html', messages=[])

if __name__ == "__main__":
    app.run(debug=True)