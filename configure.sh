#!/bin/bash

# Copyright 2013 Signal Analysis and Interpretation Laboratory,
# University of Southern California

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Creates a configuration file for SKIP.

if [ $# -lt 1 ]; then
  echo "Usage: configure.sh <kaldi-dir>"
  exit 1
fi

CONFIG_DIR="$HOME/.skip"
CONFIG_FILE="$CONFIG_DIR/skipconfig.py"
mkdir "$CONFIG_DIR" > /dev/null 2> /dev/null

echo "\"\"\"Auto-generated configuration for SKIP.\"\"\"" > $CONFIG_FILE
echo "KALDI_DIR = \"$1\"" >> $CONFIG_FILE

echo "Wrote config file to $CONFIG_FILE"

