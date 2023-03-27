from flask import current_app
from sqlite3 import Error
from tlapbot.owncast_helpers import use_points

def counter_exists(db, counter_name):
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
        current_app.logger.error(f"Error occured checking if counter exists: {e.args[0]}")
        current_app.logger.error(f"For counter: {counter_name}")


def add_to_counter(db, counter_name):
    if counter_exists(db, counter_name):
        try:
            cursor = db.execute(
                "UPDATE counters SET count = count + 1 WHERE name = ?",
                (counter_name,)
            )
            db.commit()
            return True
        except Error as e:
            current_app.logger.error(f"Error occured adding to counter: {e.args[0]}")
            current_app.logger.error(f"To counter: {counter_name}")
    return False


def add_to_redeem_queue(db, user_id, redeem_name, note=None):
    try:
        cursor = db.execute(
            "INSERT INTO redeem_queue(redeem, redeemer_id, note) VALUES(?, ?, ?)",
            (redeem_name, user_id, note)
            )
        db.commit()
        return True
    except Error as e:
        current_app.logger.error(f"Error occured adding to redeem queue: {e.args[0]}")
        current_app.logger.error(f"To user: {user_id} with redeem: {redeem_name} with note: {note}")
    return False


def start_milestone(db, redeem_name):
    try:
        cursor = db.execute(
            "SELECT progress, goal FROM milestones WHERE name = ?",
            (redeem_name,)
        )
        milestone = cursor.fetchone()
        current_app.logger.error(f"Milestone: {milestone}")
        if milestone is None:
            cursor = db.execute(
                    "INSERT INTO milestones(name, progress, goal) VALUES(?, ?, ?)",
                    (redeem_name, 0, current_app.config['REDEEMS'][redeem_name]['goal'])
                )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occured adding a milestone: {e.args[0]}")


def add_to_milestone(db, user_id, redeem_name, points_donated):
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
        current_app.logger.error(f"Error occured updating milestone: {e.args[0]}")
    return False


def milestone_complete(db, redeem_name):
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
        current_app.logger.error(f"Error occured checking if milestone is complete: {e.args[0]}")


def check_apply_milestone_completion(db, redeem_name):
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
        current_app.logger.error(f"Error occured applying milestone completion: {e.args[0]}")
        return False


def all_milestones(db):
    try:
        cursor = db.execute(
            """SELECT name, progress, goal FROM milestones"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occured selecting all milestones: {e.args[0]}")


def all_counters(db):
    try:
        cursor = db.execute(
            """SELECT counters.name, counters.count FROM counters"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occured selecting all counters: {e.args[0]}")


def all_active_counters(db):
    counters = all_counters(db)
    all_active_counters = []
    for name, count in counters:
        if is_redeem_active(name):
            all_active_counters.append((name, count))
    return all_active_counters


def all_active_milestones(db):
    milestones = all_milestones(db)
    all_active_milestones = []
    for name, progress, goal in milestones:
        if is_redeem_active(name):
            all_active_milestones.append((name, progress, goal))
    return all_active_milestones

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
        current_app.logger.error(f"Error occured selecting pretty redeem queue: {e.args[0]}")


def whole_redeem_queue(db):
    try:
        cursor = db.execute(
            "SELECT * from redeem_queue"
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occured selecting redeem queue: {e.args[0]}")


def is_redeem_active(redeem_name):
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



def is_redeem_from_config_active(redeem, active_categories):
    """Checks if redeem is active. `redeem` is a whole key:value pair from redeems config."""
    if "category" in redeem[1] and redeem[1]["category"]:
        for category in redeem[1]["category"]:
            if category in active_categories:
                return True
        return False
    return True


def remove_inactive_redeems(redeems, active_categories):
    return dict(filter(lambda redeem: is_redeem_from_config_active(redeem, active_categories),
                       redeems.items()))