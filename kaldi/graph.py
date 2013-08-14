"""
Defines methods for creating Kaldi decoding graphs.
"""
__license__ = "Apache License, Version 2.0"

from os import path,remove
from string import split,strip
from shutil import copy2,rmtree
from collections import deque
from subprocess import Popen,PIPE
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
        makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(startState, loopState, config.EPS, config.EPS, noSilCost))
        makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(startState, loopState, config.SIL_PHONE, config.EPS, silCost))
        makeProc.stdin.write("{0} {1} {2} {3}\n".format(silenceState, loopState, config.SIL_PHONE, config.EPS))

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
              makeProc.stdin.write("{0} {1} {2} {3}\n".format(curState, loopState, phone, word))
            else:
              makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(curState, loopState, phone, word, noSilCost))
              makeProc.stdin.write("{0} {1} {2} {3} {4}\n".format(curState, silenceState, phone, word, silCost))
          else:
            phone = phones.popleft()
            makeProc.stdin.write("{0} {1} {2} {3}\n".format(curState, nextState, phone, word))
            curState = nextState
            nextState += 1
          word = config.EPS

      makeProc.stdin.write("{0} 0\n".format(loopState))
    makeProc.stdin.close()
    makeProc.wait()
    retCode = makeProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

  except:
    makeProc.kill()
    raise
  finally:
    logFile.close()

  return _cacheObject(L, idxFile)





def makeGGraph(directory, wordsfile, transcripts, interpolateestimates,
  ngramorder, keepunknowns, rmillegalseqences, limitvocab):

  Gdir = path.join(directory, "G_graphs")
  (G, idxFile) = _getCachedObject(Gdir, str(locals()))
  
  
  # check file modification time to see if a refresh is required
  origNames = []
  copyNames = []
  try:
    origNames.append(wordsfile)
    copyNames.append(G.wordsfile)
  except AttributeError:
    copyNames.append(None)
  try:
    origNames.append(transcripts)
    copyNames.append(G.transcripts)
  except AttributeError:
    copyNames.append(None)

  if not _refreshRequired(zip(origNames, copyNames)):
    return G



  # copy source files
  G.wordsfile = path.join(Gdir, _randFilename("words-", ".txt"))
  G.transcripts = path.join(Gdir, _randFilename("trans-", ".ark"))
  G.filename = path.join(Gdir, _randFilename("G-", ".fst"))

  copy2(wordsfile, G.wordsfile)
  copy2(transcripts, G.transcripts)



  # create temp dir for intermediate files
  tmpDir = mkdtemp()
  trainFile = "{0}/train.txt".format(tmpDir)
  vocabFile = "{0}/vocab.txt".format(tmpDir)
  lmFile = "{0}/lm.arpa".format(tmpDir)
  fstFile = "{0}/text.fst".format(tmpDir)


  # prepare commands
  interpStr = ""
  if interpolateestimates:
    interpStr = "-interpolate"
  vocabStr = ""
  if limitvocab:
    vocabStr = "-limit-vocab -vocab {0}".format(vocabFile)
  makeNgramCmd = "{0} -order {1} {2} -kndiscount \
   {3} -text {4} -lm {5}".format(config.ngramcount,
    ngramorder, interpStr, vocabStr, trainFile, lmFile)


  makeFstCmd = "{0} - | {1} - {2}".format(config.arpa2fst,
    config.fstprint, fstFile)

  compileFstCmd = "{0} --isymbols={1} --osymbols={1} \
    --keep_isymbols=false --keep_osymbols=false | \
    {2} > \"{3}\"".format(config.fstcompile,
      wordsfile, config.fstrmepsilon, G.filename)

  # prepare vocab for SRILM
  vocab = {}
  with open(wordsfile, "r") as wordsIn:
    with open(vocabFile, "w") as vocabOut:
      for line in wordsIn:
        word = split(line)[0]
        vocab[word] = True
        vocabOut.write("{0}\n".format(word))

  # prepare training text for SRILM
  with open(transcripts, "r") as textIn:
    with open(trainFile, "w") as trainOut:
      for line in textIn:
        words = split(line)[1:]
        for i in range(len(words)):
          if not words[i] in vocab:
            if keepunknowns:
              words[i] = config.UNKNOWN_WORD
            else:
              words[i] = ""
        trainOut.write("{0}\n".format(" ".join(words)))


   # remove illegal sos and eos sequences
  illegalSeqs = []
  if rmillegalseqences:
    illegalSeqs.append("{0} {1}".format(config.SOS_WORD, config.SOS_WORD))
    illegalSeqs.append("{0} {1}".format(config.EOS_WORD, config.SOS_WORD))
    illegalSeqs.append("{0} {1}".format(config.EOS_WORD, config.EOS_WORD))

  logFile = open(path.join(Gdir, _randFilename(suffix=".log")), "w")

  try:
    # make LM and create text fst from it
    makeLmProc = Popen(makeNgramCmd, stderr=logFile, shell=True)
    makeLmProc.communicate()
    retCode = makeLmProc.poll()
    if retCode:
      raise KaldiError(logFile.name)
    makeFstProc = Popen(makeFstCmd, stdin=PIPE, stderr=logFile, shell=True)

    with open(lmFile, "r") as lmIn:
      for line in lmIn:
        legal = True
        for seq in illegalSeqs:
          if seq in line:
            legal = False
            break
        if legal:
          makeFstProc.stdin.write(line)

    makeFstProc.stdin.close()
    makeFstProc.wait()
    retCode = makeFstProc.poll()
    if retCode:
      raise KaldiError(logFile.name)


    # read text fst, replace symbols, and send to compiler process,
    #  which will output to stdout
    compileFstProc = Popen(compileFstCmd, stdin=PIPE, stderr=logFile, shell=True)

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
        compileFstProc.stdin.write("{0}\n".format(" ".join(parts)))

    compileFstProc.stdin.close()
    compileFstProc.wait()
    retCode = compileFstProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

  finally:
    logFile.close()


  rmtree(tmpDir, True)

  return _cacheObject(G, idxFile)



def makeGGraphArpa(directory, wordsfile, arpafile, rmillegalseqences):

  Gdir = path.join(directory, "G_graphs_arpa")
  (G, idxFile) = _getCachedObject(Gdir, str(locals()))
  
  
  # check file modification time to see if a refresh is required
  origNames = []
  copyNames = []
  try:
    origNames.append(wordsfile)
    copyNames.append(G.wordsfile)
  except AttributeError:
    copyNames.append(None)
  try:
    origNames.append(arpafile)
    copyNames.append(G.arpafile)
  except AttributeError:
    copyNames.append(None)

  if not _refreshRequired(zip(origNames, copyNames)):
    return G



  # copy source files
  G.wordsfile = path.join(Gdir, _randFilename("words-", ".txt"))
  G.arpafile = path.join(Gdir, _randFilename("lm-", ".arpa"))
  G.filename = path.join(Gdir, _randFilename("G-", ".fst"))

  copy2(wordsfile, G.wordsfile)
  copy2(arpafile, G.arpafile)


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
  if rmillegalseqences:
    illegalSeqs.append("{0} {1}".format(config.SOS_WORD, config.SOS_WORD))
    illegalSeqs.append("{0} {1}".format(config.EOS_WORD, config.SOS_WORD))
    illegalSeqs.append("{0} {1}".format(config.EOS_WORD, config.EOS_WORD))


  logFile = open(path.join(Gdir, _randFilename(suffix=".log")), "w")

  try:
    makeFstProc = Popen(makeFstCmd, stdin=PIPE, stderr=logFile, shell=True)

    with open(G.arpafile, "r") as lmIn:
      for line in lmIn:
        legal = True
        for seq in illegalSeqs:
          if seq in line:
            legal = False
            break
        if legal:
          makeFstProc.stdin.write(line)

    makeFstProc.stdin.close()
    makeFstProc.wait()
    retCode = makeFstProc.poll()
    if retCode:
      raise KaldiError(logFile.name)


    # read text fst, replace symbols, and send to compiler process,
    #  which will output to stdout
    compileFstProc = Popen(compileFstCmd, stdin=PIPE, stderr=logFile, shell=True)

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
        compileFstProc.stdin.write("{0}\n".format(" ".join(parts)))

    compileFstProc.stdin.close()
    compileFstProc.wait()
    retCode = compileFstProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

  finally:
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

