#!/bin/bash
# Creates a configuration file for SKIP.

if [ $# -lt 1 ]; then
  echo "Usage: configure.sh <kaldi-dir> [srilm-dir]"
  exit 1
fi

CONFIG_DIR="$HOME/.skip"
CONFIG_FILE="$CONFIG_DIR/skipconfig.py"
mkdir "$CONFIG_DIR" > /dev/null 2> /dev/null

echo "\"\"\"Auto-generated configuration for SKIP.\"\"\"" > $CONFIG_FILE
echo "KALDI_DIR = \"$1\"" >> $CONFIG_FILE

if [ ! -z "$2" ]; then
  echo "SRILM_DIR = \"$2\"" >> $CONFIG_FILE
fi

echo "Wrote config file to $CONFIG_FILE"

