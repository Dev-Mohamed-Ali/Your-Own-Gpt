import json
import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

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
    vectorizer = TfidfVectorizer()
    knowledge_base_vectors = vectorizer.fit_transform(questions)
    user_question_vector = vectorizer.transform([user_question])

    similarity_scores = cosine_similarity(user_question_vector, knowledge_base_vectors)
    best_match_idx = similarity_scores.argmax()

    return questions[best_match_idx] if similarity_scores[0, best_match_idx] > 0 else None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return "Bot: I don't know the answer. Can you teach me?"


@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    chat_history = session.get("chat_history", [])
    return render_template("index.html", chat_history=chat_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    # if session["username"]:
    #     return redirect(url_for("index"))
    if request.method == "POST":
        session["username"] = request.form["username"]
        append_message("Bot", "Hello, I'm the Chatbot! How can I help you?")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def append_message(who, message):
    if "chat_history" not in session:
        print("not found")
        session["chat_history"] = []

    session["chat_history"].append((who, message))
    session["chat_history"] = session["chat_history"]


def chatbot(user_input):
    knowledge_base = load_knowledge_base('knowledge_base.json')
    # Finds the best match using TF-IDF and cosine similarity, otherwise returns None
    best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])
    answer = get_answer_for_question(best_match, knowledge_base)
    return answer


@app.route("/get_response", methods=["POST"])
def get_chatbot_response():
    time.sleep(1)
    user_input = request.json["user_input"]
    append_message(session["username"], user_input)
    response = chatbot(user_input)
    print("response is %s" % response)
    if response == "Bot: I don't know the answer. Can you teach me?":
        append_message("Chatbot", "Bot: Alright, I understand. Feel free to ask anything else!")
    else:
        append_message("Chatbot", response)
    return jsonify(response)


@app.route("/update_knowledge_base", methods=["POST"])
def update_knowledge_base():
    user_input = request.json["user_input"]
    new_answer = request.json["new_answer"]

    # Update the knowledge base with the new answer (not implemented here)
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')
    knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
    save_knowledge_base('knowledge_base.json', knowledge_base)
    # For demonstration purposes, we will simply acknowledge that the bot has learned something new
    return jsonify("Bot: Thank you! I've learned something new.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
