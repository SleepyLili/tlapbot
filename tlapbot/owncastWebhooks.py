from flask import Flask,request,json,Blueprint
from sqlite3 import Error
from tlapbot.db import get_db
from tlapbot.owncastHelpers import userExists, addUserToDatabase, sendChat

bp = Blueprint('owncastWebhooks', __name__)

@bp.route('/owncastWebhook',methods=['POST'])
def owncastWebhook():
    data = request.json
    db = get_db()
    if data["type"] == "USER_JOINED":
        user_id = data["eventData"]["user"]["id"]
        addUserToDatabase(user_id, db)
    elif data["type"] == "CHAT":
        display_name = data["eventData"]["user"]["displayName"]
        print("New chat message:")
        print(f'from {display_name}:')
        print(f'{data["eventData"]["body"]}')
        user_id = data["eventData"]["user"]["id"]  
        if "!points" in data["eventData"]["body"]:
            if not userExists(user_id, db):
                addUserToDatabase(user_id, db)
            try:
                cursor = db.execute(
                    "SELECT points FROM points WHERE id = ?",
                    (user_id,)
                )
                message = "{}'s points: {}".format(display_name, cursor.fetchone()[0])
                print(message)
                sendChat(message)
            except Error as e:
                print("Error occured reading points:", e.args[0])
                print("To user:", user_id)
        else: # DEBUG: give points for message
            try:
                db.execute(
                    "UPDATE points SET points = points + 10 WHERE id = ?",
                    (user_id,)
                )
                db.commit()
            except Error as e:
                print("Error occured giving DEBUG points:", e.args[0])
                print("To user:", user_id)
    return data