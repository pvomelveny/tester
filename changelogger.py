#!/usr/bin/env python3

import click
from datetime import date
import json
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from pathlib import Path
import shutil

#####
## PATH CONSTANTS
#####
CHANGELOG_DIR = Path("~/.jenkins/userContent/changelog")
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
def maybe_get_last():
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
    with open(data_file, "w") as f:
        json.dump(payload, f)


def write_initial_log():
    payload = {TODAY: {"hash": "{}".format(GIT_HEAD), "changes": []}}
    write_log(payload)


#####
## git Functions
#####

#####
## Template Functions
#####

#####
## Main CLI
#####
@click.command()
def cli():
    # TODO: remove prints
    print(GIT_HEAD)
    print(GIT_URL)
    print(GIT_PROJECT)
    # Check if this project has previous commits
    # If not, start the log and end
    data = maybe_get_last()
    if not data:
        write_initial_log()
        return


if __name__ == "__main__":
    cli()
