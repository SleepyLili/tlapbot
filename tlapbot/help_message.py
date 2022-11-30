from flask import current_app
from tlapbot.owncast_helpers import send_chat


help_message = f"""
Tlapbot gives you points for being in chat, and then allows you to spend those points.
People connected to chat receive {current_app.config['POINTS_AMOUNT_GIVEN']} points every {current_app.config['POINTS_CYCLE_TIME']} seconds.
You can see your points and recent redeems in the Tlapbot dashboard. Look for a button to click under the stream window.
Tlapbot commands:
        !help to see this help message.
        !points to see your points.
""".lstrip()

def send_help():
    message = "" + help_message
    
    if not current_app.config['LIST_REDEEMS']:
        message += "Check the dashboard for a list of currently active redeems."
        send_chat(message)
        return

    message += "Active redeems:\n"
    for redeem, redeem_info in current_app.config['REDEEMS'].items():
        if 'info' in redeem_info:
            message += f"!{redeem} for {redeem_info['price']} points. {redeem_info['info']}\n"
        else:
            message += f"!{redeem} for {redeem_info['price']} points.\n"
        
    send_chat(message)
