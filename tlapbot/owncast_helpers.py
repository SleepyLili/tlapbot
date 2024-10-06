from flask import current_app
from sqlite3 import Error, Connection
from re import sub
from typing import Tuple


# # # db stuff # # #
def read_users_points(db: Connection, user_id: str) -> int | None:
    """Returns None and logs error in case of error, or if user doesn't exist."""
    try:
        cursor = db.execute(
            "SELECT points FROM points WHERE id = ?",
            (user_id,)
        )
        return cursor.fetchone()[0]
    except Error as e:
        current_app.logger.error(f"Error occurred reading points: {e.args[0]}")
        current_app.logger.error(f"Of user: {user_id}")


def read_all_users_with_username(db: Connection, username: str) -> list[Tuple[str, int]] | None:
    """Returns None only if Error was logged."""
    try:
        cursor = db.execute(
            "SELECT name, points FROM points WHERE name = ?",
            (username,)
        )
        users = cursor.fetchall()
        return users
    except Error as e:
        current_app.logger.error(f"Error occurred reading points by username: {e.args[0]}")
        current_app.logger.error(f"Of everyone with username: {username}")


def give_points_to_user(db: Connection, user_id: str, points: int) -> None:
    try:
        db.execute(
            "UPDATE points SET points = points + ? WHERE id = ?",
            (points, user_id,)
        )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occurred giving points: {e.args[0]}")
        current_app.logger.error(f"To user: {user_id} amount of points: {points}")


def use_points(db: Connection, user_id: str, points: int) -> bool:
    try:
        db.execute(
            "UPDATE points SET points = points - ? WHERE id = ?",
            (points, user_id,)
        )
        db.commit()
        return True
    except Error as e:
        current_app.logger.error(f"Error occurred using points: {e.args[0]}")
        current_app.logger.error(f"From user: {user_id} amount of points: {points}")
        return False


def user_exists(db: Connection, user_id: str) -> bool | None:
    """Returns None only if an error was logged."""
    try:
        cursor = db.execute(
            "SELECT points FROM points WHERE id = ?",
            (user_id,)
        )
        if cursor.fetchone() is None:
            return False
        return True
    except Error as e:
        current_app.logger.error(f"Error occurred checking if user exists: {e.args[0]}")
        current_app.logger.error(f"To user: {user_id}")


def add_user_to_database(db: Connection, user_id: str, display_name: str) -> None:
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
        current_app.logger.error(f"Error occurred adding user to db: {e.args[0]}")
        current_app.logger.error(f"To user id: {user_id}, with display name: {display_name}")


def change_display_name(db: Connection, user_id: str, new_name: str) -> None:
    try:
        db.execute(
            "UPDATE points SET name = ? WHERE id = ?",
            (new_name, user_id)
        )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occurred changing display name: {e.args[0]}")
        current_app.logger.error(f"To user id: {user_id}, with display name: {new_name}")


def remove_duplicate_usernames(db: Connection, user_id: str, username: str) -> None:
    try:
        db.execute(
            """UPDATE points
            SET name = NULL
            WHERE name = ? AND NOT id = ?""",
            (username, user_id)
        )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occurred removing duplicate usernames: {e.args[0]}")


# # # misc. stuff # # #
# This is now unused since rawBody attribute of the webhook now returns cleaned-up emotes.
def remove_emoji(message: str) -> str:
    return sub(
        r'<img class="emoji" alt="(:.*?:)" title=":.*?:" src="/img/emoji/.*?">',
        r'\1',
        message
    )
