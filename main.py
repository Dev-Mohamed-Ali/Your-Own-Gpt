import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from sentence_transformers import util, SentenceTransformer
import faiss
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secure secret key for production use

# Load the SentenceTransformer model (for embeddings) - Load it only once
model = SentenceTransformer('paraphrase-distilroberta-base-v1')


# Load the knowledge base from a JSON file - Load it only once
def load_knowledge_base(file_path: str):
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data


# Save the updated knowledge base to the JSON file
def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


# Create an index and store the embeddings of knowledge base questions
def create_knowledge_base_index(knowledge_base: dict, model):
    knowledge_base_questions = [q["question"] for q in knowledge_base["questions"]]
    embeddings_all_questions = model.encode(knowledge_base_questions, convert_to_tensor=False)

    # Convert the list of NumPy arrays into a single NumPy array
    embeddings_all_questions = np.vstack(embeddings_all_questions)

    index = faiss.IndexFlatIP(model.get_sentence_embedding_dimension())
    index.add(embeddings_all_questions)
    return index


# Find the closest matching question using sentence embeddings and cosine similarity
def find_best_match(user_question: str, index, model, knowledge_base: dict) -> str | None:
    user_embedding = model.encode(user_question, convert_to_tensor=False).reshape(1, -1)
    _, best_match_indices = index.search(user_embedding, 1)

    best_match_idx = best_match_indices[0][0]
    best_match_score = util.pytorch_cos_sim(user_embedding, [
        model.encode(knowledge_base["questions"][best_match_idx]["question"], convert_to_tensor=False)])
    if best_match_score > 0.5:
        return knowledge_base["questions"][best_match_idx]["question"]
    else:
        return None


def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    chat_history = session.get("chat_history", [])
    return render_template("index.html", chat_history=chat_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
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
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')
    index = create_knowledge_base_index(knowledge_base, model)

    # Use multithreading to parallelize sentence embedding and similarity calculation
    with ThreadPoolExecutor() as executor:
        future = executor.submit(find_best_match, user_input, index, model, knowledge_base)
        best_match = future.result()

    if best_match:
        # If there is a best match, return the answer from the knowledge base
        answer: str = get_answer_for_question(best_match, knowledge_base)
        return answer  # Return the answer as it is, without "Bot: " prefix
    else:
        return "Bot: I don't know the answer. Can you teach me?"


@app.route("/get_response", methods=["POST"])
def get_chatbot_response():
    user_input = request.json["user_input"]
    append_message(session["username"], user_input)
    response = chatbot(user_input)
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
    index = create_knowledge_base_index(knowledge_base, model)
    knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
    index.add(model.encode(user_input, convert_to_tensor=False).reshape(1, -1))
    save_knowledge_base('knowledge_base.json', knowledge_base)
    # For demonstration purposes, we will simply acknowledge that the bot has learned something new
    return jsonify("Bot: Thank you! I've learned something new.")


if __name__ == "__main__":
    app.run(debug=True)
