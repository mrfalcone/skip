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
Configuration file for SKIP. Any variables may be overridden
by creating a file named skipconfig.py in ~/.skip/.
"""

from os import sys,environ,path
sys.path.append(path.join(environ["HOME"], ".skip"))
try:
  import skipconfig as userconf
except ImportError:
  userconf = object()



# directory where kaldi files and result files will be kept
try:
  CONTEXTS_DIR = userconf.CONTEXTS_DIR
except AttributeError:
  CONTEXTS_DIR = path.join(path.dirname(__file__), "contexts")


# root directory of kaldi e.g. ~/kaldi-trunk
try:
  KALDI_DIR = userconf.KALDI_DIR
except AttributeError:
  KALDI_DIR = None



# binary paths
try:
  OPENFST_DIR = userconf.OPENFST_DIR
except AttributeError:
  OPENFST_DIR = "{0}/tools/openfst".format(KALDI_DIR)
try:
  fstcompile = userconf.fstcompile
except AttributeError:
  fstcompile = "{0}/src/bin/fstcompile".format(OPENFST_DIR)
try:
  fstarcsort = userconf.fstarcsort
except AttributeError:
  fstarcsort = "{0}/src/bin/fstarcsort".format(OPENFST_DIR)
try:
  fstaddselfloops = userconf.fstaddselfloops
except AttributeError:
  fstaddselfloops = "{0}/src/fstbin/fstaddselfloops".format(KALDI_DIR)
try:
  arpa2fst = userconf.arpa2fst
except AttributeError:
  arpa2fst = "{0}/src/bin/arpa2fst".format(KALDI_DIR)
try:
  fstprint = userconf.fstprint
except AttributeError:
  fstprint = "{0}/src/bin/fstprint".format(OPENFST_DIR)
try:
  fstrmepsilon = userconf.fstrmepsilon
except AttributeError:
  fstrmepsilon = "{0}/src/bin/fstrmepsilon".format(OPENFST_DIR)
try:
  makehtransducer = userconf.makehtransducer
except AttributeError:
  makehtransducer = "{0}/src/bin/make-h-transducer".format(KALDI_DIR)
try:
  fsttablecompose = userconf.fsttablecompose
except AttributeError:
  fsttablecompose = "{0}/src/fstbin/fsttablecompose".format(KALDI_DIR)
try:
  fstdeterminizestar = userconf.fstdeterminizestar
except AttributeError:
  fstdeterminizestar = "{0}/src/fstbin/fstdeterminizestar".format(KALDI_DIR)
try:
  fstminimizeencoded = userconf.fstminimizeencoded
except AttributeError:
  fstminimizeencoded = "{0}/src/fstbin/fstminimizeencoded".format(KALDI_DIR)
try:
  fstcomposecontext = userconf.fstcomposecontext
except AttributeError:
  fstcomposecontext = "{0}/src/fstbin/fstcomposecontext".format(KALDI_DIR)
try:
  fstrmsymbols = userconf.fstrmsymbols
except AttributeError:
  fstrmsymbols = "{0}/src/fstbin/fstrmsymbols".format(KALDI_DIR)
try:
  fstrmepslocal = userconf.fstrmepslocal
except AttributeError:
  fstrmepslocal = "{0}/src/fstbin/fstrmepslocal".format(KALDI_DIR)
try:
  addselfloops = userconf.addselfloops
except AttributeError:
  addselfloops = "{0}/src/bin/add-self-loops".format(KALDI_DIR)
try:
  computemfccfeats = userconf.computemfccfeats
except AttributeError:
  computemfccfeats = "{0}/src/featbin/compute-mfcc-feats".format(KALDI_DIR)
try:
  adddeltas = userconf.adddeltas
except AttributeError:
  adddeltas = "{0}/src/featbin/add-deltas".format(KALDI_DIR)
try:
  extractfeaturesegments = userconf.extractfeaturesegments
except AttributeError:
  extractfeaturesegments = "{0}/src/featbin/extract-feature-segments".format(KALDI_DIR)
try:
  computecmvnstats = userconf.computecmvnstats
except AttributeError:
  computecmvnstats = "{0}/src/featbin/compute-cmvn-stats".format(KALDI_DIR)
try:
  applycmvn = userconf.applycmvn
except AttributeError:
  applycmvn = "{0}/src/featbin/apply-cmvn".format(KALDI_DIR)
try:
  gmmdecode = userconf.gmmdecode
except AttributeError:
  gmmdecode = "{0}/src/gmmbin/gmm-decode-faster".format(KALDI_DIR)
try:
  gmmalign = userconf.gmmalign
except AttributeError:
  gmmalign = "{0}/src/gmmbin/gmm-align".format(KALDI_DIR)
try:
  alitophones = userconf.alitophones
except AttributeError:
  alitophones = "{0}/src/bin/ali-to-phones".format(KALDI_DIR)
try:
  phonestoprons = userconf.phonestoprons
except AttributeError:
  phonestoprons = "{0}/src/bin/phones-to-prons".format(KALDI_DIR)
try:
  pronstowordali = userconf.pronstowordali
except AttributeError:
  pronstowordali = "{0}/src/bin/prons-to-wordali".format(KALDI_DIR)




# symbol configurations
try:
  SIL_PHONE = userconf.SIL_PHONE
except AttributeError:
  SIL_PHONE = "SIL"
try:
  EPS = userconf.EPS
except AttributeError:
  EPS = "<eps>"
try:
  UNKNOWN_WORD = userconf.UNKNOWN_WORD
except AttributeError:
  UNKNOWN_WORD = "<UNK>"
try:
  SOS_WORD = userconf.SOS_WORD
except AttributeError:
  SOS_WORD = "<s>"
try:
  EOS_WORD = userconf.EOS_WORD
except AttributeError:
  EOS_WORD = "</s>"
try:
  EPS_G = userconf.EPS_G
except AttributeError:
  EPS_G = "#0"
try:
  WORD_BOUND_L = userconf.WORD_BOUND_L
except AttributeError:
  WORD_BOUND_L = "#1"
try:
  WORD_BOUND_R = userconf.WORD_BOUND_R
except AttributeError:
  WORD_BOUND_R = "#2"
try:
  DECODE_OOV_WORD = userconf.DECODE_OOV_WORD
except AttributeError:
  DECODE_OOV_WORD = "<SPOKEN_NOISE>"
try:
  DECODE_OOV_PHONE = userconf.DECODE_OOV_PHONE
except AttributeError:
  DECODE_OOV_PHONE = "SPN"


