from flask import Flask, request, json, Blueprint, current_app
from tlapbot.db import get_db
from tlapbot.owncast_helpers import (add_user_to_database, change_display_name,
        user_exists, send_chat, read_users_points, remove_duplicate_usernames)
from tlapbot.help_message import send_help
from tlapbot.redeems_handler import handle_redeem


bp = Blueprint('owncast_webhooks', __name__)


@bp.route('/owncastWebhook', methods=['POST'])
def owncast_webhook():
    data = request.json
    db = get_db()

    # Make sure user is in db before doing anything else.
    if data["type"] in ["CHAT", "NAME_CHANGED", "USER_JOINED"]:
        user_id = data["eventData"]["user"]["id"]
        display_name = data["eventData"]["user"]["displayName"]
        add_user_to_database(db, user_id, display_name)

    if data["type"] == "USER_JOINED":
        if data["eventData"]["user"]["authenticated"]:
            remove_duplicate_usernames(db, user_id, display_name)
    elif data["type"] == "NAME_CHANGE":
        user_id = data["eventData"]["user"]["id"]
        new_name = data["eventData"]["newName"]
        change_display_name(db, user_id, new_name)
        if data["eventData"]["user"]["authenticated"]:
            remove_duplicate_usernames(db, user_id, new_name)
    elif data["type"] == "CHAT":
        user_id = data["eventData"]["user"]["id"]
        display_name = data["eventData"]["user"]["displayName"]
        current_app.logger.debug(f'New chat message from {display_name}:')
        current_app.logger.debug(f'{data["eventData"]["body"]}')
        if data["eventData"]["body"].startswith("!help"):
            send_help()
        elif data["eventData"]["body"].startswith("!points"):
            points = read_users_points(db, user_id)
            send_chat(f"{display_name}'s points: {points}")
        elif data["eventData"]["body"].startswith("!name_update"):
            # Forces name update in case bot didn't catch the NAME_CHANGE
            # event. Also removes saved usernames from users with same name
            # if user is authenticated.
            change_display_name(db, user_id, display_name)
            if data["eventData"]["user"]["authenticated"]:
                remove_duplicate_usernames(db, user_id, display_name)
        elif data["eventData"]["body"].startswith("!"):  # TODO: make prefix configurable
            handle_redeem(data["eventData"]["body"], user_id)
    return data
