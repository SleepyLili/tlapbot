from flask import current_app
from sqlite3 import Error, Connection
from typing import Tuple, Any
from tlapbot.owncast_helpers import use_points
from tlapbot.redeems import is_redeem_active


# TODO: add a milestone_exists check?
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

def milestone_complete(db: Connection, redeem_name: str) -> bool | None:
    """Returns None only if error was logged."""
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
                return True
            return False
    except Error as e:
        current_app.logger.error(f"Error occurred checking if milestone is complete: {e.args[0]}")


def all_milestones(db: Connection) -> list[Tuple[str, int, int]] | None:
    """Returns list of all (even inactive) milestones, their progress and their goal.
    Returns None only if error was logged."""
    try:
        cursor = db.execute(
            """SELECT name, progress, goal FROM milestones"""
        )
        return cursor.fetchall()
    except Error as e:
        current_app.logger.error(f"Error occurred selecting all milestones: {e.args[0]}")


def all_active_milestones(db: Connection) -> list[Tuple[str, int, int]] | None:
    """Returns list of all active milestones, their progress and their goal.
    Returns None only if error was logged."""
    milestones = all_milestones(db)
    if milestones is not None:
        all_active_milestones = []
        for name, progress, goal in milestones:
            if is_redeem_active(name):
                all_active_milestones.append((name, progress, goal))
        return all_active_milestones

