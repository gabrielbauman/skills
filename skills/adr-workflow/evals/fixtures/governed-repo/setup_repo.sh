#!/bin/sh
# Initializes this directory as a governed git repo with proper history.
set -e
git init -q
git config user.email agent@example.com
git config user.name "Agent"
git add docs/adr
git commit -q -m "spec: adopt ADR-driven development; greeting output format"
git add -A
git commit -q -m "code: greet CLI and workflow tooling" -m "Implements: ADR-0001, ADR-0002"
python3 tools/adr/adr_tools.py install-hooks
echo "governed repo initialized"
