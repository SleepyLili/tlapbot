from flask import current_app
from tlapbot.db import get_db
from tlapbot.owncast_helpers import (use_points, add_to_redeem_queue,
        add_to_counter, read_users_points, send_chat, remove_emoji)


def handle_redeem(message, user_id):
    split_message = message[1:].split(maxsplit=1)
    redeem = split_message[0]
    if len(split_message) == 1:
        note = None
    else:
        note = split_message[1]

    if redeem not in current_app.config['REDEEMS']:
        send_chat("Can't redeem, redeem not found.")
        return

    db = get_db()
    price = current_app.config['REDEEMS'][redeem]["price"]
    redeem_type = current_app.config['REDEEMS'][redeem]["type"]
    points = read_users_points(db, user_id)

    if not points or points < price:
        send_chat(f"Can't redeem {redeem}, you don't have enough points.")
        return

    if redeem_type == "counter":
        if add_to_counter(db, redeem) and use_points(db, user_id, price):
            send_chat(f"{redeem} redeemed for {price} points.")
        else:
            send_chat(f"Redeeming {redeem} failed.")
    elif redeem_type == "list":
        if add_to_redeem_queue(db, user_id, redeem) and use_points(db, user_id, price):
            send_chat(f"{redeem} redeemed for {price} points.")
        else:
            send_chat(f"Redeeming {redeem} failed.")
    elif redeem_type == "note":
        if not note:
            send_chat(f"Cannot redeem {redeem}, no note included.")
            return
        if add_to_redeem_queue(db, user_id, redeem, remove_emoji(note)) and use_points(db, user_id, price):
            send_chat(f"{redeem} redeemed for {price} points.")
        else:
            send_chat(f"Redeeming {redeem} failed.")
    else:
        send_chat(f"{redeem} not redeemed, type of redeem not found.")
