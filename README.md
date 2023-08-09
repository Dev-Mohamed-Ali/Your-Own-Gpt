# Chatbot with Knowledge Base

This repository contains a simple Flask-based chatbot that interacts with users and answers questions using a predefined knowledge base. The chatbot utilizes TF-IDF vectorization and cosine similarity to find the best-matching question in the knowledge base and provides relevant answers.

## Features

- User authentication and session management.
- Knowledge base stored in a JSON file.
- Updating the knowledge base with new questions and answers.
- Ability to teach the chatbot new answers.
- Clearing the chat history for a fresh conversation.
- Web interface for user interaction.


## Setup and Usage

1. Clone the repository:

```
git clone https://github.com/sd950216/Your-Own-Gpt.git
cd Your-Own-Gpt
```
## Install the necessary dependencies

1- Installing Flask:
```
pip install Flask
```

2- Installing scikit-learn:
```
pip install scikit-learn
```

3- Installing NLTK (Natural Language Toolkit):
```
pip install nltk
```

## Configure the secret key in the app.secret_key variable in the app.py file:

```
app.secret_key = "your_secret_key"  # Set a secure secret key for production use
```

## Prepare your knowledge base:
Create a JSON file named knowledge_base.json with the following structure:
```
{
    "questions": [
        {
            "question": "What is the capital of France?",
            "answer": "The capital of France is Paris."
        },
        ...
    ]
}
```
## Improve Accuracy:

To enhance the accuracy of the answer matching process, you can adjust the similarity threshold in the code. The similarity threshold determines how closely a user's question should match a question in the knowledge base for it to be considered a match.

```
# Choose a similarity threshold above 0. Adjust as needed.
similarity_threshold = 0.7
```
## Run the Chatbot:

```
python app.py
```

Open your web browser and navigate to http://localhost:5000 to access the chatbot interface.

Log in with a username, and start interacting with the chatbot.

## Contributions
Contributions are welcome! If you have suggestions, enhancements, or bug fixes, please feel free to submit a pull request.
