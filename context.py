"""
Defines objects and methods for interacting with Kaldi contexts.
"""
__license__ = "Apache License, Version 2.0"

import config





class KaldiContext(object):
  """
  A Kaldi context represents an independent application of
  Kaldi on some training and testing data. Each context manages
  its own decoding graphs, intermediate files, features, etc. and
  provides access to Kaldi functions and objects of interest.


  Usage:
      context = KaldiContext.init("exp1")       # created if doesn't exist

      L = context.makeL("exp1_phones.txt",
        "exp1_words.txt", "exp1_lexicon.txt")   # returns immediately if already called

      G = context.makeG(L, "exp1_train/text")   # returns immediately if already called

      ...
  """



  def __init__(self):
    print config.CONTEXTS_DIR
    print config.KALDI_DIR
    print config.SRILM_DIR
