#!/usr/bin/env python
"""
Command line tool to test KaldiContext operations.
"""
__license__ = "Apache License, Version 2.0"

from time import time
from context import KaldiContext


def main():
  contextName = "TestContext"
  phonesTableFile = "/usr/skiptest/phones.txt"
  wordsTableFile = "/usr/skiptest/words.txt"
  lexiconFile = "/usr/skiptest/lexicon.txt"
  trainTranscripts = "/usr/skiptest/train_si84/text"
  testwavscp = "/usr/skiptest/test_small/wav.scp"
  testutt2spk = "/usr/skiptest/test_eval93/utt2spk"
  testspk2utt = "/usr/skiptest/test_eval93/spk2utt"
  
  phonesTableAlignFile = "/usr/skiptest/phones_ali.txt"
  wordsTableAlignFile = "/usr/skiptest/words_ali.txt"
  lexiconAlignFile = "/usr/skiptest/lexicon_ali.txt"

  mdlFile = "/usr/skiptest/final.mdl"
  treeFile = "/usr/skiptest/tree"



  context = KaldiContext(contextName)

  print "Creating lexicon..."
  t0 = time()
  L = context.makeL(phonesTableFile, wordsTableFile, lexiconFile)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Creating grammar..."
  t0 = time()
  G = context.makeG(L, trainTranscripts)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Adding existing gmm..."
  t0 = time()
  mdl = context.addGMM(mdlFile, treeFile)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Creating decoding graph..."
  t0 = time()
  HCLG = context.makeHCLG(L, G, mdl)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Computing wave features..."
  t0 = time()
  feats = context.makeFeats(testwavscp, utt2spk=testutt2spk, spk2utt=testspk2utt)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Creating alignment lexicon..."
  t0 = time()
  Lalign = context.makeL(phonesTableAlignFile, wordsTableAlignFile, lexiconAlignFile)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Decoding features..."
  t0 = time()
  hyp = context.decode(feats, HCLG, L, mdl, Lalign)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print




if __name__ == "__main__":
  main()
