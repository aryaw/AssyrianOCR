#!/usr/bin/env bash
set -e
LOCAL_PYENV="$PWD/.pyenv"
if [ -d "$LOCAL_PYENV" ]; then
  echo ".pyenv exists, skipping clone"
else
  git clone https://github.com/pyenv/pyenv.git "$LOCAL_PYENV"
fi
export PYENV_ROOT="$LOCAL_PYENV"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$($PYENV_ROOT/bin/pyenv init -)"
if "$PYENV_ROOT/bin/pyenv" versions | grep -q "3.12.3"; then
  echo "Python 3.12.3 installed"
else
  CFLAGS="-O2" "$PYENV_ROOT/bin/pyenv" install 3.12.3
fi
"$PYENV_ROOT/bin/pyenv" local 3.12.3
echo "Local Python installed at $LOCAL_PYENV/versions/3.12.3/bin/python"
