from flask import current_app
from tlapbot.owncast_helpers import send_chat


def send_help():
    message = []
    message.append("""Tlapbot commands:
        !help to see this help message.
        !points to see your points.
        !name_update to force name update if tlapbot didn't catch it.\n"""
    )
    if current_app.config['LIST_REDEEMS']:
        message.append("Tlapbot redeems:\n")
        for redeem, redeem_info in current_app.config['REDEEMS'].items():
            if 'info' in redeem_info:
                message.append(f"!{redeem} for {redeem_info['price']} points. {redeem_info['info']}\n")
            else:
                message.append(f"!{redeem} for {redeem_info['price']} points.\n")
    send_chat(''.join(message))