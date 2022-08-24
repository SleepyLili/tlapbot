from flask import current_app
import requests
from sqlite3 import Error


def user_exists(user_id, db):
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
def add_user_to_database(user_id, db):
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

def send_chat(message): # TODO: url to constant?
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/integrations/chat/send'
    headers = {"Authorization": "Bearer " + current_app.config['OWNCAST_ACCESS_TOKEN']}
    r = requests.post(url, headers=headers, json={"body": message})
    return r.json()