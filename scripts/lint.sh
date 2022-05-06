#!/bin/bash

set -xeuo pipefail

black --check newmu
mypy newmu
isort --check-only newmu
flake8 newmu
