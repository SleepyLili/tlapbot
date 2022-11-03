from flask import Flask, request, json, Blueprint, current_app
from sqlite3 import Error
from tlapbot.db import get_db
from tlapbot.owncast_helpers import (add_user_to_database, change_display_name,
        user_exists, send_chat, read_users_points, remove_duplicate_usernames)
from tlapbot.redeems_handler import handle_redeem

bp = Blueprint('owncast_webhooks', __name__)


@bp.route('/owncastWebhook', methods=['POST'])
def owncast_webhook():
    data = request.json
    db = get_db()
    if data["type"] == "USER_JOINED":
        user_id = data["eventData"]["user"]["id"]
        display_name = data["eventData"]["user"]["displayName"]
        # CONSIDER: join points for joining stream
        add_user_to_database(db, user_id, display_name)
        if data["eventData"]["user"]["authenticated"]:
            remove_duplicate_usernames(db, user_id, display_name)
    elif data["type"] == "NAME_CHANGE":
        user_id = data["eventData"]["user"]["id"]
        new_name = data["eventData"]["newName"]
        change_display_name(db, user_id, new_name)
        if data["eventData"]["user"]["authenticated"]:
            remove_duplicate_usernames(db, user_id, display_name)
    elif data["type"] == "CHAT":
        user_id = data["eventData"]["user"]["id"]
        display_name = data["eventData"]["user"]["displayName"]
        print(f'New chat message from {display_name}:')
        print(f'{data["eventData"]["body"]}')
        if "!help" in data["eventData"]["body"]:
            message = """Tlapbot commands:
            !help to see this help message.
            !points to see your points.
            !name_update to force name update if tlapbot didn't catch it.
            Tlapbot redeems:\n"""
            for redeem, redeem_info in current_app.config['REDEEMS'].items():
                message += (f"!{redeem} for {redeem_info['price']} points.\n")
            # TODO: also make this customizable
            send_chat(message)
        elif "!points" in data["eventData"]["body"]:
            if not user_exists(db, user_id):
                add_user_to_database(db, user_id, display_name)
            points = read_users_points(db, user_id)
            message = f"{display_name}'s points: {points}"
            send_chat(message)
        elif "!name_update" in data["eventData"]["body"]:
            # Forces name update in case bot didn't catch the NAME_CHANGE
            # event. Also removes saved usernames from users with same name
            # if user is authenticated.
            change_display_name(db, user_id, display_name)
            if data["eventData"]["user"]["authenticated"]:
                remove_duplicate_usernames(db, user_id, display_name)
        elif data["eventData"]["body"].startswith("!"):  # TODO: make prefix configurable
            handle_redeem(data["eventData"]["body"], user_id)
    return data
