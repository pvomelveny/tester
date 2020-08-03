#!/usr/bin/env python3

import click
from datetime import date
import json
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from pathlib import Path
import shutil
import subprocess

#####
## PATH CONSTANTS
#####
CHANGELOG_DIR = Path("/home/ubuntu/.jenkins/userContent/changelog")
# CHANGELOG_DIR = Path(".")
TEMPLATES = CHANGELOG_DIR / "templates"
DATA_DIR = CHANGELOG_DIR / "data"


#####
## JENKINS ENV CONSTANTS
#####
GIT_HEAD = os.environ["GIT_COMMIT"]
GIT_URL = os.environ["GIT_URL"]
GIT_PROJECT = GIT_URL.split("/")[-1].replace(".git", "")


#####
## TODAY
#####
TODAY = date.today().strftime("%Y-%m-%d")

#####
## File Functions
#####
def maybe_get_data():
    """
    manages the file with commits and dates.
    Returns last commit if possible otherwise None
    """
    data_file = DATA_DIR / (GIT_PROJECT + ".json")
    if data_file.exists():
        with open(data_file, "r") as f:
            data = json.load(f)
    else:
        data = None

    return data


def write_log(payload):
    data_file = DATA_DIR / (GIT_PROJECT + ".json")
    # TODO: remove print
    print(data_file)
    with open(str(data_file), "w") as f:
        json.dump(payload, f)


def write_initial_log():
    payload = {
        TODAY: {
            "hash": "{}".format(GIT_HEAD),
            "changes": [
                "This is where we have started logging, stay tuned for real logs"
            ],
        }
    }
    write_log(payload)


#####
## git Functions
#####
def git_history_between(old, new):
    result = subprocess.run(
        ["git", "--oneline", "--ancestry-path", "{}..{}".format(old, new)],
        stdout=subprocess.PIPE,
    )
    lines = result.stdout.decode("utf-8").split("\n")
    return lines


#####
## Jinja2 Template Functions
#####

#####
## Main CLI
#####
@click.command()
def cli():
    # Check if this project has previous commits
    # Load the json if so
    # If not, start the log and end
    data = maybe_get_data()
    if not data:
        write_initial_log()
        return

    # Sort the dates in the file, most recent first
    sorted_keys = sorted(data, reverse=True)
    last_commit = data[sorted_keys[0]]["hash"]
    # Bail if there have been no changes, no changes to log
    if last_commit == GIT_HEAD:
        return

    # Git new commit history
    new_commits = git_history_between(last_commit, GIT_HEAD)
    print(new_commits)


if __name__ == "__main__":
    cli()
