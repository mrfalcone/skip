#!/usr/bin/env python
"""
Command line tool to test KaldiContext.
"""
__license__ = "Apache License, Version 2.0"

from time import clock
from context import KaldiContext


def main():
  contextName = "TestContext"
  phonesTableFile = "/usr/skiptest/phones.txt"
  wordsTableFile = "/usr/skiptest/words.txt"
  lexiconFile = "/usr/skiptest/lexicon.txt"
  trainTranscripts = "/usr/skiptest/train_si84/text"
  lmArpa = "/usr/skiptest/bg5k.arpa"

  context = KaldiContext(contextName)

  print "Creating lexicon..."
  t0 = clock()
  L = context.makeL(phonesTableFile, wordsTableFile, lexiconFile)
  print "Done in {0:0.2f} seconds.".format(clock() - t0)
  print


  print "Creating grammar..."
  t0 = clock()
  G = context.makeG(L, trainTranscripts)
  print "Done in {0:0.2f} seconds.".format(clock() - t0)
  print



if __name__ == "__main__":
  main()
