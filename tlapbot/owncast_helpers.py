from flask import current_app
import requests
from sqlite3 import Error
from re import sub

# # # requests stuff # # #
def is_stream_live():
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/status'
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error occured checking if stream is live: {e.args[0]}")
        return False
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
            "SELECT count, goal FROM milestones WHERE name = ?",
            (redeem_name,)
        )
        milestone = cursor.fetchone()
        current_app.logger.error(f"Milestone: {milestone}")
        if milestone is None:
            current_app.logger.error(f"Adding milestone to db.")
            cursor = db.execute(
                    "INSERT INTO milestones(name, count, goal) VALUES(?, ?, ?)",
                    (redeem_name, 0, current_app.config['REDEEMS'][redeem_name]['goal'])
                )
        db.commit()
    except Error as e:
        current_app.logger.error(f"Error occured adding a milestone: {e.args[0]}")



def add_to_milestone(db, redeem_name, points):
    try:
        start_milestone(db, redeem_name)

        cursor = db.execute(
            "SELECT count, goal FROM milestones WHERE name = ?",
            (redeem_name,)
        )
        row = cursor.fetchone()
        count = row[0]
        goal = row[1]
        result = count + points
        if result > goal:
            result = goal
        current_app.logger.error(f"Doing db operation to add to milestone.")
        cursor = db.execute(
            "UPDATE milestones SET count = ? WHERE name = ?",
            (result, redeem_name)
        )
        db.commit()
        return True
    except Error as e:
        current_app.logger.error(f"Error occured updating milestone: {e.args[0]}")
    current_app.logger.error(f"Milestone add failed.")
    return False


def all_milestones(db):
    try:
        cursor = db.execute(
            """SELECT name, count, goal FROM milestones"""
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


def is_redeem_active(redeem, active_categories):
    if "category" in redeem[1] and redeem[1]["category"]:
        for category in redeem[1]["category"]:
            if category in active_categories:
                return True
        return False
    return True


def remove_inactive_redeems(redeems, active_categories):
    return dict(filter(lambda redeem: is_redeem_active(redeem, active_categories),
                       redeems.items()))