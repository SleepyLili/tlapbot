from flask import current_app
from sqlite3 import Error, Connection
from typing import Tuple, Any
from tlapbot.tlapbot_types import Redeems

# TODO: test if the new default works
def add_to_redeem_queue(db: Connection, user_id: str, redeem_name: str, note: str="") -> bool:
    try:
        db.execute(
            "INSERT INTO redeem_queue(redeem, redeemer_id, note) VALUES(?, ?, ?)",
            (redeem_name, user_id, note)
            )
        db.commit()
        return True
    except Error as e:
        current_app.logger.error(f"Error occurred adding to redeem queue: {e.args[0]}")
        current_app.logger.error(f"To user: {user_id} with redeem: {redeem_name} with note: {note}")
    return False

def all_active_redeems() -> Redeems:
    """Returns list of all active redeems."""
    redeems = current_app.config['REDEEMS']
    all_active_redeems = {}
    for redeem_name, redeem_dict in redeems.items():
        if redeem_dict.get('category', None):
            for category in redeem_dict['category']:
                if category in current_app.config['ACTIVE_CATEGORIES']:
                    all_active_redeems[redeem_name] = redeem_dict
                    break
        else:
            all_active_redeems[redeem_name] = redeem_dict
    return all_active_redeems


def pretty_redeem_queue(db: Connection) -> list[Tuple[str, str, str, str]] | None:
    """Returns a 'pretty' redeem queue, with name of the redeemer joined instead of ID.
    Returns None only if error was logged."""
    try:
        cursor = db.execute(
            """SELECT redeem_queue.created, redeem_queue.redeem, redeem_queue.note, points.name
            FROM redeem_queue
            INNER JOIN points
            on redeem_queue.redeemer_id = points.id"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occurred selecting pretty redeem queue: {e.args[0]}")


def whole_redeem_queue(db: Connection) -> list[Any] | None:
    """Returns None if error was logged."""
    try:
        cursor = db.execute(
            "SELECT * from redeem_queue" #TODO: specify columns to fetch
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occurred selecting redeem queue: {e.args[0]}")


def is_redeem_active(redeem_name: str) -> bool | None:
    """Checks if redeem is active. Pulls the redeem by name from config.
    Returns None if the redeem doesn't exist."""
    active_categories = current_app.config['ACTIVE_CATEGORIES']
    redeem_dict = current_app.config['REDEEMS'].get(redeem_name, None)
    if redeem_dict:
        if redeem_dict.get('category', None):
            for category in redeem_dict["category"]:
                if category in active_categories:
                    return True
            return False
        else:
            return True
    return None # redeem does not exist, unknown active state