from flask import current_app
from sqlite3 import Error, Connection
from typing import Tuple, Any
from tlapbot.owncast_helpers import use_points
from tlapbot.tlapbot_types import Redeem, Redeems

def counter_exists(db: Connection, counter_name: str) -> bool:
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


def add_to_milestone(db: Connection, user_id: str, redeem_name: str, points_donated: int) -> bool:
    try:
        cursor = db.execute(
            "SELECT progress, goal FROM milestones WHERE name = ?",
            (redeem_name,)
        )
        row = cursor.fetchone()
        if row is None:
            current_app.logger.warning("Milestone not found in database.")
            current_app.logger.warning("Maybe you forgot to run the refresh-milestones CLI command "
                                       "after you added a new milestone to the config?")
            return False
        progress, goal = row
        if progress + points_donated > goal:
            points_donated = goal - progress
            if points_donated < 0:
                points_donated = 0
        if use_points(db, user_id, points_donated):
            cursor = db.execute(
                "UPDATE milestones SET progress = ? WHERE name = ?",
                (progress + points_donated, redeem_name)
            )
            db.commit()
            return True
    except Error as e:
        current_app.logger.error(f"Error occurred updating milestone: {e.args[0]}")
    return False

# TODO: milestone is complete when progress equals goal?
def milestone_complete(db: Connection, redeem_name: str) -> bool:
    try:
        cursor = db.execute(
            "SELECT complete FROM milestones WHERE name = ?",
            (redeem_name,)
        )
        row = cursor.fetchone()
        if row is None:
            current_app.logger.warning("Milestone not found in database.")
            current_app.logger.warning("Maybe you forgot to run the refresh-milestones CLI command "
                                       "after you added a new milestone to the config?")
        else:
            return row[0]
    except Error as e:
        current_app.logger.error(f"Error occurred checking if milestone is complete: {e.args[0]}")


def check_apply_milestone_completion(db: Connection, redeem_name: str) -> bool:
    try:
        cursor = db.execute(
            "SELECT progress, goal FROM milestones WHERE name = ?",
            (redeem_name,)
        )
        row = cursor.fetchone()
        if row is None:
            current_app.logger.warning("Milestone not found in database.")
            current_app.logger.warning("Maybe you forgot to run the refresh-milestones CLI command "
                                       "after you added a new milestone to the config?")
        else:
            progress, goal = row
            if progress == goal:
                cursor = db.execute(
                    "UPDATE milestones SET complete = TRUE WHERE name = ?",
                    (redeem_name,)
                )
                db.commit()
                return True
        return False
    except Error as e:
        current_app.logger.error(f"Error occurred applying milestone completion: {e.args[0]}")
        return False


def all_milestones(db: Connection) -> list[Tuple[str, int, int]]:
    try:
        cursor = db.execute(
            """SELECT name, progress, goal FROM milestones"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occurred selecting all milestones: {e.args[0]}")


def all_active_milestones(db: Connection) -> list[Tuple[str, int, int]]:
    milestones = all_milestones(db)
    all_active_milestones = []
    for name, progress, goal in milestones:
        if is_redeem_active(name):
            all_active_milestones.append((name, progress, goal))
    return all_active_milestones


def all_counters(db: Connection) -> list[Tuple[str, int]]:
    try:
        cursor = db.execute(
            """SELECT name, count FROM counters"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occurred selecting all counters: {e.args[0]}")


def all_active_counters(db: Connection) -> list[Tuple[str, int]]:
    counters = all_counters(db)
    all_active_counters = []
    for name, count in counters:
        if is_redeem_active(name):
            all_active_counters.append((name, count))
    return all_active_counters


def all_active_redeems() -> dict[str, dict[str, Any]]:
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


def pretty_redeem_queue(db: Connection) -> list[Tuple[str, str, str, str]]:
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


def whole_redeem_queue(db: Connection) -> list[Any]:
    try:
        cursor = db.execute(
            "SELECT * from redeem_queue" #TODO: specify columns to fetch
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occurred selecting redeem queue: {e.args[0]}")


def is_redeem_active(redeem_name: str) -> bool | None:
    """Checks if redeem is active. Pulls the redeem by name from config."""
    active_categories = current_app.config['ACTIVE_CATEGORIES']
    redeem_dict = current_app.config['REDEEMS'].get(redeem_name, None)
    if redeem_dict:
        if "category" in redeem_dict:
            for category in redeem_dict["category"]:
                if category in active_categories:
                    return True
            return False
        else:
            return True
    return None # redeem does not exist, unknown active state



def is_redeem_from_config_active(redeem: tuple[str, Redeem], active_categories: list[str]) -> bool:
    """Checks if redeem is active. `redeem` is a whole key:value pair from redeems config."""
    if isinstance(redeem[1].get("category"), list):
        for category in redeem[1]["category"]:
            if category in active_categories:
                return True
        return False
    return True


def remove_inactive_redeems(redeems: Redeems, active_categories: list[str]) -> Redeems:
    return dict(filter(lambda redeem: is_redeem_from_config_active(redeem, active_categories),
                       redeems.items()))