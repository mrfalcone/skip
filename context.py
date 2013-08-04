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
    self.dirname = path.join(config.CONTEXTS_DIR, name)






  def makeL(self, phonesfile, wordsfile, lexiconfile, addsilence = True,
    silenceprobability = 0.5):
    """
    Creates a lexicon FST for decoding graph creation.

    *phonesfile* must be a text OpenFST symbol table defining phone symbols

    *wordsfile* must be a text OpenFST symbol table defining word symbols

    *lexiconfile* must be a text file mapping words to phone sequences

    If *addsilence* is True, transitions to silence are added at
    the end of each word with probability given by *silenceprobability*.

    Returns an object representing the L graph.
    """
    return kaldi.makeLGraph(self.dirname, phonesfile, wordsfile,
      lexiconfile, addsilence, silenceprobability)





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





  def makeG(self, L, transcripts, interpolateestimates = True,
    ngramorder=3, keepunknowns = True, rmillegalseqences = True,
    limitvocab = False):
    """
    Creates a grammar FST for decoding graph creation.

    Uses SRILM to generate an ngram language model from
    *transcripts* using modified Kneser-Ney discounting.

    *L* must be an object representing the lexicon FST that will be
    composed with this G

    *transcripts* must be a list of utterance transcripts in Kaldi archive
    text format, with utterance id as key

    Returns an object representing the G graph.
    """
    return kaldi.makeGGraph(self.dirname, L.wordsfile, transcripts,
      interpolateestimates, ngramorder, keepunknowns, rmillegalseqences,
      limitvocab)





  def makeGArpa(self, L, arpafile):
    """
    Creates a grammar FST for decoding graph creation using the
    language model from the specified ARPA file.

    *L* must be an object representing the lexicon FST that will be
    composed with this G

    *arpafile* must be a language model in ARPA text format

    Returns an object representing the G graph.
    """
    raise NotImplementedError()
    return kaldi.makeGGraphArpa()





  def addG(self, fstfile):
    """
    Adds an existing grammar FST to the context.

    *fstfile* must be a binary grammar FST created as described
    at http://kaldi.sourceforge.net/graph_recipe_test.html

    Returns an object representing the G graph.
    """
    G = KaldiObject()
    G.filename = fstfile
    return G









  def makeAcousticModel():
    raise NotImplementedError()


  def addAcousticModel():
    raise NotImplementedError()