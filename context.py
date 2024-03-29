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
Defines objects and methods for interacting with Kaldi contexts.
"""

from os import path,remove,walk
from shutil import rmtree

from util import KaldiObject
from config import ConfigObject
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


  def __init__(self, name, kaldiDir, userConfig=None):
    """
    Initializes a new Kaldi context with the name given
    by *name*. Uses the Kaldi installation specified by
    *kaldiDir*. If *userConfig* is not None, it must be
    a dictionary object specifying config key/value
    pairs to override.
    """
    self.config = ConfigObject(kaldiDir, userConfig)
    self.dirname = path.join(self.config.CONTEXTS_DIR, name)
    



  def destroy(self):
    """
    Removes the directory associated with the context and
    destroys all its files.
    """
    try:
      rmtree(self.dirname)
    except OSError:
      pass



  def rmlogs(self):
    """
    Deletes all log files associated with the context.
    """
    try:
      logs = []
      for (dirpath, dirnames, filenames) in walk(self.dirname):
        for f in filenames:
          if f.endswith(".log"):
            logs.append(f)
      for f in logs:
        remove(f)
    except OSError:
      pass




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
    return graph.makeLGraph(self.dirname, self.config, phonesfile, wordsfile,
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



  def makeGText(self, wordsfile, fstfile, arcsort=False):
    """
    Creates a grammar FST for decoding graph creation from the
    specified text FST.

    *wordsfile* is the words symbol table used to create the grammar.

    *fstfile* must be the FST file, in AT&T FST format.

    If *arcsort* is True, arcs will be sorted by output label.

    Returns an object representing the G graph.
    """
    return graph.makeGGraphTextFst(self.dirname, self.config, wordsfile,
        fstfile, arcsort)




  def makeGArpa(self, wordsfile, arpafile, arcsort=False):
    """
    Creates a grammar FST for decoding graph creation from the
    specified ARPA model. Discards illegal word sequences and
    oov words.

    *wordsfile* is the words symbol table used to create the grammar.

    *arpafile* must be the ARPA LM file from which to create the
    grammar FST.

    If *arcsort* is True, arcs will be sorted by output label.

    Returns an object representing the G graph.
    """
    return graph.makeGGraphArpa(self.dirname, self.config, wordsfile,
        arpafile, arcsort)





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
    Creates the HCLG graph for decoding.

    *L* and *G* must be kaldi objects representing the FSTs
    used to create HCLG. *L* should have disambiguation symbols.

    *mdl* must be the kaldi object representing the
    GMM-based acoustic model.

    *contextsize* is the size of the phone window for C.

    *centralposition* is the center of the context window for C.

    *transitionscale* specifies the transition scale for
    the H transducer.

    *loopscale* specifies the self loop scale for the
    final graph.

    Returns an object representing the HCLG graph.
    """
    return graph.makeHCLGGraph(self.dirname, self.config, L.filename, L.phonesfile,
      G.filename, mdl.filename, mdl.treefile, transitionscale,
      loopscale, contextsize, centralposition)




  def addHCLG(self, fstfile):
    """
    Adds an existing HCLG graph to the context for decoding.

    *fstfile* must be a binary, minimized HCLG FST with self loops,
    created as described at http://kaldi.sourceforge.net/graph_recipe_test.html

    Returns an object representing the HCLG graph.
    """
    HCLG = KaldiObject()
    HCLG.filename = fstfile
    return HCLG



  def composeGraphs(self, A, B):
    """
    Composes the FST represented by the KaldiObject *A*
    with the FST represented by the KaldiObject *B*.

    Returns A o B
    """
    return graph.composeGraphs(self.dirname, self.config, A.filename, B.filename)




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





  def makeFeatures(self, wavscp, segmentsfile=None, samplefreq=16000,
    feattype="mfcc", useenergy=False, framelength=25,
    frameshift=10, numceps=13, applycmvn=True,
    normvars=False, utt2spk=None, spk2utt=None, deltaorder=2):
    """
    Creates features for the wave files specified by *wavscp*.

    If *segmentsfile* is specified, audio is first segmented
    before computing features.

    If *feattype* is "mfcc", *useenergy* specifies whether to
    use energy (else C0) to compute mfccs.

    *framelength*, *frameshift*, and *numceps* are the frame length
    and shift in milliseconds and the number of coefficients to
    compute, respectively.

    If *applycmvn* is True, cepstral mean normalization will
    be applied, per-utterance by default or per-speaker if
    *utt2spk* and *spk2utt* specify files in ark text format
    mapping utterance ids to speaker ids and speaker ids to
    utterance ids respectively. If *normvars* is True, cepstral
    variance normalization will also be applied.

    *deltaorder* specifies the order of delta computation
    if greater than zero.

    Returns an object representing the features.
    """
    if feattype == "mfcc":
      return feat.makeMfccFeats(self.dirname, self.config, wavscp, segmentsfile,
        samplefreq, useenergy, framelength, frameshift, numceps, applycmvn,
        normvars, utt2spk, spk2utt, deltaorder)

    elif feattype == "plp":
      raise NotImplementedError() 

    else:
      raise ValueError("Unsupported value: {0}.".format(feattype))





  def addFeatures(self, featsfile):
    """
    Adds existing features to the context.

    *featsfile* must be a Kaldi archive file specifying
    the features to add.

    Returns an object representing the features.
    """
    feats = KaldiObject()
    feats.filename = featsfile 
    return feats





  def segmentFeatures(self, feats, segfile, framerate=100.0):
    """
    Segments the specified *feats* object according to the
    specified *segfile*. *segfile* must be formatted as follows:
    out-utt-id in-utt-id start_time end_time

    *framerate* specifies the feature sampling rate.

    Returns an object representing the feature segments.
    """
    return feat.segmentFeats(self.dirname, self.config, feats.filename,
      segfile, framerate)



  def decodeNbest(self, n, feats, HCLG, wordsfile, lexiconfile, mdl, 
    Lalign=None, beam=16, allowpartial=False, acousticscale=0.1, mbr=False):
    """
    Decodes the features corresponding to the specified
    features object *feats* and returns the *n* best
    hypotheses.

    *HCLG* is the object representing the decoding graph
    to use. *wordsfile* must be the symbol table with the
    words to decode. *lexiconfile* must be a text file
    with lines formatted like: word-in word-out phone-sequence
    with words and phones specified as integer IDs.

    *mdl* must be the kaldi object representing the
    GMM-based acoustic model.

    If *Lalign* is specified, it must be a lexicon FST
    object created with alignment symbols. This will
    cause word and phone lengths to be computed.

    The parameters *beam*, *allowpartial*, and *acousticscale*
    are passed to Kaldi's lattice generator.

    If *mbr* is True, Minimum Bayes Risk decoding is performed
    on the lattice as well.

    Returns an object representing up to *n* best hypothesis
    transcriptions and/or alignments generated by Kaldi.
    """
    phonesfilealign = None
    lexfstalign = None

    if Lalign:
      phonesfilealign = Lalign.phonesfile
      lexfstalign = Lalign.filename

    return gmmdecode.decodeNbestFeats(self.dirname, self.config, n, feats.filename,
      HCLG.filename, wordsfile, lexiconfile, mdl.filename, mdl.treefile,
      phonesfilealign, lexfstalign, beam, allowpartial, acousticscale, mbr)




  def decode(self, feats, HCLG, wordsfile, mdl, Lalign=None, beam=16,
    allowpartial=True, acousticscale=0.1):
    """
    Decodes the features corresponding to the specified
    features object *feats*.

    *HCLG* is the object representing the decoding graph
    to use. *wordsfile* must be the symbol table with the
    words to decode.

    *mdl* must be the kaldi object representing the
    GMM-based acoustic model.

    If *Lalign* is specified, it must be a lexicon FST
    object created with alignment symbols. This will
    cause word and phone lengths to be computed.

    The parameters *beam*, *allowpartial*, and *acousticscale*
    are passed to Kaldi's decoder

    Returns an object representing the hypothesis transcriptions
    and/or alignments generated by Kaldi.
    """
    phonesfilealign = None
    lexfstalign = None

    if Lalign:
      phonesfilealign = Lalign.phonesfile
      lexfstalign = Lalign.filename

    return gmmdecode.decodeFeats(self.dirname, self.config, feats.filename,
      HCLG.filename, wordsfile, mdl.filename, mdl.treefile,
      phonesfilealign, lexfstalign, beam, allowpartial, acousticscale)



  def align(self, feats, transfile, L, Lalign, mdl, beam=200, retrybeam=0,
    acousticscale=1.0, selfloopscale=1.0, transitionscale=1.0):
    """
    Aligns the features corresponding to the specified
    features object *feats* to the transcripts specified
    by *transfile*.

    *L* must be a lexicon FST object created without disambiguation
    or alignment symbols and *Lalign* must be a lexicon FST with alignment
    but without disambiguation symbols.

    *mdl* must be the kaldi object representing the
    GMM-based acoustic model.

    The parameters *beam*, *retrybeam*, *acousticscale*, *selfloopscale*,
    and *transitionscale*, are passed to Kaldi's aligner

    Returns an object representing the hypothesis alignments
    generated by Kaldi.
    """
    return gmmdecode.alignFeats(self.dirname, self.config, feats.filename,
      transfile, L.wordsfile, L.filename, Lalign.phonesfile, Lalign.filename,
      mdl.filename, mdl.treefile, beam, retrybeam, acousticscale,
      selfloopscale, transitionscale)

