import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def insert_counters(db):
    for redeem, redeem_info in current_app.config['REDEEMS'].items():
        if redeem_info["type"] == "counter":
            try:
                db.execute(
                    "INSERT INTO counters(name, count) VALUES(?, 0)",
                    (redeem,)
                )
                db.commit()
            except sqlite3.Error as e:
                print("Failed inserting counters to db:", e.args[0])


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    insert_counters(db)


def clear_redeem_queue():
    db = get_db()

    try:
        cursor = db.execute(
            "DELETE FROM redeem_queue"
        )
        cursor.execute(
            """UPDATE counters SET count = 0"""
        )
        db.commit()
    except sqlite3.Error as e:
        print("Error occured deleting redeem queue:", e.args[0])


def refresh_counters():
    db = get_db()

    try:
        db.execute("DELETE FROM counters")
        db.commit()
    except sqlite3.Error as e:
        print("Error occured deleting old counters:", e.args[0])

    for redeem, redeem_info in current_app.config['REDEEMS'].items():
        if redeem_info["type"] == "counter":
            try:
                cursor = db.execute(
                    "INSERT INTO counters(name, count) VALUES(?, 0)",
                    (redeem,)
                )
                db.commit()
            except sqlite3.Error as e:
                print("Failed inserting counters to db:", e.args[0])


def refresh_milestones():
    db = get_db()
    # delete old milestones
    try:
        cursor = db.execute("SELECT name FROM milestones")
        milestones = cursor.fetchall()
        to_delete = []
        for milestone in milestones:
            milestone = milestone[0]
            if milestone not in current_app.config['REDEEMS'].keys():
                to_delete.append(milestone)
            elif current_app.config['REDEEMS'][milestone]['type'] != "milestone":
                to_delete.append(milestone)
        for milestone in to_delete:
            cursor.execute("DELETE FROM milestones WHERE name = ?", (milestone,))
        db.commit()
    except sqlite3.Error as e:
        print("Failed deleting old milestones from db:", e.args[0])

    # add new milestones
    try:
        for redeem, redeem_info in current_app.config['REDEEMS'].items():
            if redeem_info["type"] == "milestone":
                cursor = db.execute(
                    "SELECT goal FROM milestones WHERE name = ?",
                    (redeem,)
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO milestones(name, progress, goal) VALUES(?, 0, ?)",
                        (redeem, redeem_info['goal'])
                    )
        db.commit()
    except sqlite3.Error as e:
        print("Failed inserting milestones to db:", e.args[0])




@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('clear-queue')
@with_appcontext
def clear_queue_command():
    """Remove all redeems from the redeem queue."""
    clear_redeem_queue()
    click.echo('Cleared redeem queue.')


@click.command('refresh-counters')
@with_appcontext
def refresh_counters_command():
    """Refresh counters from current config file.
    (Remove old ones, add new ones.)"""
    refresh_counters()
    click.echo('Counters refreshed.')


@click.command('clear-refresh')
@with_appcontext
def refresh_and_clear_command():
    """Refresh counters and clear queue."""
    refresh_counters()
    clear_redeem_queue()
    click.echo('Counters refreshed and queue cleared.')


@click.command('refresh-milestones')
@with_appcontext
def refresh_milestones_command():
    """Initialize all milestones from the redeems file, 
    delete milestones not in redeem file."""
    refresh_milestones()
    click.echo('Refreshed milestones.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
