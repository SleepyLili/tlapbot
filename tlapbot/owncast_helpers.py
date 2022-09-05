from flask import current_app
import requests
from sqlite3 import Error

def read_users_points(db, user_id):
    try:
        cursor = db.execute(
            "SELECT points FROM points WHERE id = ?",
            (user_id,)
        )
        return cursor.fetchone()[0]
    except Error as e:
        print("Error occured reading points:", e.args[0])
        print("To user:", user_id)

def give_points_to_user(db, user_id, points):
    try:
        db.execute(
        "UPDATE points SET points = points + ? WHERE id = ?",
        (points, user_id,)
        )
        db.commit()
    except Error as e:
        print("Error occured giving DEBUG points:", e.args[0])
        print("To user:", user_id, "  amount of points:", points)

def use_points(db, user_id, points):
    try:
        db.execute(
        "UPDATE points SET points = points - ? WHERE id = ?",
        (points, user_id,)
        )
        db.commit()
    except Error as e:
        print("Error occured using points:", e.args[0])
        print("From user:", user_id, "  amount of points:", points)

def give_points_to_chat(db):
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/integrations/clients'
    headers = {"Authorization": "Bearer " + current_app.config['OWNCAST_ACCESS_TOKEN']}
    r = requests.post(url, headers=headers)
    for user_object in r.json():
        give_points_to_user(db,
                            user_object["user"]["id"],
                            current_app.config['POINTS_AMOUNT_GIVEN'])

def user_exists(db, user_id):
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

""" Adds a new user to the database. Does nothing if user is already in."""
def add_user_to_database(db, user_id):
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

def send_chat(message):
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/integrations/chat/send'
    headers = {"Authorization": "Bearer " + current_app.config['OWNCAST_ACCESS_TOKEN']}
    r = requests.post(url, headers=headers, json={"body": message})
    return r.json()