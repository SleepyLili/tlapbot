from flask import current_app
from tlapbot.db import get_db
from tlapbot.owncast_helpers import use_points, add_to_redeem_queue

def handle_redeem(message, user_id)
    split_message = message[1:].split(maxsplit=1)
    redeem = split_message[0]
    if len(split_message) == 1:
        note = None
    else:
        note = split_message[1]

    if redeem in current_app.config['REDEEMS']:
        price = current_app.config['REDEEMS'][redeem]["price"]
        redeem_type = current_app.config['REDEEMS'][redeem]["type"]
        points = read_users_points(db, user_id)
        if points is not None and points >= price:
            if use_points(db, user_id, redeem):
                if redeem_type == "counter":
                    add_to_counter(db, redeem)
                elif redeem_type == "list":
                    add_to_redeem_queue(db, user_id, redeem)
                elif redeem_type == "note":
                    if note is not None:
                        add_to_redeem_queue(db, user_id, redeem, note)
                    else:
                        send_chat(f"Cannot redeem {redeem}, no note included.")
                send_chat(f"{redeem} redeemed for 60 points.")
            else:
                send_chat(f"{redeem} not redeemed because of an error.")
        else:
            send_chat(f"Can't redeem {redeem}, you don't have enough points.")
    else:
        send_chat("Can't redeem, redeem not found.")
        return False