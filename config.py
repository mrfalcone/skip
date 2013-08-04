"""
Configuration file for SKIP. Any variables may be overridden
by creating a file named skipconfig.py in ~/.skip/.
"""
__license__ = "Apache License, Version 2.0"

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


# root directory of SRILM, optional if using existing LMs
try:
  SRILM_DIR = userconf.SRILM_DIR
except AttributeError:
  SRILM_DIR = None

try:
  SRILM_MACHINE = userconf.SRILM_MACHINE
except AttributeError:
  SRILM_MACHINE = "i686-m64"



# kaldi/openfst/srilm binary paths
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
  ngramcount = userconf.ngramcount
except AttributeError:
  ngramcount = "{0}/lm/bin/{1}/ngram-count".format(SRILM_DIR, SRILM_MACHINE)



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
