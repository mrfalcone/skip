"""
Configuration file for SKIP. Any variables may be overridden
by creating a file named skipconfig.py in ~/.skip/.
"""
__license__ = "Apache License, Version 2.0"

from os import sys,environ,path
sys.path.append("{0}/.skip/".format(environ["HOME"]))
try:
  import skipconfig as userconf
except ImportError:
  userconf = object()


# directory where kaldi files and result files will be kept
try:
  CONTEXTS_DIR = userconf.CONTEXTS_DIR
except AttributeError:
  CONTEXTS_DIR = "{0}/contexts".format(path.dirname(__file__))


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

