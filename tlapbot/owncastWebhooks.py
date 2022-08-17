from flask import Flask,request,json,g,Blueprint
from sqlite3 import Error
from tlapbot.db import get_db
import requests

bp = Blueprint('owncastWebhooks', __name__)

def userExists(user_id, db):
    try:
        cursor = db.execute(
            "SELECT points FROM points WHERE id = ?",
            (user_id,)
        )
        if cursor.fetchone() == None:
            return False
        return True
    except Error as e:
        print("Error occured checking if user exists:", e.args[0])
        print("To user:", user_id)

# only adds user if they aren't already in.
def addUserToDatabase(user_id, db):
    try:
        cursor = db.execute(
            "SELECT points FROM points WHERE id = ?",
            (user_id,)
        )
        if cursor.fetchone() == None:
            cursor.execute(
                "INSERT INTO points(id, points) VALUES(?, 10)",
                (user_id,)
            )
        db.commit()
    except Error as e:
        print("Error occured adding user to db:", e.args[0])
        print("To user:", user_id)

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
                print("{}'s points: {}".format(display_name, cursor.fetchone()[0]))
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

if __name__ == '__main__':
    app.run(debug=True)