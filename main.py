from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from dotenv import load_dotenv
import os

load_dotenv()
secret_key = os.getenv("SITE_SECRET_KEY")

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key
socketio = SocketIO(app)

rooms = {}


def generate_room_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break

    return code


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template(
                "index.html", error="Please enter a name.", code=code, name=name
            )

        if join != False and not code:
            return render_template("index.html", error="Please enter a room code.")

        room = code
        if create != False:
            room = generate_room_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("index.html", error="Room does not exist")

        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))

    return render_template("index.html")


@app.route("/room")
def room():
    room = session.get("room")

    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", title=f"The {room} Room")


if __name__ == "__main__":
    socketio.run(app, debug=True)
