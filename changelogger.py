#!/usr/bin/env python3

import click
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from pathlib import Path
import shutil

#####
## PATH CONSTANTS
#####
# CHANGELOG_DIR = Path("~/.jenkins/userContent/changelog")
CHANGELOG_DIR = Path(".")
TEMPLATES = CHANGELOG_DIR / "templates"
DATA_DIR = CHANGELOG_DIR / "data"


#####
## JENKINS ENV CONSTANTS
#####
GIT_HEAD = os.environ["GIT_COMMIT"]
GIT_URL = os.environ["GIT_URL"]
GIT_PROJECT = GIT_URL.split("/")[-1].replace(".git", "")

#####
## git Functions
#####

#####
## Main CLI
#####
@click.command()
def cli():
    print(GIT_HEAD)
    print(GIT_URL)
    print(GIT_PROJECT)


if __name__ == "__main__":
    cli()
