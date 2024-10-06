import requests
from flask import current_app
from tlapbot.owncast_helpers import give_points_to_user
from sqlite3 import Connection
from typing import Any


def is_stream_live() -> bool:
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/status'
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error occurred checking if stream is live: {e.args[0]}")
        return False
    return r.json()["online"]


def give_points_to_chat(db: Connection) -> None:
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/integrations/clients'
    headers = {"Authorization": "Bearer " + current_app.config['OWNCAST_ACCESS_TOKEN']}
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error occurred getting users to give points to: {e.args[0]}")
        return
    if r.status_code != 200:
        current_app.logger.error(f"Error occurred when giving points: Response code not 200.")
        current_app.logger.error(f"Response code received: {r.status_code}.")
        current_app.logger.error(f"Check owncast instance url and access key.")
        return
    unique_users = set(map(lambda user_object: user_object["user"]["id"], r.json()))
    for user_id in unique_users:
        give_points_to_user(db, user_id, current_app.config['POINTS_AMOUNT_GIVEN'])


def send_chat(message: str) -> Any:
    url = current_app.config['OWNCAST_INSTANCE_URL'] + '/api/integrations/chat/send'
    headers = {"Authorization": "Bearer " + current_app.config['OWNCAST_ACCESS_TOKEN']}
    try:
        r = requests.post(url, headers=headers, json={"body": message})
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error occurred sending chat message: {e.args[0]}")
        return
    if r.status_code != 200:
        current_app.logger.error(f"Error occurred when sending chat: Response code not 200.")
        current_app.logger.error(f"Response code received: {r.status_code}.")
        current_app.logger.error(f"Check owncast instance url and access key.")
        return
    return r.json()
