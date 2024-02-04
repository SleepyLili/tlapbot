from flask import current_app
from sqlite3 import Error
from re import sub

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
        current_app.logger.error(f"Error occured reading points: {e.args[0]}")
        current_app.logger.error(f"To user: {user_id}")


def read_all_users_with_username(db, username):
    try:
        cursor = db.execute(
            "SELECT name, points FROM points WHERE name = ?",
            (username,)
        )
        users = cursor.fetchall()
        return users
    except Error as e:
        current_app.logger.error(f"Error occured reading points by username: {e.args[0]}")
        current_app.logger.error(f"To everyone with username: {username}")


def give_points_to_user(db, user_id, points):
    try:
        db.execute(
            "UPDATE points SET points = points + ? WHERE id = ?",
            (points, user_id,)
        )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occured giving points: {e.args[0]}")
        current_app.logger.error(f"To user: {user_id} amount of points: {points}")


def use_points(db, user_id, points):
    try:
        db.execute(
            "UPDATE points SET points = points - ? WHERE id = ?",
            (points, user_id,)
        )
        db.commit()
        return True
    except Error as e:
        current_app.logger.error(f"Error occured using points: {e.args[0]}")
        current_app.logger.error(f"From user: {user_id} amount of points: {points}")
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
        current_app.logger.error(f"Error occured checking if user exists: {e.args[0]}")
        current_app.logger.error(f"To user: {user_id}")


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
        current_app.logger.error(f"Error occured adding user to db: {e.args[0]}")
        current_app.logger.error(f"To user id: {user_id}, with display name: {display_name}")


def save_last_online_time(db, timestamp, from_owncast):
    try:
        db.execute(
            "INSERT OVERWRITE last_online_time(id, last_online_time, from_owncast)",
            (1, timestamp, from_owncast)
        )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occured saving last online time: {e.args[0]}")
        current_app.logger.error(f"Timestamp: {timestamp}, from_owncast: {from_owncast}")


def get_last_online_time(db):
    try:
        cursor = db.execute(
            "SELECT last_online_time FROM last_online_time WHERE id = 1"
        )
        last_online_time = cursor.fetchone()
        return last_online_time
    except Error as e:
        current_app.logger.error(f"Error occured reading last online time: {e.args[0]}")


def delete_last_online_time(db):
    try:
        db.execute("DELETE FROM last_online_time")
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occured deleting last online time: {e.args[0]}")


def change_display_name(db, user_id, new_name):
    try:
        cursor = db.execute(
            "UPDATE points SET name = ? WHERE id = ?",
            (new_name, user_id)
        )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occured changing display name: {e.args[0]}")
        current_app.logger.error(f"To user id: {user_id}, with display name: {new_name}")


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
        current_app.logger.error(f"Error occured removing duplicate usernames: {e.args[0]}")


# # # misc. stuff # # #
def remove_emoji(message):
    return sub(
        r'<img class="emoji" alt="(:.*?:)" title=":.*?:" src="/img/emoji/.*?">',
        r'\1',
        message
    )
