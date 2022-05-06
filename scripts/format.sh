#!/usr/bin/env bash

set -xeuo pipefail

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place $1 --exclude=__init__.py
black $1
isort $1
