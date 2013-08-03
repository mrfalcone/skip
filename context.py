"""
Defines objects and methods for interacting with Kaldi contexts.
"""
__license__ = "Apache License, Version 2.0"

from os import path
from util import KaldiObject
import config
import kaldi



class KaldiContext(object):
  """
  Represents an independent application of Kaldi on some training
  and testing data. Each context manages its own decoding graphs,
  intermediate files, features, etc. and provides access to Kaldi
  functions and objects of interest.

  Upon initialization, if a Kaldi context has never been initialized,
  a new directory is created in config.CONTEXTS_DIR to store its files.
  Subsequent initializations and function calls with the same parameters
  return cached results.
  """






  def __init__(self, name):
    """
    Initializes a new Kaldi context with the specified name.
    """
    self.dirname = path.join(config.CONTEXTS_DIR, "name")






  def makeL(self, phonesfile, wordsfile, lexiconfile, addsilence = True,
    silencephone = "SIL", silenceprobability = 0.5):
    """
    Creates a lexicon FST for decoding graph creation.

    *phonesfile* must be a text OpenFST symbol table defining phone symbols

    *wordsfile* must be a text OpenFST symbol table defining word symbols

    *lexiconfile* must be a text file mapping words to phone sequences

    If *addsilence* is True, transitions to *silencephone* are added at
    the end of each word with probability given by *silenceprobability*.

    Returns an object representing the L graph.
    """
    return kaldi.makeLGraph(self.dirname, phonesfile, wordsfile,
      lexiconfile, addsilence, silencephone, silenceprobability)





  def addL(self, fstfile, phonesfile, wordsfile):
    """
    Adds an existing lexicon FST to the context.

    *fstfile* must be a binary, arc sorted lexicon FST created as described
    at http://kaldi.sourceforge.net/graph_recipe_test.html

    *phonesfile* must be a text OpenFST symbol table defining phone symbols

    *wordsfile* must be a text OpenFST symbol table defining word symbols

    Returns an object representing the L graph.
    """
    L = KaldiObject()
    L.filename = fstfile
    L.phonesfile = phonesfile
    L.wordsfile = wordsfile
    return L
