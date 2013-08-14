"""
Defines methods for decoding and aligning with GMM-based models.
"""
__license__ = "Apache License, Version 2.0"

from os import path,remove
from subprocess import Popen,PIPE
from string import split,strip
from tempfile import NamedTemporaryFile
from shutil import copy2

from skip.util import (KaldiObject, _randFilename, _getCachedObject,
  _cacheObject, _refreshRequired, KaldiError)
import skip.config as config






def _align(logFile, mdlfile, intfilename, lexfstalign,
  alignFile, intphonelens, phonelens, intwordlens, wordlens,
  phoneSymbols, wordSymbols, wordLeftSym, wordRightSym):

 
  makePhonelensCmd = "{0} --write-lengths=true {1} \"ark:{2}\" \
    ark,t:-".format(config.alitophones, mdlfile, alignFile)


  # align phones and translate to text
  makePhonelensProc = Popen(makePhonelensCmd, stdout=PIPE,
    stderr=logFile, shell=True)

  with open(intphonelens, "w") as lensIntOut:
    with open(phonelens, "w") as lensOut:
      for line in makePhonelensProc.stdout:
        sp = line.index(" ")
        uttId = line[:sp]
        pairsStr = []
        for pair in line[sp+1:].split(";"):
          parts = split(pair)
          try:
            sym = phoneSymbols[parts[0]]
          except KeyError:
            sym = config.DECODE_OOV_PHONE
          pairsStr.append("{0} {1}".format(sym, parts[1]))

        lensIntOut.write(line)
        lensOut.write("{0} {1}\n".format(uttId, " ; ".join(pairsStr)))
  makePhonelensProc.stdout.close()
  makePhonelensProc.wait()
  retCode = makePhonelensProc.poll()
  if retCode:
    raise KaldiError(logFile.name)


  makeWordlensCmd = "{0} \"{1}\" \"ark:{2}\" ark:- | {3} \"{4}\" \
    {5} {6} ark:- \"ark,t:{7}\" ark:- | {8} ark:- \"ark,t:{9}\" \
    ark,t:-".format(config.alitophones, mdlfile, alignFile,
      config.phonestoprons, lexfstalign, wordLeftSym, wordRightSym,
      intfilename, config.pronstowordali, intphonelens)


  # align words and translate to text
  makeWordlensProc = Popen(makeWordlensCmd, stdout=PIPE,
    stderr=logFile, shell=True)

  with open(intwordlens, "w") as lensIntOut:
    with open(wordlens, "w") as lensOut:
      for line in makeWordlensProc.stdout:
        sp = line.index(" ")
        uttId = line[:sp]
        pairsStr = []
        for pair in line[sp+1:].split(";"):
          parts = split(pair)
          try:
            sym = wordSymbols[parts[0]]
          except KeyError:
            sym = config.DECODE_OOV_WORD
          pairsStr.append("{0} {1}".format(sym, parts[1]))

        lensIntOut.write(line)
        lensOut.write("{0} {1}\n".format(uttId, " ; ".join(pairsStr)))
  makeWordlensProc.stdout.close()
  makeWordlensProc.wait()
  retCode = makeWordlensProc.poll()
  if retCode:
    raise KaldiError(logFile.name)




def decodeFeats(directory, featsfile, graphfile, wordsfile, mdlfile,
  treefile, phonesfilealign, lexfstalign, beam, allowpartial, acousticscale):

  hypdir = path.join(directory, "hypotheses")
  (hyp, idxFile) = _getCachedObject(hypdir, str(locals()))
  

  # check file modification times to see if refresh is required
  refreshRequired = False
  try:
    if int(path.getmtime(featsfile)) > hyp.featsfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(graphfile)) > hyp.graphfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(wordsfile)) > hyp.wordsfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(mdlfile)) > hyp.mdlfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(treefile)) > hyp.treefile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True

  if phonesfilealign and lexfstalign:
    try:
      if int(path.getmtime(phonesfilealign)) > hyp.phonesfilealign_time:
        refreshRequired = True
    except AttributeError:
      refreshRequired = True
    try:
      if int(path.getmtime(lexfstalign)) > hyp.lexfstalign_time:
        refreshRequired = True
    except AttributeError:
      refreshRequired = True

  if not refreshRequired:
    return hyp


  # remove old files
  try:
    remove(hyp.filename)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.intfilename)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.wordlens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.intwordlens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.phonelens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.intphonelens)
  except (OSError, AttributeError):
    pass


  hyp.featsfile_time = int(path.getmtime(featsfile))
  hyp.graphfile_time = int(path.getmtime(graphfile))
  hyp.wordsfile_time = int(path.getmtime(wordsfile))
  hyp.mdlfile_time = int(path.getmtime(mdlfile))
  hyp.treefile_time = int(path.getmtime(treefile))
  if phonesfilealign and lexfstalign:
    hyp.phonesfilealign_time = int(path.getmtime(phonesfilealign))
    hyp.lexfstalign_time = int(path.getmtime(lexfstalign))
  
  

  hyp.filename = path.join(hypdir, _randFilename("hyp-", ".txt"))
  hyp.intfilename = path.join(hypdir, _randFilename("hyp-", ".int"))
  if phonesfilealign and lexfstalign:
    hyp.wordlens = path.join(hypdir, _randFilename("wordlens-", ".txt"))
    hyp.intwordlens = path.join(hypdir, _randFilename("wordlens-", ".int"))
    hyp.phonelens = path.join(hypdir, _randFilename("phonelens-", ".txt"))
    hyp.intphonelens = path.join(hypdir, _randFilename("phonelens-", ".int"))


  # prepare decode command
  tmp = NamedTemporaryFile(suffix=".ark", delete=False)
  alignFile = tmp.name
  tmp.close()

  decodeCmd = "{0} --beam={1} --allow-partial={2} --acoustic-scale={3} \
    {4} {5} \"ark:{6}\" \"ark,t:-\" \"ark:{7}\"".format(config.gmmdecode,
    beam, str(allowpartial).lower(), acousticscale, mdlfile,
    graphfile, featsfile, alignFile)


  logFile = open(path.join(hypdir, _randFilename(suffix=".log")), "w")

  try:
    # read word/phone symbol tables
    wordSymbols = {}
    with open(wordsfile, "r") as symTableIn:
      for line in symTableIn:
        parts = split(line)
        wordSymbols[parts[1]] = parts[0]

    phoneSymbols = {}
    with open(phonesfilealign, "r") as symTableIn:
      for line in symTableIn:
        parts = split(line)
        phoneSymbols[parts[1]] = parts[0]
        if parts[0] == config.WORD_BOUND_L:
          wordLeftSym = parts[1]
        elif parts[0] == config.WORD_BOUND_R:
          wordRightSym = parts[1]


    # decode hypothesis transcripts and translate to text
    decodeProc = Popen(decodeCmd, stdout=PIPE, stderr=logFile, shell=True)
    with open(hyp.intfilename, "w") as hypIntOut:
      with open(hyp.filename, "w") as hypOut:
        for line in decodeProc.stdout:
          parts = split(line)
          uttId = parts[0]
          words = parts[1:]
          for i in range(len(words)):
            try:
              words[i] = wordSymbols[words[i]]
            except KeyError:
              words[i] = config.DECODE_OOV_WORD
          hypIntOut.write(line)
          hypOut.write("{0} {1}\n".format(uttId, " ".join(words)))
    decodeProc.stdout.close()
    decodeProc.wait()
    retCode = decodeProc.poll()
    if retCode:
      raise KaldiError(logFile.name)


    # if alignment symbols were given, compute word and phone lengths
    if phonesfilealign and lexfstalign:
      _align(logFile, mdlfile, hyp.intfilename, lexfstalign,
        alignFile, hyp.intphonelens, hyp.phonelens, hyp.intwordlens,
        hyp.wordlens, phoneSymbols, wordSymbols, wordLeftSym, wordRightSym)


  finally:
    logFile.close()


  remove(alignFile)


  return _cacheObject(hyp, idxFile)





def alignFeats(directory, featsfile, transfile, wordsfile, lexfst,
  phonesfilealign, lexfstalign, mdlfile, treefile, beam,
  retrybeam, acousticscale, selfloopscale, transitionscale):

  hypdir = path.join(directory, "align_hypotheses")
  (hyp, idxFile) = _getCachedObject(hypdir, str(locals()))
  

  # check file modification times to see if refresh is required
  refreshRequired = False
  try:
    if int(path.getmtime(featsfile)) > hyp.featsfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(transfile)) > hyp.transfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(wordsfile)) > hyp.wordsfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(mdlfile)) > hyp.mdlfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(treefile)) > hyp.treefile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(phonesfilealign)) > hyp.phonesfilealign_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(lexfst)) > hyp.lexfst_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(lexfstalign)) > hyp.lexfstalign_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True

  if not refreshRequired:
    return hyp


  # remove old files
  try:
    remove(hyp.filename)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.intfilename)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.wordlens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.intwordlens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.phonelens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hyp.intphonelens)
  except (OSError, AttributeError):
    pass


  hyp.featsfile_time = int(path.getmtime(featsfile))
  hyp.transfile_time = int(path.getmtime(transfile))
  hyp.wordsfile_time = int(path.getmtime(wordsfile))
  hyp.mdlfile_time = int(path.getmtime(mdlfile))
  hyp.treefile_time = int(path.getmtime(treefile))
  hyp.phonesfilealign_time = int(path.getmtime(phonesfilealign))
  hyp.lexfst_time = int(path.getmtime(lexfst))
  hyp.lexfstalign_time = int(path.getmtime(lexfstalign))
  
  

  hyp.filename = path.join(hypdir, _randFilename("trans-", ".txt"))
  hyp.intfilename = path.join(hypdir, _randFilename("trans-", ".int"))
  hyp.wordlens = path.join(hypdir, _randFilename("wordlens-", ".txt"))
  hyp.intwordlens = path.join(hypdir, _randFilename("wordlens-", ".int"))
  hyp.phonelens = path.join(hypdir, _randFilename("phonelens-", ".txt"))
  hyp.intphonelens = path.join(hypdir, _randFilename("phonelens-", ".int"))

  copy2(transfile, hyp.filename)

  # prepare align command
  tmp = NamedTemporaryFile(suffix=".ark", delete=False)
  alignFile = tmp.name
  tmp.close()


  alignCmd = "{0} --transition-scale={1} --acoustic-scale={2} \
    --self-loop-scale={3} --beam={4} --retry-beam={5} \"{6}\" \"{7}\" \
    \"{8}\" \"ark:{9}\" ark,t:- \"ark:{10}\"".format(config.gmmalign,
    transitionscale, acousticscale, selfloopscale, beam, retrybeam, treefile,
    mdlfile, lexfst, featsfile, alignFile)


  logFile = open(path.join(hypdir, _randFilename(suffix=".log")), "w")

  try:
    # read word/phone symbol tables
    wordIntSymbols = {}
    wordSymbols = {}
    with open(wordsfile, "r") as symTableIn:
      for line in symTableIn:
        parts = split(line)
        wordIntSymbols[parts[0]] = parts[1]
        wordSymbols[parts[1]] = parts[0]

    phoneSymbols = {}
    with open(phonesfilealign, "r") as symTableIn:
      for line in symTableIn:
        parts = split(line)
        phoneSymbols[parts[1]] = parts[0]
        if parts[0] == config.WORD_BOUND_L:
          wordLeftSym = parts[1]
        elif parts[0] == config.WORD_BOUND_R:
          wordRightSym = parts[1]


    # translate transcripts to int symbols and send to aligner
    alignProc = Popen(alignCmd, stdin=PIPE, stderr=logFile, shell=True)
    with open(hyp.intfilename, "w") as hypOut:
      with open(hyp.filename, "r") as hypIn:
        for line in hypIn:
          parts = split(line)
          uttId = parts[0]
          words = parts[1:]
          for i in range(len(words)):
            try:
              words[i] = wordIntSymbols[words[i]]
            except KeyError:
              words[i] = wordIntSymbols[config.DECODE_OOV_WORD]
          translated = "{0} {1}\n".format(uttId, " ".join(words))
          hypOut.write(translated)
          alignProc.stdin.write(translated)
    alignProc.stdin.close()
    alignProc.wait()
    retCode = alignProc.poll()
    if retCode:
      raise KaldiError(logFile.name)


    _align(logFile, mdlfile, hyp.intfilename, lexfstalign,
        alignFile, hyp.intphonelens, hyp.phonelens, hyp.intwordlens,
        hyp.wordlens, phoneSymbols, wordSymbols, wordLeftSym, wordRightSym)
      

  finally:
    logFile.close()


  remove(alignFile)


  return _cacheObject(hyp, idxFile)

