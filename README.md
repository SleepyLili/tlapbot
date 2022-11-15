# Tlapbot
Tlapbot is an [Owncast](https://owncast.online/) bot, aiming to add the feature of channel points and
channel point redeems to Owncast.

This bot is currently in-development. The goal is to have an experience similar
to [Twitch channel points](https://help.twitch.tv/s/article/viewer-channel-point-guide), while making use of [Owncast webhooks](https://owncast.online/thirdparty/webhooks/) and especially
[External actions](https://owncast.online/thirdparty/actions/).
## Features
The bot gives points to everyone in chat -- 10 points every 10 minutes by
default, but the time interval and amount of points can be changed.

The users in chat can then use their points on redeems -- rewards like "choose my
background music", "choose what level to play next", "react to this video" etc.
You can configure redeems to fit your stream and the activities you're
doing.

The redeems then show on a "Redeems dashboard" that everyone can view
as an External Action on the Owncast stream, or at its standalone URL.
This allows easy browsing of active challenges and recent redeems.
## Setup
Tlapbot requires Python 3, probably a fairly recent version of it too. (My live instance runs on Python 3.9.2.)

The Python prerequisites for running tlapbot are the libraries `flask`,
`requests` and `apscheduler`. If you follow the installation steps below,
they should automatically be installed if you don't have them.
### Install from git repo (as a folder)
1. Clone the repository.
2. Run `pip install -e .` in the root folder. This will install tlapbot
as a package in editable more.
3. Initialize the database:
    ```bash
    python -m flask init-db
    ```
4. Create a `instance/config.py` file and fill it in as needed.
Default values are included in `tlapbot/default_config`, and values in
`config.py` overwrite them. (The database also lives in the `instance` folder
by default.)

    Tlapbot might not work if you don't overwrite these:
    ```bash
    SECRET_KEY # get one from running `python -c 'import secrets; print(secrets.token_hex())'`
    OWNCAST_ACCESS_TOKEN # get one from owncast instance
    OWNCAST_INSTANCE_URL # default points to localhost owncast on default port
    ```
5. OPTIONAL: Create an `instance/redeems.py` file and add your custom redeems.  
  If you don't add a redeems file, the bot will initialize the default redeems from `tlapbot/default_redeems.py`.  
  More details on how to write the config and redeems files are written later in the readme.

## Owncast setup
In the Owncast web interface, navigate to the admin interface at `/admin`,
and then go to Integrations.
### Access Token
In the Access Tokens tab, generate an Access Token to put in
`instance/config.py`. The bot needs both the "send chat messages" and "perform administrative actions"
permissions, since getting the list of all connected chat users is an administrator-only
action.
### Webhook
In the webhooks tab, create a Webhook, and point it at your bot's URL with
`/owncastWebhook` added.

In debug, this will be something like `localhost:5000/owncastWebhook`. If you're not running the debug Owncast instance and bot on the same machine,
you can use a tool like [ngrok](https://ngrok.com/)
to redirect Owncast traffic to your `localhost`.
### External Action
In External Actions, point the external action to your bot's URL with `/dashboard` added.

**External Actions only work with https. Your server will need to support SSL and
https connections for this part to work.**

In development, a `localhost` address will not work with External Actions, since it doesn't provide https.
If you use [ngrok](https://ngrok.com/) to redirect Owncast traffic to localhost,
it will work because the ngrok connection is https.

**External Action config example:**
```
URL: MyTlapbotServer.com/dashboard
Action Title: Redeems Dashboard
```
#### Note about https and reverse proxying
Since External Actions require a secure https connection (for the tlapbot dashboard to work), you will need to set up a reverse proxy for tlapbot on your server. I'm not including a lot of information about it here, since I'm assuming you have some knowledge of the topic since you set up your own Owncast instance.

If you don't, the Owncast documentation about SSL and Reverse proxying is here: https://owncast.online/docs/sslproxies/

If your followed the [Owncast recommendation to use Caddy](https://owncast.online/docs/sslproxies/caddy/) you'd only need to include this in your caddyfile to make the tlapbot dashboard work:

```
MyTlapbotServer.com {
        reverse_proxy localhost:8000
}
```
then MyTlapbotServer.com/owncastWebhook is the URL for webhooks,
and MyTlapbotServer.com/dashboard is the URL for the dashboard.

(And, obviously, you'd need to own the MyTlapbotServer.com domain, and have an A record pointing to your server's IP address.)
## Running the bot
### Running in debug:
Set the FLASK_APP variable:
```bash
export FLASK_APP=tlapbot
```
or in Powershell on Windows:
```powershell
$Env:FLASK_APP = "tlapbot"
```
Run the app (in debug mode):
```bash
python -m flask --debug run 
```
### Running in production:
Set the FLASK_APP variable:
```bash
export FLASK_APP=tlapbot
```

Using the flask debug server for running apps for non-development purposes is not recommended. Rather, you should be using a proper Python WSGI server.
On my own live owncast instance, I use gunicorn.

Install gunicorn (if you don't have it installed):
```bash
pip install gunicorn
```
Run the app (with gunicorn):
```bash
gunicorn -w 1 'tlapbot:create_app()'
```

**⚠️WARNING:** Because of the way the scheduler is initialized in the project,
I recommend running tlapbot with only one gunicorn worker. (`-w 1`)

If you use multiple workers, each worker sets up its own scheduler, and then users
get given points by each worker. (So running the app with `-w 4` means users get four times as many points than listed in the config.)

I'd like to fix this shortcoming of tlapbot at some point in the future (so that it can take advantage of extra workers), but for now it's broken like this.

## Configuration files
### config.py
Values you can include in `config.py` to change how the bot behaves.

(`config.py` should be in the instance folder: `/instance/config.py` for folder install, or `/[venv]/var/tlapbot-instance/config.py` for a `.whl` package install.)
#### Channel points interval and amount
`POINTS_CYCLE_TIME` decides how often channel points are given to users in chat,
in seconds. 

`POINTS_AMOUNT_GIVEN` decides how many channel points users receive.

By default, everyone receives 10 points every 600 seconds (10 minutes).
### redeems.py
(`redeems.py` should be in the instance folder: `/instance/redeems.py` for folder install, or `/[venv]/var/tlapbot-instance/redeems.py` for a `.whl` package install.)