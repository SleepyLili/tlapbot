from flask import Flask,request,json,Blueprint
from sqlite3 import Error
from tlapbot.db import get_db
from tlapbot.owncast_helpers import *

bp = Blueprint('owncast_webhooks', __name__)

@bp.route('/owncastWebhook',methods=['POST'])
def owncast_webhook():
    data = request.json
    db = get_db()
    if data["type"] == "USER_JOINED":
        user_id = data["eventData"]["user"]["id"]
        display_name = data["eventData"]["user"]["displayName"]
        # CONSIDER: join points for joining stream
        add_user_to_database(db, user_id, display_name)
    elif data["type"] == "NAME_CHANGE":
        user_id = data["eventData"]["user"]["id"]
        new_name = data["eventData"]["newName"]
        old_names = data["eventData"]["user"]["previousNames"]
        change_display_name(db, user_id, new_name)
    elif data["type"] == "CHAT":
        user_id = data["eventData"]["user"]["id"]
        display_name = data["eventData"]["user"]["displayName"]
        print(f'New chat message from {display_name}:')
        print(f'{data["eventData"]["body"]}')
        if "!help" in data["eventData"]["body"]:
            message = """Tlapbot commands:
            !points to see your points.
            !drink to redeem a pitíčko for 60 points.
            That's it for now."""
            send_chat(message)
        elif "!points" in data["eventData"]["body"]:
            if not user_exists(db, user_id):
                add_user_to_database(db, user_id, display_name)
            points = read_users_points(db, user_id)
            message = "{}'s points: {}".format(display_name, points)
            send_chat(message)
        elif "!drink" in data["eventData"]["body"]:
            points = read_users_points(db, user_id)
            if points is not None and points >= 60:
                if use_points(db, user_id, 60):
                    add_to_redeem_queue(db, user_id, "drink")
                    send_chat("Pitíčko redeemed for 60 points.")
                else:
                    send_chat("Pitíčko not redeemed because of an error.")
            else:
                send_chat("Can't redeem pitíčko, you don't have enough points.")
        elif "!name_update" in data["eventData"]["body"]:
            # Forces name update in case bot didn't catch the NAME_CHANGE
            # event. Theoretically only needed when bot was off.
            change_display_name(db, user_id, display_name)
    return data