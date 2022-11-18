# Tlapbot
Tlapbot is an [Owncast](https://owncast.online/) bot that adds channel points and
channel point redeems to your Owncast page.

This bot is currently in-development. The goal is to have an experience similar
to [Twitch channel points](https://help.twitch.tv/s/article/viewer-channel-point-guide) by making use of [Owncast webhooks](https://owncast.online/thirdparty/webhooks/) and 
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
### Tlapbot bot commands
Tlapbot has these basic commands:
- `!help` sends a help string in the chat, explaining how tlapbot works.
- `!points` shows a chatter how many points they have.
- `!name_update` is a special debug command, to be used with the user's name displays wrong in the redeem dashboard. Normally, it shouldn't have to be used at all, as display names get updated automatically when the bot is running.

Then, Tlapbot automatically adds a command for each redeem in the redeem file.
### Tlapbot redeems types
Tlapbot currently supports three different redeem types.
#### List
List redeems are basic redeems, most similar to the ones on Twitch.

Every time a chatter redeems a List redeem, the redeem gets added to the list of recent redeems with a timestamp, similar to how redeems on Twitch get added to the [Twitch redeem queue](https://help.twitch.tv/s/article/making-the-most-of-channel-points?language=en_US#manage).

Unlike the Note redeems, chatters can't write messages to send along with their List redeems, so make sure the redeem makes sense on its own, like "stop talking for one minute", or "drop your weapon", etc.
#### Note
Note redeems are like List redeems, they get added to the list of recent redeems.

Unlike the List redeems, chatters can add a message to their Note redeems, so this is the ideal type for open-ended redeems like "choose what character I play as next", "choose what song to play next", etc.
#### Counter
Counter is a unique redeem type, in that it doesn't show up in the list of recent redeems, and counters don't list the people who redeemed them. This redeem type is good for any rewards or incentives where the important thing isn't "who redeemed it?" but rather "how many people redeemed it?"

Instead, the tlapbot dashboard keeps a number for each "counter", and each redeems adds +1 to it.

Counter redeems can be used to gauge interest, tally up votes, or to keep track of how many emotes should be added to the OBS scene.

### Tlapbot dashboard
All of the recent redeems and active counters are shown together in the Tlapbot dashboard. The counters are on top, along with the number of times they've been redeemed, followed by a chronological list of recent List and Note redeems.

Tlapbot dashboard is a standalone page available at `/dashboard`, made to be easily viewable as an owncast external action.

Tlapbot dashboard also shows the chatter's points balance when they open it as an external action.

![Tlapbot dashboard](https://ak.kawen.space/media/67c1ac6ed0d2f4efb09937c1cbfe864102182e990796853507860f50db7ff5f5.png)

*Tlapbot dashboard when viewed as an external action.*
## License & Contributions
Tlapbot as it currently is does not come with a license. If you're a content creator, streamer, vtuber, etc. I'll be happy to give you permission to use Tlapbot, or make changes that'd fit your stream.

I didn't make Tlapbot available under a permissive or a free software license, as Owncast is also used by some religious groups, extremist individuals, and dubious corporations to self-host their streams, and I do not want for them to use the bot.
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
`config.py` overwrite them. (The database also lives in the instance folder
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

This installation is fine both for just running Tlapbot as it is, but it also works as a dev setup if you want to make changes or contribute.

Updating should be as easy as `git pull`ing the new version.
## Owncast  configuration
In the Owncast web interface, navigate to the admin interface at `/admin`,
and then go to Integrations.
### Access Token
In the Access Tokens tab, generate an Access Token to put in
the config file in the instance folder. The bot needs both the "send chat messages" and "perform administrative actions"
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
Since External Actions require a secure https connection (for the tlapbot dashboard to work), you will need to set up a reverse proxy for tlapbot on your server. I'm not including much information about it here, since some knowledge of the topic is required to set up Owncast itself.

The Owncast documentation about SSL and Reverse proxying is here: https://owncast.online/docs/sslproxies/

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

Using the flask debug server for running apps for non-development purposes is not recommended. Rather, you should be using a proper [Python WSGI server](https://flask.palletsprojects.com/en/2.2.x/deploying/).
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

## CLI commands: updating config + redeems
Tlapbot comes with a few Click CLI commands. The commands let you clear out counters and the redeems dashboard.

#### init-db
The init-db command initializes the database.

**This command should only be run when first installing tlapbot.**
#### clear-queue
The clear-queue command clears the redeem queue and resets all active counters to zero.
You should run this command if you're about to start a new stream, and want to start with empty counters and queue.

```bash
python -m flask clear-queue
```

**If you've changed the config, and want new/different counters to work, you should run the `refresh-counters` command first.**
#### refresh-counters
This command deletes old counters that are no longer in the config file, and then adds all counters from the config file.
You should run this command every time you've added or removed counters from `redeems.py`.
```bash
python -m flask refresh-counters
```
This command only changes counters, so if you want to clear the queue with list and note redeems too, you should run `clear-queue` after it.
## Configuration files
### config.py
Values you can include in `config.py` to change how the bot behaves.

(`config.py` should be in the instance folder: `/instance/config.py` for folder install.)
#### Mandatory
Including these values is mandatory if you want tlapbot to work.
- `SECRET_KEY` is your secret key. Get one from running `python -c 'import secrets; print(secrets.token_hex())'`
- `OWNCAST_ACCESS_TOKEN` is the owncast access token that owncast will use to get list of users in chat. Generate one in your owncast instance.
- `OWNCAST_INSTANCE_URL` is the full URL of your owncast instance, like `"http://MyTlapbotServer.com"`
#### Optional
Including these values will overwrite their defaults from `/tlapbot/default_config.py`.
- `POINTS_CYCLE_TIME` decides how often channel points are given to users in chat,
in seconds. 
- `POINTS_AMOUNT_GIVEN` decides how many channel points users receive.
- `LIST_REDEEMS` if `True`, all redeems will be listed after the `!help` command in chat.
This makes the !help output quite long, so it's `False` by default.
#### Example config:
An example to show what your config like could look like
```python
SECRET_KEY= # string with secret key would be here.
OWNCAST_ACCESS_TOKEN="5AT0gbe9ZuzDunsBG0rcwfalQNTi3fvV70NPvvQHk3I="
OWNCAST_INSTANCE_URL="http://MyTlapbotServer.com"
POINTS_CYCLE_TIME=300
LIST_REDEEMS=True
```
### redeems.py
`redeems.py` is a file where you define all your custom redeems. Tlapbot will work without it, but it will load a few default, generic redeems from `tlapbot/default_redeems.py`.

(`redeems.py` should be in the instance folder: `/instance/redeems.py` for folder install.)
#### Default `redeems.py`:
```python
REDEEMS={
    "hydrate": {"price": 60, "type": "list"},
    "lurk": {"price": 1, "type": "counter", "info": "Let us know you're going to lurk."},
    "react": {"price": 200, "type": "note", "info": "Attach link to a video for me to react to."},
    "request": {"price": 100, "type": "note", "info": "Request a level, gamemode, skin, etc."}
}
```
#### File format
`redeems.py` is a config file with just a `REDEEMS` key, that assigns a dictionary of redeems to it.
Each dictionary entry is a redeem, and the dictionary keys are strings that decides the chat command for the redeem. The value is another dictionary that needs to have entries for `"price"`, `"type"` and optionally `"info"`.

- `"price"` value should be an integer that decides how many points the redeem will cost.
- `"type"` value should be either `"list"`, `"counter"` or `"note"`. This decided the redeem's type, and whether it will show up as a counter at the top of the dashboard or as an entry in the "recent redeems" chart.
- `"info"` value should be a string that describes what the command does. It's optional, but I recommend writing one for all `"list"` and `"note"` redeems (so that chatters know that they should write a note).