#!/bin/sh
# Initializes this directory as a plain, ungoverned repo with history.
set -e
git init -q
git config user.email agent@example.com
git config user.name "Agent"
git add README.md
git commit -q -m "initial commit"
git add convert.py
git commit -q -m "add converter"
echo "ungoverned repo initialized"
