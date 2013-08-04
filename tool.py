#!/usr/bin/env python
"""
Command line tool to test KaldiContext.
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
  lmArpa = "/usr/skiptest/bg5k.arpa"
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

  print "Adding gmm..."
  t0 = time()
  mdl = context.addGMM(mdlFile, treeFile)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Creating decoding graph..."
  t0 = time()
  HCLG = context.makeHCLG(L, G, mdl)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print



if __name__ == "__main__":
  main()
