"""
Defines objects and methods for interacting with Kaldi contexts.
"""
__license__ = "Apache License, Version 2.0"

from os import path
from util import KaldiObject
import config
from kaldi import *



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

    *phonesfile* must be a text OpenFST symbol table defining phone symbols.

    *wordsfile* must be a text OpenFST symbol table defining word symbols.

    *lexiconfile* must be a text file mapping words to phone sequences.

    If *addsilence* is True, transitions to silence are added at
    the end of each word with probability given by *silenceprobability*.

    Returns an object representing the L graph.
    """
    return graph.makeLGraph(self.dirname, phonesfile, wordsfile,
      lexiconfile, addsilence, silenceprobability)





  def addL(self, fstfile, phonesfile, wordsfile):
    """
    Adds an existing lexicon FST to the context.

    *fstfile* must be a binary, arc sorted lexicon FST created as described
    at http://kaldi.sourceforge.net/graph_recipe_test.html

    *phonesfile* must be a text OpenFST symbol table defining phone symbols.

    *wordsfile* must be a text OpenFST symbol table defining word symbols.

    Returns an object representing the L graph.
    """
    L = KaldiObject()
    L.filename = fstfile
    L.phonesfile = phonesfile
    L.wordsfile = wordsfile
    return L





  def makeG(self, L, transcripts, interpolateestimates=True,
    ngramorder=3, keepunknowns=True, rmillegalseqences=True,
    limitvocab=False):
    """
    Creates a grammar FST for decoding graph creation.

    Uses SRILM to generate an ngram language model from
    *transcripts* using modified Kneser-Ney discounting.

    *L* must be an object representing the lexicon FST that will be
    composed with this G.

    *transcripts* must be a list of utterance transcripts in Kaldi archive
    text format, with utterance id as key.

    If *interpolateestimates* is True, word estimates will be interpolated
    across *ngram* orders.

    If *keepunknowns* is True, oov words are kept as unknown words in
    the language model.

    If *rmillegalseqences* is True, illegal sequences of sentence start/end
    symbols will be removed from the arpa file.

    If *limitvocab* is True, vocabulary in the LM will be limited
    to the words in L's corresponding words symbol table.

    Returns an object representing the G graph.
    """
    return graph.makeGGraph(self.dirname, L.wordsfile, transcripts,
      interpolateestimates, ngramorder, keepunknowns, rmillegalseqences,
      limitvocab)





  def makeGArpa(self, L, arpafile, rmillegalseqences=True):
    """
    Like makeG but creates an FST using the language model
    from the specified ARPA file instead of creating one.
    """
    return graph.makeGGraphArpa(self.dirname, L.wordsfile, arpafile,
      rmillegalseqences)





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




  def makeHCLG(self, L, G, mdl, contextsize=3, centralposition=1,
    transitionscale=1.0, loopscale=0.1):
    """
    Creates the final decoding graph.

    *L* and *G* must be kaldi objects representing
    those FSTs.

    *mdl* must be the kaldi object representing the
    GMM-based model acoustic model.

    *contextsize* is the size of the phone window for C.

    *centralposition* is the center of the context window for C.

    *transitionscale* specifies the transition scale for
    the H transducer.

    *loopscale* specifies the self loop scale for the
    final graph.

    Returns an object representing the HCLG graph.
    """
    return graph.makeHCLGGraph(self.dirname, L.filename, L.phonesfile,
      G.filename, mdl.filename, mdl.treefile, transitionscale,
      loopscale, contextsize, centralposition)




  def addHCLG(self, fstfile):
    """
    Adds an existing final decoding FST to the context.

    *fstfile* must be a binary, minimized HCLG FST with self loops,
    created as described at http://kaldi.sourceforge.net/graph_recipe_test.html

    Returns an object representing the HCLG graph.
    """
    HCLG = KaldiObject()
    HCLG.filename = fstfile
    return HCLG




  def makeGMM(self):
    """
    Creates a new GMM-based model.

    Returns an object representing the model and tree.
    """
    raise NotImplementedError() 




  def addGMM(self, gmmfile, treefile):
    """
    Adds an existing GMM-based model to the context.

    *gmmfile* must be the GMM model file.

    *treefile* must be a Kaldi decision tree file
    corresponding to the model.

    Returns an object representing the model and tree.
    """
    mdl = KaldiObject()
    mdl.filename = gmmfile
    mdl.treefile = treefile
    return mdl