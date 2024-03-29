from flask import current_app
from tlapbot.owncast_requests import send_chat


def send_help():
    message = []
    message.append("Tlapbot gives you points for being in chat, and then allows you to spend those points. <br>")
    message.append(f"People connected to chat receive {current_app.config['POINTS_AMOUNT_GIVEN']} points every {current_app.config['POINTS_CYCLE_TIME']} seconds. <br>")
    message.append("You can see your points and recent redeems in the Tlapbot dashboard. Look for a button to click under the stream window. <br>")
    message.append("""Tlapbot commands: <br>
        !help to see this help message. <br>
        !points to see your points. <br>"""
    )
    if current_app.config['LIST_REDEEMS']:
        message.append("Active redeems: <br>")
        for redeem, redeem_info in current_app.config['REDEEMS'].items():
            if redeem_info.get('category', None):
                if not set(redeem_info['category']).intersection(set(current_app.config['ACTIVE_CATEGORIES'])):
                    continue
            if 'type' in redeem_info and redeem_info['type'] == 'milestone':
                message.append(f"!{redeem} milestone with goal of {redeem_info['goal']}.")
            else:
                message.append(f"!{redeem} for {redeem_info['price']} points.")
            if 'info' in redeem_info:
                message.append(f" {redeem_info['info']} <br>")
            else:
                message.append("<br>")
    else:
        message.append("Check the dashboard for a list of currently active redeems.")
    send_chat(''.join(message))
