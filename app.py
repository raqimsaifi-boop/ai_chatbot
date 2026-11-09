
from flask import Flask, render_template, request, jsonify
from chatbot import run_chatbot

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        question = data.get("message", "").strip()

        if not question:
            return jsonify({
                "error": "Please enter a question."
            }), 400

        # Call your existing RAG chatbot
        answer = run_chatbot(question)

        return jsonify({
            "answer": answer
        })

    except Exception as error:
        print("Chat error:", error)

        return jsonify({
            "error": "Something went wrong. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
