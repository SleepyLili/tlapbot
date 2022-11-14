# Tlapbot
Tlapbot is an [Owncast](https://owncast.online/) bot, aiming to add the feature of channel points and
channel point redeems to Owncast.

This bot is currently in-development. The goal is to have an experience similar
to [Twitch channel points](https://help.twitch.tv/s/article/viewer-channel-point-guide), while making use of [Owncast webhooks](https://owncast.online/thirdparty/webhooks/) and especially
[External actions](https://owncast.online/thirdparty/actions/).
## Features
The bot gives points to everyone in chat -- 10 points every 10 minutes by
default, but the time interval and amount of points can be changed in the config.

The users in chat can then use their points on redeems -- rewards like "choose my
background music", "choose what level to play next", "react to this video" etc.
The streamer can configure redeems to fit their stream and the activity they're
doing, to add more viewer-streamer interactions to the stream.

The redeems then show on a "Redeems dashboard" that everyone can view
as an External Action on the Owncast stream, or at its standalone URL.
This allows easy browsing of active challenges and recent redeems, for
both the streamer and the viewers.
## Setup
The Python prerequisites for running tlapbot are the libraries `flask`,
`requests` and `apscheduler`. If you follow the installation steps below,
they should automatically be installed if you don't have them.

**The only difference between installing the project as a folder and installing from a package file is that the `instance` folder will be in a slightly different place. (And that you can more easily change the code when running the project from a folder.)**
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
### Install from a .whl package file
On my live owncast instance, I like to run the bot from a `.whl` package file.
I'll include those in releases, but you can also compile your own
by cloning the repository, installing the `wheel` package and then running `python setup.py bdist_wheel`. The `.whl` file will be saved in the `dist` folder.

1. Download the `.whl` file or create your own. Move it to your server and set up your Python virtual environment.  
(I'm not sure what happens when you do all this without a virtual environment, so please do actually set one up if you're doing this.)
2. Run `pip install tlapbot-[version].whl`. This will install the package.
3. Initialize the database:
    ```bash
    python -m flask init-db
    ```
4. Create a `/[venv]/var/tlapbot-instance/config.py` file and fill it in as needed. (`[venv]` is what you called your virtual environment.)

    Default values are included in `tlapbot/default_config`, and values in
`config.py` overwrite them. (The database also lives in the `tlapbot-instance` folder
by default.)

    Tlapbot might not work if you don't overwrite these:
    ```bash
    SECRET_KEY # get one from running `python -c 'import secrets; print(secrets.token_hex())'`
    OWNCAST_ACCESS_TOKEN # get one from owncast instance
    OWNCAST_INSTANCE_URL # default points to localhost owncast on default port
    ```
5. OPTIONAL: Create an `/[venv]/var/tlapbot-instance/config.py` file and add your custom redeems.
  If you don't add a redeems file, the bot will initialize the default redeems from `tlapbot/default_redeems.py`.  
  More details on how to write the config and redeems files are written later in the readme.
## Owncast setup
In Owncast, navigate to the admin interface at `/admin`,
and then go to Integrations.
### Access Token
In Access Tokens, generate an Access Token to put in
`instance/config.py`. The bot needs both the "send chat messages" and "perform administrative actions"
permissions, since getting the list of all connected chat users is an administrator-only
action.
### Webhook
In webhooks, create a Webhook, and point it at your bot's URL with
`/owncastWebhook` added.

In debug, this will be something like `localhost:5000/owncastWebhook`,
or, if you're not running the debug Owncast instance and bot on the same machine,
you can use a tool like [ngrok](https://ngrok.com/)
to redirect the Owncast traffic to your `localhost`.
### External Action
In External Actions, point the external action to your bot's URL with `/dashboard` added.

In debug, pointing the External Action to an address like `localhost:5000/dashboard` might not work because your localhost address doesn't provide https, which owncast requires.

If you use [ngrok](https://ngrok.com/) to redirect Owncast traffic to localhost,
it will work because the ngrok connection is https.

**Example:**
```
URL: MyTlapbotServer.com/dashboard
Action Title: Redeems Dashboard
```
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
### Running in prod:
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