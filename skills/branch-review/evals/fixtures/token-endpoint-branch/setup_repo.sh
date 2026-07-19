#!/bin/sh
# Initializes this directory as a git repo with a local origin, a main
# branch, and feature/session-tokens checked out. The branch seeds
# findings for a review to discover: a token value logged (SECURITY.md
# violation), a TTL unit bug (TOKEN_TTL_HOURS added to epoch seconds,
# so tokens live 24 seconds while README promises 24 hours), swallowed
# persistence errors, a committed debug print, vague bundled commit
# messages, and no test for the expiry or failure paths. One trap: the
# /tokens route shows no auth in routes.py, but Router.add_route
# authenticates by default, so "endpoint lacks auth" is a false
# positive the challenger should dismiss with a citation.
set -e
git init -q -b main
git config user.email agent@example.com
git config user.name "Agent"
git add -A -- ':!branch'
git commit -q -m "sessiond: initial import"
git init -q --bare .origin.git
git remote add origin ./.origin.git
git push -q -u origin main
git checkout -q -b feature/session-tokens
cp -R branch/. .
rm -rf branch
git add app/tokens.py app/routes.py
git commit -q -m "add tokens"
git add -A
git commit -q -m "wip"
git push -q -u origin feature/session-tokens
echo "fixture repo initialized on branch feature/session-tokens"
