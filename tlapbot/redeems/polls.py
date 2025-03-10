from flask import current_app
from sqlite3 import Error, Connection


def poll_option_exists(db: Connection, poll_name: str, option: str) -> bool | None:
    """Returns None only if error was logged."""
    try:
        cursor = db.execute(
            "SELECT poll_name, option FROM polls WHERE poll_name = ? and option = ?",
            (poll_name, option)
        )
        counter = cursor.fetchone()
        if counter is None:
            current_app.logger.warning("Poll and option combination not found in database.")
            current_app.logger.warning("Maybe you forgot to run the refresh-polls CLI command "
                                       "after you added a new poll to the config?")
            return False
        return True
    except Error as e:
        current_app.logger.error(f"Error occurred checking if poll exists: {e.args[0]}")
        current_app.logger.error(f"For poll&option: {poll_name}:{option}")


def vote_in_poll(db: Connection, poll_name: str, option: str, points: int) -> bool | None:
    if points <= 0:
        current_app.logger.warning(f"Vote for {poll_name}:{option} was not a positive integer.")
        return
    if poll_option_exists(db, poll_name, option):
        try:
            cursor = db.execute(
                "UPDATE polls SET progress = progress + ? WHERE poll_name = ? and option = ?",
                (points, poll_name, option)
                )
            db.commit()
            return True
        except Error as e:
            current_app.logger.error(f"Error occurred updating milestone: {e.args[0]}")
        return False
