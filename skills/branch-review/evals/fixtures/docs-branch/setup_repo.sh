#!/bin/sh
# Initializes this directory as a git repo with a local origin, a main
# branch, and the docs branch under review checked out. The reworded
# docs deliberately drift from src/retry.py (30s cap vs 60s, "any
# failed call" vs network errors only) so a substantive review has
# something to find.
set -e
git init -q -b main
git config user.email agent@example.com
git config user.name "Agent"
git add -A -- ':!branch'
git commit -q -m "fetchd: initial import"
git init -q --bare .origin.git
git remote add origin ./.origin.git
git push -q -u origin main
git checkout -q -b docs/clarify-retry-semantics
cp -R branch/. .
rm -rf branch
git add -A
git commit -q -m "docs: fix typos and clarify retry semantics"
git push -q -u origin docs/clarify-retry-semantics
echo "fixture repo initialized on branch docs/clarify-retry-semantics"
