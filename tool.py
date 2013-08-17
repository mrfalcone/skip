#!/usr/bin/env python

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
Command line tool to test KaldiContext operations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from time import time
from context import KaldiContext



def main():

  # parameters to test
  sampleFreq = 16000
  transTest = "/usr/skiptest/test_small/text"
  wavTest = "/usr/skiptest/test_small/wav.scp"
  utt2spkTest = "/usr/skiptest/test_small/utt2spk"
  spk2uttTest = "/usr/skiptest/test_small/spk2utt"
  newLm = "/usr/skiptest/skip/lm_bg5k.arpa"

  # parameters for creating new graphs and models
  newTransTrain = "/usr/skiptest/train_si84/text"
  newPhones = "/usr/skiptest/phones.txt"
  newWords = "/usr/skiptest/words.txt"
  newLexicon = "/usr/skiptest/lexicon.txt"
  newPhonesAlign = "/usr/skiptest/phones_align.txt"
  newWordsAlign = newWords
  newLexiconAlign = "/usr/skiptest/lexicon_align.txt"
  newPhonesDisambig = "/usr/skiptest/phones_disambig.txt"
  newWordsDisambig = newWords
  newLexiconDisambig = "/usr/skiptest/lexicon_disambig.txt"

  # parameters for using existing graphs and models
  exPhones = "/usr/skiptest/existing/phones.txt"
  exWords = "/usr/skiptest/existing/words.txt"
  exLexFst = "/usr/skiptest/existing/L.fst"
  exPhonesAlign = "/usr/skiptest/existing/phones_disambig.txt"
  exWordsAlign = exWords
  exLexFstAlign = "/usr/skiptest/existing/L_align.fst"
  exPhonesDisambig = "/usr/skiptest/existing/phones_disambig.txt"
  exWordsDisambig = exWords
  exLexFstDisambig = "/usr/skiptest/existing/L_disambig.fst"
  exHCLG = "/usr/skiptest/existing/HCLG_mono.fst"
  # exHCLG = "/usr/skiptest/existing/HCLG_tri.fst"
  exMdlFile = "/usr/skiptest/existing/mono.mdl"
  exTreeFile = "/usr/skiptest/existing/mono.tree"
  contextSize = 1
  centerPos = 0
  # exMdlFile = "/usr/skiptest/existing/tri.mdl"
  # exTreeFile = "/usr/skiptest/existing/tri.tree"
  # contextSize = 3
  # centerPos = 1




  # ======= EXISTING CONTEXT TEST ======================================
  context = KaldiContext("ExistingContext")

  print "Adding lexicon FSTs..."
  t0 = time()
  L = context.addL(exLexFst, exPhones, exWords)
  L_align = context.addL(exLexFstAlign, exPhonesAlign, exWordsAlign)
  L_disambig = context.addL(exLexFstDisambig, exPhonesDisambig, exWordsDisambig)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Adding gmm..."
  t0 = time()
  mdl = context.addGMM(exMdlFile, exTreeFile)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Adding decoding graph..."
  t0 = time()
  HCLG = context.addHCLG(exHCLG)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Computing test wave features..."
  t0 = time()
  feats = context.makeFeatures(wavTest, samplefreq=sampleFreq, utt2spk=utt2spkTest, spk2utt=spk2uttTest)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Decoding test wave features..."
  t0 = time()
  hyp = context.decode(feats, HCLG, exWords, mdl, L_align)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  with open(hyp.filename) as f:
    for line in f:
      print line
  with open(hyp.wordlens) as f:
    for line in f:
      print line


  print "Aligning test wave features to test transcripts..."
  t0 = time()
  hyp_ali = context.align(feats, transTest, L, L_align, mdl)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  with open(hyp_ali.wordlens) as f:
    for line in f:
      print line





  # ======= NEW CONTEXT TEST ===========================================
  context = KaldiContext("NewContext")

  print "Creating new lexicon FSTs..."
  t0 = time()
  L = context.makeL(newPhones, newWords, newLexicon)
  L_align = context.makeL(newPhonesAlign, newWordsAlign, newLexiconAlign)
  L_disambig = context.makeL(newPhonesDisambig, newWordsDisambig, newLexiconDisambig)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Creating new grammar..."
  t0 = time()
  #G = context.makeG(newWords, newTransTrain)
  G = context.makeGArpa(newWords, newLm)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Adding existing gmm..."
  t0 = time()
  mdl = context.addGMM(exMdlFile, exTreeFile)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Creating new decoding graph..."
  t0 = time()
  HCLG = context.makeHCLG(L_disambig, G, mdl, contextsize=contextSize, centralposition=centerPos)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Computing test wave features..."
  t0 = time()
  feats = context.makeFeatures(wavTest, samplefreq=sampleFreq, utt2spk=utt2spkTest, spk2utt=spk2uttTest)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  print "Decoding test wave features..."
  t0 = time()
  hyp = context.decode(feats, HCLG, newWords, mdl, L_align)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  with open(hyp.filename) as f:
    for line in f:
      print line
  with open(hyp.wordlens) as f:
    for line in f:
      print line


  print "Aligning test wave features to test transcripts..."
  t0 = time()
  hyp_ali = context.align(feats, transTest, L, L_align, mdl)
  print "Done in {0:0.2f} seconds.".format(time() - t0)
  print

  with open(hyp_ali.wordlens) as f:
    for line in f:
      print line



if __name__ == "__main__":
  main()
