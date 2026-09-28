# FriendlyChatBoT 🤖

A friendly AI chatbot built using Flask and the Groq API.

## ✨ Features

- Conversational AI chatbot
- Flask-based backend
- Groq API integration
- SQLite database for storing chat messages
- Responsive web interface
- HTML, CSS, and JavaScript frontend

## 🛠️ Technologies Used

- Python
- Flask
- Groq API
- SQLite
- HTML
- CSS
- JavaScript

## 📁 Project Structure

```text
FriendlyChatBoT/
│
├── Static/
│   ├── CSS/
│   │   └── style.css
│   └── JS/
│       └── chat.js
│
├── Templates/
│   └── index.html
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Renu0222/FriendlyChatBoT.git
cd FriendlyChatBoT
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 4. Install the required packages

```bash
pip install -r requirements.txt
```

## 🔑 API Key Setup

Create a `.env` file in the project folder and add your Groq API key:

```text
GROQ_API_KEY=your_api_key_here
```

**Never upload your `.env` file or expose your API key publicly.**

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

Then open your browser and go to:

```text
http://127.0.0.1:5000
```

## 📌 Note

This project was created as a learning project to explore Flask, APIs, databases, and AI chatbot development.