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
  computecmvnstats = userconf.computecmvnstats
except AttributeError:
  computecmvnstats = "{0}/src/featbin/compute-cmvn-stats".format(KALDI_DIR)
try:
  applycmvn = userconf.applycmvn
except AttributeError:
  applycmvn = "{0}/src/featbin/apply-cmvn".format(KALDI_DIR)




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
