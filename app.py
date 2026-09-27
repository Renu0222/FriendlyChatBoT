import os
import sqlite3

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq


# -----------------------------
# Environment
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
DATABASE = os.path.join(BASE_DIR, "chatbot.db")

load_dotenv(ENV_FILE)

print("ENV file:", ENV_FILE)
print("API key found:", bool(os.getenv("GROQ_API_KEY")))


# -----------------------------
# Flask
# -----------------------------

app = Flask(__name__)


# -----------------------------
# Groq
# -----------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------
# Database
# -----------------------------

def get_db():

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    return connection


def init_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


init_database()


# -----------------------------
# Load recent conversation
# -----------------------------

def load_memory():

    connection = get_db()

    rows = connection.execute("""
        SELECT role, content
        FROM messages
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    connection.close()

    rows = list(reversed(rows))

    return [
        {
            "role": row["role"],
            "content": row["content"]
        }
        for row in rows
    ]


# -----------------------------
# Save message
# -----------------------------

def save_message(role, content):

    connection = get_db()

    connection.execute(
        """
        INSERT INTO messages (role, content)
        VALUES (?, ?)
        """,
        (role, content)
    )

    connection.commit()
    connection.close()


# -----------------------------
# Buddy personality
# -----------------------------

SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are a friendly AI companion named Buddy.

Your personality:
- Warm, playful, natural, and conversational.
- Talk like a real friendly person.
- Be supportive without being overly formal.
- Use emojis naturally, but do not overuse them.
- Match the user's mood and message length.
- Keep casual replies short and natural.
- Do not repeatedly ask "How can I help?"
- If the user says "let's play", start a game naturally.
- Remember information the user tells you.

Formatting:
- Do not use Markdown.
- Do not use asterisks for bold or italic text.
- Do not use hashtags for headings.
- Do not use horizontal lines.
- Avoid unnecessary bullet points.
- Use normal sentences and natural paragraphs.

Coding:
- When the user asks for a small or simple code example, give a small code example.
- Do not create a full interactive program unless the user specifically asks for one.
- Do not add input(), try/except, or __main__ unless the user asks for a complete program.
- Keep coding explanations brief.

Web search:
- When web search is used, answer using the information found on the web.
- Prefer reliable and authoritative sources.
- Understand reasonable spelling mistakes, missing letters, extra letters,
  swapped letters, and small variations in names.
- When the user gives a person's name or topic with a possible spelling mistake,
  infer the most likely intended name from the available context.
- If the first search does not find useful information, try a reasonable
  spelling variation or corrected version.
- For example, "Harekal Hajabba", "Harekala Hajabba", and
  "Harekala Hajjabba" may refer to the same person.
- Do not criticize the user's spelling.
- If you are confident about the intended name, use the correct spelling
  naturally in your answer.
- If you are not confident, explain that there may be multiple possible matches.
- Never invent information just because a name looks similar.
"""
}


# -----------------------------
# Detect web-search questions
# -----------------------------

def needs_web_search(message):

    message_lower = message.lower().strip()

    web_phrases = [
        "latest",
        "today",
        "current",
        "recent",
        "news",
        "this week",
        "this month",
        "yesterday",
        "who is ",
        "who was ",
        "what happened",
        "what's happening",
        "whats happening",
        "current price",
        "price today",
        "recent update",
        "latest update",
        "search the web",
        "search online",
        "look it up",
        "look this up"
    ]

    # Questions that clearly need web search
    if any(
        phrase in message_lower
        for phrase in web_phrases
    ):
        return True

    # Allow short names/topics to trigger web search.
    # Example:
    # "Harekal Hajabba"
    # "Salumarada Thimmakka"
    words = message.split()

    if 2 <= len(words) <= 4:

        # Check whether the original message contains
        # capitalized words, which may indicate a name/topic.
        if any(word[:1].isupper() for word in words):
            return True

    return False
# -----------------------------
# Normal AI response
# -----------------------------

def normal_ai_response(messages):

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=messages,

        temperature=0,

        max_tokens=500
    )

    return response.choices[0].message.content


# -----------------------------
# Web AI response
# -----------------------------

def web_ai_response(messages):

    response = client.chat.completions.create(

        model="groq/compound",

        messages=messages,

        temperature=0,

        max_tokens=500,

        tool_choice="auto"
    )

    return response.choices[0].message.content


# -----------------------------
# Home
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# Chat
# -----------------------------

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:

        return jsonify({
            "reply": "I didn't receive a message 😊"
        }), 400


    user_message = data.get("message", "").strip()


    if not user_message:

        return jsonify({
            "reply": "Please type a message 😊"
        })


    # Save user's message
    save_message("user", user_message)


    # Load recent conversation
    conversation_history = load_memory()


    # Build messages
    messages = [
        SYSTEM_MESSAGE
    ] + conversation_history


    try:

        # -----------------------------
        # Choose AI mode
        # -----------------------------

        if needs_web_search(user_message):

            print("WEB SEARCH: enabled 🌐")

            reply = web_ai_response(messages)

        else:

            print("WEB SEARCH: not needed ⚡")

            reply = normal_ai_response(messages)


        # Safety fallback
        if not reply:

            reply = "I'm not sure what to say right now 😅"


        # Save AI response
        save_message("assistant", reply)


        return jsonify({
            "reply": reply
        })


    except Exception as e:

        print("GROQ ERROR:", repr(e))

        return jsonify({
            "reply": "Sorry, something went wrong. Please try again. 😕"
        }), 500


# -----------------------------
# Start server
# -----------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )