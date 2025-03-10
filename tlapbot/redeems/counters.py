from flask import current_app
from sqlite3 import Error, Connection
from typing import Tuple
from tlapbot.redeems.redeems import is_redeem_active


def counter_exists(db: Connection, counter_name: str) -> bool | None:
    """Returns None only if error was logged."""
    try:
        cursor = db.execute(
            "SELECT count FROM counters WHERE name = ?",
            (counter_name,)
        )
        counter = cursor.fetchone()
        if counter is None:
            current_app.logger.warning("Counter not found in database.")
            current_app.logger.warning("Maybe you forgot to run the refresh-counters CLI command "
                                       "after you added a new counter to the config?")
            return False
        return True
    except Error as e:
        current_app.logger.error(f"Error occurred checking if counter exists: {e.args[0]}")
        current_app.logger.error(f"For counter: {counter_name}")


def add_to_counter(db: Connection, counter_name: str) -> bool:
    if counter_exists(db, counter_name):
        try:
            db.execute(
                "UPDATE counters SET count = count + 1 WHERE name = ?",
                (counter_name,)
            )
            db.commit()
            return True
        except Error as e:
            current_app.logger.error(f"Error occurred adding to counter: {e.args[0]}")
            current_app.logger.error(f"To counter: {counter_name}")
    return False


def all_counters(db: Connection) -> list[Tuple[str, int]] | None:
    """Returns list of all (even inactive) counters and their current value.
    Returns None only if error was logged."""
    try:
        cursor = db.execute(
            """SELECT name, count FROM counters"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occurred selecting all counters: {e.args[0]}")


def all_active_counters(db: Connection) -> list[Tuple[str, int]] | None:
    """Returns list of all active counters, and their current value.
    Returns None if error was logged."""
    counters = all_counters(db)
    if counters is not None:
        all_active_counters = []
        for name, count in counters:
            if is_redeem_active(name):
                all_active_counters.append((name, count))
        return all_active_counters

