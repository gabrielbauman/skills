#!/bin/sh
# Initializes this directory as a git repo with a local origin, a main
# branch, and fix/upload-limits checked out. The branch is used to test
# the challenge round: the "missing auth" finding in the eval prompt is
# a false positive (App.register wraps every handler in auth middleware),
# the unbounded body read is a real defect raised without a citation,
# and the swallowed parse error and untested 413 path are real.
set -e
git init -q -b main
git config user.email agent@example.com
git config user.name "Agent"
git add -A -- ':!branch'
git commit -q -m "api: initial import"
git init -q --bare .origin.git
git remote add origin ./.origin.git
git push -q -u origin main
git checkout -q -b fix/upload-limits
cp -R branch/. .
rm -rf branch
git add config api/upload.py
git commit -q -m "upload: enforce configurable size limit"
git add -A
git commit -q -m "upload: wire handler and add tests"
git push -q -u origin fix/upload-limits
echo "fixture repo initialized on branch fix/upload-limits"
