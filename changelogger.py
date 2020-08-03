#!/usr/bin/env python3

import click
from datetime import datetime
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
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
BUILD_NUMBER = os.environ.get("BUILD_NUMBER")


#####
## RIGHT NOW
#####
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        with open(str(data_file), "r") as f:
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
        NOW: {
            "hash": "{}".format(GIT_HEAD),
            "changes": [
                "This is where we have started logging, stay tuned for real logs"
            ],
            "build_number": BUILD_NUMBER,
        }
    }
    write_log(payload)


#####
## git Functions
#####
def git_history_between(old, new):
    result = subprocess.run(
        ["git", "log", "--oneline", "--ancestry-path", "{}..{}".format(old, new)],
        stdout=subprocess.PIPE,
    )
    lines = result.stdout.decode("utf-8").split("\n")
    return [line for line in lines if line]


#####
## Jinja2 Template Functions
#####

#####
## Main CLI
#####
@click.command()
@click.option("--keep", default=100, help="number of logs to keep")
def cli(keep):
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

    # Update data and remove logs over keep limit
    data[NOW] = {"hash": GIT_HEAD, "changes": new_commits, "build_number": BUILD_NUMBER}
    sorted_keys = sorted(data, reverse=True)

    changelog = {key: data[key] for key in sorted_keys[:keep]}

    # Write out this new to data
    write_log(changelog)

    # Create Jinja Template
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("changelog.jinja")
    rendered = template.render(
        project_name=GIT_PROJECT, sorted_keys=sorted_keys, changelog=changelog
    )

    out_file = str(CHANGELOG_DIR / "logs" / "{}.html".format(GIT_PROJECT))
    print(out_file)
    with open(out_file, "w") as f:
        f.write(rendered)


if __name__ == "__main__":
    cli()
