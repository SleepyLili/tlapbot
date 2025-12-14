from sqlite3 import Connection
from tlapbot.db import get_db
from tlapbot.owncast_requests import send_chat
from tlapbot.owncast_helpers import read_users_points, use_points
from tlapbot.redeems.polls import poll_option_exists, vote_in_poll


def handle_poll_vote(message: str, user_id: str) -> None:
    split_message = message[5:].split(maxsplit=2)
    if len(split_message) < 3:
        send_chat("Can't vote for poll, not enough arguments in message.")
        return
    poll_name = split_message[0]
    option = split_message[1]
    poll_points = split_message[2]

    db: Connection = get_db()
    if not poll_option_exists(db, poll_name, option):
        send_chat("Can't vote for poll, poll and option combination not found.")
        return
    if not poll_points.isdigit():
        send_chat(f"Can't vote in {poll_name} poll, donation amount is not a number.")
        return
    user_points = read_users_points(db, user_id)
    if not user_points:
        send_chat(f"Can't vote in {poll_name} poll, failed to read users' points.")
        return
    poll_points = int(poll_points)
    if user_points < poll_points:
        send_chat(f"Can't vote in {poll_name} poll, you're voting with more points than you have.")
        return
    if (vote_in_poll(db, poll_name, option, poll_points) and 
            use_points(db, user_id, poll_points)):
        send_chat(f"{poll_points} points donated to {option} in poll {poll_name}")