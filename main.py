from flask import Flask,request,json,g
from tlapbot.db import get_db
import requests

app = Flask(__name__)

@app.route('/owncastWebhook',methods=['POST'])
def owncastWebhook():
    data = request.json
    db = get_db()
    if data["type"] == "CHAT":
        print("New chat message:")
        print(f'from {data["eventData"]["user"]["displayName"]}:')
        print(f'{data["eventData"]["body"]}')

    elif data["type"] == "USER_JOINED":
        user_id = data["eventData"]["user"]["id"]
        try:
            cursor = db.execute(
                "SELECT username FROM points WHERE id = ?",
                (user_id)
            )
            if cursor.fetchone() == None:
                username = data["eventData"]["user"]["displayName"]
                cursor.execute(
                    "INSERT INTO points(id, username, points) VALUES(?, ?, 0)",
                    (user_id, username)
                )
            db.commit()
    
    elif data["type"] == "NAME_CHANGED":
        user_id = data["eventData"]["user"]["id"]
        new_username = data["eventData"]["user"]["newName"]
        try:
            db.execute(
                "UPDATE points SET username = ? WHERE id = ?",
                (new_username, user_id),
            )
            db.commit()
        except db.IntegrityError:
            print("Integrity Error.")
            print(f"User ID {user_id} probably does not exist.")
    
    return data

if __name__ == '__main__':
    app.run(debug=True)