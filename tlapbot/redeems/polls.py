from flask import current_app
from sqlite3 import Error, Connection


def get_poll_votes(db: Connection, poll_name: str) -> dict[str, int] | None:
    """Get all poll votes and point values for a given `poll_name`"""
    try:
        options = {}
        cursor = db.execute(
            "SELECT option, points from polls WHERE poll_name = ?",
            (poll_name,)
        )
        for row in cursor:
            options[row[0]] = row[1]
        return options
    except Error as e:
        current_app.logger.error(f"Error occurred getting poll votes: {e.args[0]}")
        current_app.logger.error(f"For poll {poll_name}")


def all_active_polls(db: Connection) -> dict[str, dict[str, int]] | None:
    """Returns a dict where the keys are poll names, values is a dict of options and points.
    Returns None if polls aren't enabled."""
    if not current_app.config['POLLS_ENABLED']:
        return None
    polls = current_app.config['POLLS']
    poll_votes = {}
    for poll_name in polls.keys():
        poll_votes[poll_name] = get_poll_votes(db, poll_name)
    return poll_votes


def max_poll_votes(poll_dict: dict[str, int]) -> int:
    """Returns the maximum number of poll votes/points. Input is the output of `get_poll_votes`"""
    highest_points = 0
    for _, points in poll_dict.items():
        if points > highest_points:
            highest_points = points
    return highest_points


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
                "UPDATE polls SET points = points + ? WHERE poll_name = ? and option = ?",
                (points, poll_name, option)
                )
            db.commit()
            return True
        except Error as e:
            current_app.logger.error(f"Error occurred updating poll: {e.args[0]}")
        return False
