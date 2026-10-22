import os
import html
import logging
import requests

from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8192

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID", "8902663892")


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(".", "style.css")


@app.route("/script.js")
def js():
    return send_from_directory(".", "script.js")


@app.route("/api/apply", methods=["POST"])
def apply():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Неверный формат"), 400

    fields = {
        "fullname": 100,
        "age": 3,
        "experience": 2000,
        "portfolio": 500,
        "languages": 500
    }

    for field, limit in fields.items():
        value = data.get(field)

        if not isinstance(value, str):
            return jsonify(error="Заполните все поля"), 400

        value = value.strip()

        if not value or len(value) > limit:
            return jsonify(error="Некорректные данные"), 400

        data[field] = value

    try:
        age = int(data["age"])
        if not 1 <= age <= 120:
            raise ValueError
    except ValueError:
        return jsonify(error="Некорректный возраст"), 400

    if not data["portfolio"].startswith(("https://", "http://")):
        return jsonify(error="Некорректная ссылка"), 400

    def esc(value):
        return html.escape(value)

    text = f'''
📩 <b>НОВАЯ ЗАЯВКА НА РАБОТУ!</b>

👤 <b>Имя и фамилия:</b>
{esc(data["fullname"])}

🎂 <b>Возраст:</b>
{esc(data["age"])}

💼 <b>Опыт:</b>
{esc(data["experience"])}

📁 <b>Портфолио:</b>
{esc(data["portfolio"])}

💻 <b>Языки:</b>
{esc(data["languages"])}

━━━━━━━━━━━━━━━━
✅ Заявка отправлена с сайта.
'''

    if not BOT_TOKEN:
        return jsonify(error="Бот не настроен"), 500

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_ID,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=15
        )
        response.raise_for_status()

        if not response.json().get("ok"):
            raise RuntimeError("Telegram API error")

        return jsonify(success=True)

    except (requests.RequestException, ValueError, RuntimeError):
        logging.exception("Ошибка Telegram")
        return jsonify(error="Ошибка отправки"), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
