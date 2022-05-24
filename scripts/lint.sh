#!/bin/bash

set -xeuo pipefail

black --check nu
mypy nu
isort --check-only nu
flake8 nu
