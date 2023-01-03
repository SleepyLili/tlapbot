from flask import current_app
import requests
from sqlite3 import Error


# # # requests stuff # # #
def is_stream_live():
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/status'
    r = requests.get(url)
    return r.json()["online"]


def give_points_to_chat(db):
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/integrations/clients'
    headers = {"Authorization": "Bearer " + current_app.config['OWNCAST_ACCESS_TOKEN']}
    r = requests.get(url, headers=headers)
    unique_users = set(map(lambda user_object: user_object["user"]["id"], r.json()))
    for user_id in unique_users:
        give_points_to_user(db,
                            user_id,
                            current_app.config['POINTS_AMOUNT_GIVEN'])


def send_chat(message):
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/integrations/chat/send'
    headers = {"Authorization": "Bearer " + current_app.config['OWNCAST_ACCESS_TOKEN']}
    r = requests.post(url, headers=headers, json={"body": message})
    return r.json()


# # # db stuff # # #
def read_users_points(db, user_id):
    """Errors out if user doesn't exist."""
    try:
        cursor = db.execute(
            "SELECT points FROM points WHERE id = ?",
            (user_id,)
        )
        return cursor.fetchone()[0]
    except Error as e:
        current_app.logger.error("Error occured reading points:", e.args[0])
        current_app.logger.error("To user:", user_id)


def read_all_users_with_username(db, username):
    try:
        cursor = db.execute(
            "SELECT name, points FROM points WHERE name = ?",
            (username,)
        )
        users = cursor.fetchall()
        return users
    except Error as e:
        current_app.logger.error("Error occured reading points from username:", e.args[0])
        current_app.logger.error("To user:", username)


def give_points_to_user(db, user_id, points):
    try:
        db.execute(
            "UPDATE points SET points = points + ? WHERE id = ?",
            (points, user_id,)
        )
        db.commit()
    except Error as e:
        current_app.logger.error("Error occured giving points:", e.args[0])
        current_app.logger.error("To user:", user_id, "  amount of points:", points)


def use_points(db, user_id, points):
    try:
        db.execute(
            "UPDATE points SET points = points - ? WHERE id = ?",
            (points, user_id,)
        )
        db.commit()
        return True
    except Error as e:
        current_app.logger.error("Error occured using points:", e.args[0])
        current_app.logger.error("From user:", user_id, "  amount of points:", points)
        return False


def user_exists(db, user_id):
    try:
        cursor = db.execute(
            "SELECT points FROM points WHERE id = ?",
            (user_id,)
        )
        if cursor.fetchone() is None:
            return False
        return True
    except Error as e:
        current_app.logger.error("Error occured checking if user exists:", e.args[0])
        current_app.logger.error("To user:", user_id)


def add_user_to_database(db, user_id, display_name):
    """ Adds a new user to the database. Does nothing if user is already in."""
    try:
        cursor = db.execute(
            "SELECT points, name FROM points WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        if user is None:
            cursor.execute(
                "INSERT INTO points(id, name, points) VALUES(?, ?, 10)",
                (user_id, display_name)
            )
        if user is not None and user[1] is None:
            cursor.execute(
                """UPDATE points
                SET name = ?
                WHERE id = ?""",
                (display_name, user_id)
            )
        db.commit()
    except Error as e:
        current_app.logger.error("Error occured adding user to db:", e.args[0])
        current_app.logger.error("To user:", user_id, display_name)


def change_display_name(db, user_id, new_name):
    try:
        cursor = db.execute(
            "UPDATE points SET name = ? WHERE id = ?",
            (new_name, user_id)
        )
        db.commit()
    except Error as e:
        current_app.logger.error("Error occured changing display name:", e.args[0])
        current_app.logger.error("To user:", user_id, new_name)


def add_to_counter(db, counter_name):
    try:
        cursor = db.execute(
            "UPDATE counters SET count = count + 1 WHERE name = ?",
            (counter_name,)
        )
        db.commit()
    except Error as e:
        current_app.logger.error("Error occured adding to counter:", e.args[0])
        current_app.logger.error("To counter:", counter_name)


def add_to_redeem_queue(db, user_id, redeem_name, note=None):
    try:
        cursor = db.execute(
            "INSERT INTO redeem_queue(redeem, redeemer_id, note) VALUES(?, ?, ?)",
            (redeem_name, user_id, note)
            )
        db.commit()
    except Error as e:
        current_app.logger.error("Error occured adding to redeem queue:", e.args[0])
        current_app.logger.error("To user:", user_id, " with redeem:", redeem_name, "with note:", note)


def all_counters(db):
    try:
        cursor = db.execute(
            """SELECT counters.name, counters.count FROM counters"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error("Error occured selecting all counters:", e.args[0])


def pretty_redeem_queue(db):
    try:
        cursor = db.execute(
            """SELECT redeem_queue.created, redeem_queue.redeem, redeem_queue.note, points.name
            FROM redeem_queue
            INNER JOIN points
            on redeem_queue.redeemer_id = points.id"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error("Error occured selecting pretty redeem queue:", e.args[0])


def whole_redeem_queue(db):
    try:
        cursor = db.execute(
            "SELECT * from redeem_queue"
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error("Error occured selecting redeem queue:", e.args[0])


def remove_duplicate_usernames(db, user_id, username):
    try:
        cursor = db.execute(
            """UPDATE points
            SET name = NULL
            WHERE name = ? AND NOT id = ?""",
            (username, user_id)
        )
        db.commit()
    except Error as e:
        current_app.logger.error("Error occured removing duplicate usernames:", e.args[0])
