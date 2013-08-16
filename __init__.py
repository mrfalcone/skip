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
"""
SAIL Kaldi Interface for Python (SKIP)

Provides a Python interface to Kaldi that manages Kaldi
files and caches results.
"""
__license__ = "Apache License, Version 2.0"
__copyright__ = "Signal Analysis and Interpretation Laboratory, University of Southern California"
__version__ = 0.1
__all__ = ["KaldiContext", "KaldiError"]

from .context import KaldiContext
from .util import KaldiError
