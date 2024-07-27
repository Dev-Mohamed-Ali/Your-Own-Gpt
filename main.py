from flask import Flask, render_template, request, session, jsonify
import json
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secure secret key for production use


# Load the knowledge base from a JSON file
def load_knowledge_base(file_path: str):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


# Save the updated knowledge base to the JSON file
def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


# Create an index and store the embeddings of knowledge base questions
def find_best_match(user_question: str, questions: list[str]) -> str | None:
    # Preprocessing and Tokenization
    # You might want to use more advanced text preprocessing techniques here
    user_question = user_question.lower()

    vectorizer = TfidfVectorizer()
    knowledge_base_vectors = vectorizer.fit_transform(questions)
    user_question_vector = vectorizer.transform([user_question])

    similarity_scores = cosine_similarity(user_question_vector, knowledge_base_vectors)
    best_match_idx = similarity_scores.argmax()

    # Choose a similarity threshold slightly above 0. Adjust as needed.
    similarity_threshold = 0.65

    if similarity_scores[0, best_match_idx] > similarity_threshold:
        return questions[best_match_idx]
    else:
        return None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return "Bot: I don't know the answer. Can you teach me?"


def append_message(who, message):
    # Initialize an empty list if chat_history is not already in session
    chat_history = session.get("chat_history", [])

    # Append the new message to the chat history
    chat_history.append({"who": who, "message": message})

    # Update the chat_history in the session
    session["chat_history"] = chat_history


def chatbot(user_input):
    knowledge_base = load_knowledge_base('new_data.json')
    # Finds the best match using TF-IDF and cosine similarity, otherwise returns None
    best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])
    answer = get_answer_for_question(best_match, knowledge_base)
    return answer


@app.route("/get_response")
def get_chatbot_response():
    time.sleep(1)
    user_input = request.args.get("user_input")
    response = chatbot(user_input)
    if response == "Bot: I don't know the answer. Can you teach me?":
        response = "no answer"
    else:
        append_message(session["username"], user_input)
        append_message("Chatbot", response)
    return json.dumps([f"Bot:{response}"])


@app.route("/set_username")
def set_username():
    time.sleep(1)
    user_input = request.args.get("username")
    if user_input:
        session["username"] = user_input
    else:
        session["username"] = "user"
    return json.dumps(["success"])


@app.route("/get_username")
def get_username():
    user_name = session.get("username")
    if user_name:
        return json.dumps({"current_username": user_name})
    else:
        return json.dumps({"current_username": ""})


@app.route("/get_chat_history")
def get_chat_history():
    chat_history = session.get("chat_history", [])
    return jsonify(chat_history)


@app.route("/clear_chat_history", methods=["POST"])
def clear_chat_history():
    session.pop("chat_history", None)
    return jsonify({"status": "success"})


@app.route("/teach_bot", methods=["POST"])
def update_knowledge_base():
    try:
        # Extract data from the request JSON
        user_input = request.json["user_input"]
        new_answer = request.json["answer"]

        # Load the knowledge base
        knowledge_base = load_knowledge_base('knowledge_base.json')

        # Update the knowledge base with the new answer
        knowledge_base["questions"].append({"question": user_input, "answer": new_answer})

        # Save the updated knowledge base
        save_knowledge_base('knowledge_base.json', knowledge_base)

        # append messages
        append_message(session["username"], user_input)
        append_message("Chatbot", new_answer)

        # Return a success message
        return jsonify({"message": "Bot: Thank you! I've learned something new."}), 200
    except Exception as e:
        # Return an error message if there's an exception
        return jsonify({"error": str(e)}), 400


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
