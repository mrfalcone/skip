"""
Defines methods for interfacing with Kaldi binaries.
"""
__license__ = "Apache License, Version 2.0"

from os import path
from string import split,strip
from shutil import copy2
from collections import deque
from subprocess import Popen,PIPE
from math import log
from util import (KaldiObject, _randFilename, _getCachedObject,
  _cacheObject, _refreshRequired)
import config





def makeLGraph(directory, phonesfile, wordsfile, lexiconfile,
  addsilence, silencephone, silenceprobability):

  Ldir = path.join(directory, "LGraphs")
  (L, idxFile) = _getCachedObject(Ldir, str(locals()))
  
  # check file modification time to see if a refresh is required
  origNames = []
  copyNames = []
  try:
    origNames.append(phonesfile)
    copyNames.append(L.phonesfile)
  except AttributeError:
    copyNames.append(None)
  try:
    origNames.append(wordsfile)
    copyNames.append(L.wordsfile)
  except AttributeError:
    copyNames.append(None)
  try:
    origNames.append(lexiconfile)
    copyNames.append(L.lexiconfile)
  except AttributeError:
    copyNames.append(None)

  if not _refreshRequired(zip(origNames, copyNames)):
    return L



  L = KaldiObject()

  # copy source files
  L.phonesfile = path.join(Ldir, _randFilename("phones-", ".txt"))
  L.wordsfile = path.join(Ldir, _randFilename("words-", ".txt"))
  L.lexiconfile = path.join(Ldir, _randFilename("lexicon-", ".txt"))
  L.filename = path.join(Ldir, _randFilename("L-", ".fst"))

  copy2(phonesfile, L.phonesfile)
  copy2(wordsfile, L.wordsfile)
  copy2(lexiconfile, L.lexiconfile)

  
  # make L and save to the output file
  makeCmd = "{0} --isymbols={1} --osymbols={2} --keep_isymbols=false \
  --keep_osymbols=false".format(config.fstcompile, L.phonesfile, L.wordsfile)

  with open(L.phonesfile, "r") as f:
    for line in f:
      if line.startswith("#0 "):
        phoneWordDisambig = strip(line[line.index(" "):])
        break
  with open(L.wordsfile, "r") as f:
    for line in f:
      if line.startswith("#0 "):
        wordDisambig = strip(line[line.index(" "):])
        break
    makeCmd = "{0} | {1} \"echo {2}|\" \"echo {3}|\"".format(makeCmd,
      config.fstaddselfloops, phoneWordDisambig, wordDisambig)

  makeCmd = "{0} | {1} --sort_type=olabel > \"{2}\"".format(makeCmd,
    config.fstarcsort, L.filename)


  # read lexicon file, create text fst, and pipe to openfst
  # follows recipes from kaldi egs scripts
  logFile = open(path.join(Ldir, _randFilename(suffix=".log")), "w")
  makeProc = Popen(makeCmd, stdin=PIPE, stderr=logFile, shell=True)

  try:
    with open(L.lexiconfile, "r") as lexiconIn:
      if not addsilence:
        loopState = 0
        nextState = 1
      else:
        silCost = -log(silenceprobability);
        noSilCost = -log(1.0 - silenceprobability)
        startState = 0
        loopState = 1
        silenceState = 2
        nextState = 3
        makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(startState, loopState, "<eps>", "<eps>", noSilCost))
        makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(startState, loopState, silencephone, "<eps>", silCost))
        makeProc.stdin.write("{0} {1} {2} {3}\n".format(silenceState, loopState, silencephone, "<eps>"))

      for line in lexiconIn:
        sp = line.index(" ")
        word = strip(line[:sp])
        phones = deque(split(strip(line[sp:])))

        curState = loopState
        while True:
          if len(phones) == 0:
            break
          elif len(phones) == 1:
            phone = phones.popleft()
            if not addsilence or phone == silencephone:
              makeProc.stdin.write("{0} {1} {2} {3}\n".format(curState, loopState, phone, word))
            else:
              makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(curState, loopState, phone, word, noSilCost))
              makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(curState, silenceState, phone, word, silCost))
          else:
            phone = phones.popleft()
            makeProc.stdin.write("{0} {1} {2} {3}\n".format(curState, nextState, phone, word))
            curState = nextState
            nextState += 1
          word = "<eps>"

      makeProc.stdin.write("{0} 0\n".format(loopState))
    makeProc.stdin.close()
    makeProc.wait()

  except:
    makeProc.kill()
    raise
  finally:
    logFile.close()

  return _cacheObject(L, idxFile)


