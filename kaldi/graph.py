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
Defines methods for creating Kaldi decoding graphs.
"""

from os import path,remove
from string import split,strip
from shutil import copy2,rmtree
from collections import deque
from subprocess import Popen
from math import log
from tempfile import mkdtemp,NamedTemporaryFile 

from skip.util import (KaldiObject, _randFilename, _getCachedObject,
  _cacheObject, _refreshRequired, KaldiError)
import skip.config as config





def makeLGraph(directory, phonesfile, wordsfile, lexiconfile,
  addsilence, silenceprobability):

  Ldir = path.join(directory, "L_graphs")
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



  # copy source files
  L.phonesfile = path.join(Ldir, _randFilename("phones-", ".txt"))
  L.wordsfile = path.join(Ldir, _randFilename("words-", ".txt"))
  L.lexiconfile = path.join(Ldir, _randFilename("lexicon-", ".txt"))
  L.filename = path.join(Ldir, _randFilename("L-", ".fst"))

  copy2(phonesfile, L.phonesfile)
  copy2(wordsfile, L.wordsfile)
  copy2(lexiconfile, L.lexiconfile)
  
  # prepare make L command
  makeCmd = "{0} --isymbols={1} --osymbols={2} --keep_isymbols=false \
  --keep_osymbols=false".format(config.fstcompile, L.phonesfile, L.wordsfile)

  with open(L.phonesfile, "r") as f:
    for line in f:
      if line.startswith("{0} ".format(config.EPS_G)):
        phoneWordDisambig = strip(line[line.index(" "):])
        break
  with open(L.wordsfile, "r") as f:
    for line in f:
      if line.startswith("{0} ".format(config.EPS_G)):
        wordDisambig = strip(line[line.index(" "):])
        break
    makeCmd = "{0} | {1} \"echo {2}|\" \"echo {3}|\"".format(makeCmd,
      config.fstaddselfloops, phoneWordDisambig, wordDisambig)

  makeCmd = "{0} | {1} --sort_type=olabel > \"{2}\"".format(makeCmd,
    config.fstarcsort, L.filename)


  # read lexicon file, create text fst, and pipe to openfst
  # follows recipes from kaldi egs scripts
  lexiconOut = NamedTemporaryFile(mode="w+", suffix=".txt")
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
      lexiconOut.write("{0} {1} {2} {3} {4}\n".format(startState, loopState, config.EPS, config.EPS, noSilCost))
      lexiconOut.write("{0} {1} {2} {3} {4}\n".format(startState, loopState, config.SIL_PHONE, config.EPS, silCost))
      lexiconOut.write("{0} {1} {2} {3}\n".format(silenceState, loopState, config.SIL_PHONE, config.EPS))

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
          if not addsilence or phone == config.SIL_PHONE:
            lexiconOut.write("{0} {1} {2} {3}\n".format(curState, loopState, phone, word))
          else:
            lexiconOut.write("{0} {1} {2} {3} {4}\n".format(curState, loopState, phone, word, noSilCost))
            lexiconOut.write("{0} {1} {2} {3} {4}\n".format(curState, silenceState, phone, word, silCost))
        else:
          phone = phones.popleft()
          lexiconOut.write("{0} {1} {2} {3}\n".format(curState, nextState, phone, word))
          curState = nextState
          nextState += 1
        word = config.EPS

    lexiconOut.write("{0} 0\n".format(loopState))

  try:
    logFile = open(path.join(Ldir, _randFilename(suffix=".log")), "w")
    lexiconOut.seek(0)
    makeProc = Popen(makeCmd, stdin=lexiconOut, stderr=logFile, shell=True)
    makeProc.communicate()
    retCode = makeProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

  finally:
    lexiconOut.close()
    logFile.close()

  return _cacheObject(L, idxFile)






def makeGGraph(directory, wordsfile, arpafile):

  Gdir = path.join(directory, "G_graphs")
  (G, idxFile) = _getCachedObject(Gdir, str(locals()))
  
  
  # check file modification time to see if a refresh is required
  refreshRequired = False
  try:
    if int(path.getmtime(arpafile)) > G.arpafile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True

  try:
    refreshRequired = (refreshRequired and 
      _refreshRequired((wordsfile, G.wordsfile)))
  except AttributeError:
    refreshRequired = True

  if not refreshRequired:
    return G


  G.wordsfile = path.join(Gdir, _randFilename("words-", ".txt"))
  G.filename = path.join(Gdir, _randFilename("G-", ".fst"))

  copy2(wordsfile, G.wordsfile)
  G.arpafile_time = int(path.getmtime(arpafile))


  tmp = NamedTemporaryFile(suffix=".txt", delete=False)
  fstFile = tmp.name
  tmp.close()
  makeFstCmd = "{0} - | {1} - \"{2}\"".format(config.arpa2fst,
    config.fstprint, fstFile)

  compileFstCmd = "{0} --isymbols={1} --osymbols={1} \
    --keep_isymbols=false --keep_osymbols=false | \
    {2} > \"{3}\"".format(config.fstcompile,
      wordsfile, config.fstrmepsilon, G.filename)


  # remove illegal sos and eos sequences
  illegalSeqs = []
  illegalSeqs.append("{0} {1}".format(config.SOS_WORD, config.SOS_WORD))
  illegalSeqs.append("{0} {1}".format(config.EOS_WORD, config.SOS_WORD))
  illegalSeqs.append("{0} {1}".format(config.EOS_WORD, config.EOS_WORD))


  logFile = open(path.join(Gdir, _randFilename(suffix=".log")), "w")
  fstInputFile = NamedTemporaryFile(mode="w+", suffix=".txt")
  fstTextFile = NamedTemporaryFile(mode="w+", suffix=".txt")

  try:
    validWords = {}
    with open(G.wordsfile, "r") as wordsIn:
      for line in wordsIn:
        if strip(line):
          word = split(line)[0]
          validWords[word] = True

    with open(arpafile, "r") as lmIn:
      for line in lmIn:
        legal = True

        # discard illegal sequences and lines without valid words
        lineParts = split(line)
        if len(lineParts) > 1:
          try:
            float(lineParts[0])
            for seq in illegalSeqs:
              if seq in line:
                legal = False
                break

            for w in lineParts[1:]:
              try:
                float(w)
              except ValueError:
                if not w in validWords:
                  legal = False
                  break
          except ValueError:
            legal = True

        if legal:
          fstInputFile.write(line)


    fstInputFile.seek(0)
    makeFstProc = Popen(makeFstCmd, stdin=fstInputFile, stderr=logFile, shell=True)
    makeFstProc.communicate()
    retCode = makeFstProc.poll()
    if retCode:
      raise KaldiError(logFile.name)


    # read text fst, replace symbols, and send to compiler process
    with open(fstFile, "r") as fstIn:
      for line in fstIn:
        parts = split(line)
        if len(parts) >= 4:
          if parts[2] == config.EPS:
            parts[2] = config.EPS_G
          elif parts[2] == config.SOS_WORD or parts[2] == config.EOS_WORD:
            parts[2] = config.EPS
          if parts[3] == config.SOS_WORD or parts[3] == config.EOS_WORD:
            parts[3] = config.EPS
        fstTextFile.write("{0}\n".format(" ".join(parts)))

    fstTextFile.seek(0)
    compileFstProc = Popen(compileFstCmd, stdin=fstTextFile, stderr=logFile, shell=True)
    compileFstProc.communicate()
    retCode = compileFstProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

  finally:
    fstInputFile.close()
    fstTextFile.close()
    logFile.close()

  remove(fstFile)

  return _cacheObject(G, idxFile)






def makeHCLGGraph(directory, lexfst, phonesfile,
  grammarfst, mdlfile, treefile, transitionscale,
  loopscale, contextsize, centralposition):

  HCLGdir = path.join(directory, "HCLG_graphs")
  (HCLG, idxFile) = _getCachedObject(HCLGdir, str(locals()))
  

  # check file modification times instead of copying like for other graphs
  refreshRequired = False
  try:
    if int(path.getmtime(lexfst)) > HCLG.lexfst_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(phonesfile)) > HCLG.phonesfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(grammarfst)) > HCLG.grammarfst_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(treefile)) > HCLG.treefile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(mdlfile)) > HCLG.mdlfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True


  if not refreshRequired:
    return HCLG


  # remove old files
  try:
    remove(HCLG.filename)
  except (OSError, AttributeError):
    pass


  HCLG.lexfst_time = int(path.getmtime(lexfst))
  HCLG.phonesfile_time = int(path.getmtime(phonesfile))
  HCLG.grammarfst_time = int(path.getmtime(grammarfst))
  HCLG.treefile_time = int(path.getmtime(treefile))
  HCLG.mdlfile_time = int(path.getmtime(mdlfile))
  HCLG.filename = path.join(HCLGdir, _randFilename("HCLG-", ".fst"))


  # create directory for temp files
  tmpDir = mkdtemp()
  disambigSymFile = "{0}/disambig.sym".format(tmpDir)
  ilabelRemapFile = "{0}/ilabel.remap".format(tmpDir)
  disambigTidFile = "{0}/disambig.tid".format(tmpDir)
  clgOutFile = "{0}/CLG.fst".format(tmpDir)
  haOutFile = "{0}/Ha.fst".format(tmpDir)


  # read disambig phone symbols
  with open(phonesfile, "r") as phonesIn:
    with open(disambigSymFile, "w") as disambigSymbolsOut:
      for line in phonesIn:
        if line.startswith("#"):
          try:
            int(line[1:line.index(" ")])
            disambigSymbolsOut.write("{0}\n".format(line[line.index(" ")+1:]))
          except ValueError:
            continue



  # prepare graph creation commands
  makeClgCmd = "{0} {1} {2} | {3} --use-log=true | {4} | {5} --context-size={6} \
    --central-position={7} --read-disambig-syms={8} {9} > {10}".format(config.fsttablecompose, lexfst,
      grammarfst, config.fstdeterminizestar, config.fstminimizeencoded, config.fstcomposecontext,
      contextsize, centralposition, disambigSymFile, ilabelRemapFile, clgOutFile)

  makeHaCmd = "{0} --disambig-syms-out={1} --transition-scale={2} {3} \
    {4} {5} > {6}".format(config.makehtransducer, disambigTidFile,
      transitionscale, ilabelRemapFile, treefile, mdlfile, haOutFile)

  makeHclgCmd = "{0} {1} {2} | {3} --use-log=true | {4} {5} | {6} | \
    {7} | {8} --self-loop-scale={9} --reorder=true {10} > {11}".format(config.fsttablecompose,
      haOutFile, clgOutFile, config.fstdeterminizestar, config.fstrmsymbols, disambigTidFile,
      config.fstrmepslocal, config.fstminimizeencoded, config.addselfloops,
      loopscale, mdlfile, HCLG.filename)


  logFile = open(path.join(HCLGdir, _randFilename(suffix=".log")), "w")

  try:
    mkGraphProc = Popen(makeClgCmd, stderr=logFile, shell=True)
    mkGraphProc.communicate()
    retCode = mkGraphProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

    mkGraphProc = Popen(makeHaCmd, stderr=logFile, shell=True)
    mkGraphProc.communicate()
    retCode = mkGraphProc.poll()
    if retCode:
      raise KaldiError(logFile.name)
    
    mkGraphProc = Popen(makeHclgCmd, stderr=logFile, shell=True)
    mkGraphProc.communicate()
    retCode = mkGraphProc.poll()
    if retCode:
      raise KaldiError(logFile.name)
    
  finally:
    logFile.close()

  rmtree(tmpDir, True)
  

  return _cacheObject(HCLG, idxFile)

