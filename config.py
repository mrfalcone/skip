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


