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
Defines methods for decoding and aligning with GMM-based models.
"""

from os import path,remove
from subprocess import Popen
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
  phoneLensFile = NamedTemporaryFile(mode="w+", suffix=".txt")
  makePhonelensProc = Popen(makePhonelensCmd, stdout=phoneLensFile,
    stderr=logFile, shell=True)
  makePhonelensProc.communicate()
  retCode = makePhonelensProc.poll()
  if retCode:
    raise KaldiError(logFile.name)

  phoneLensFile.seek(0)

  with open(intphonelens, "w") as lensIntOut:
    with open(phonelens, "w") as lensOut:
      for line in phoneLensFile:
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
  phoneLensFile.close()

  

  makeWordlensCmd = "{0} \"{1}\" \"ark:{2}\" ark:- | {3} \"{4}\" \
    {5} {6} ark:- \"ark,t:{7}\" ark:- | {8} ark:- \"ark,t:{9}\" \
    ark,t:-".format(config.alitophones, mdlfile, alignFile,
      config.phonestoprons, lexfstalign, wordLeftSym, wordRightSym,
      intfilename, config.pronstowordali, intphonelens)


  # align words and translate to text
  wordLensFile = NamedTemporaryFile(mode="w+", suffix=".txt")
  makeWordlensProc = Popen(makeWordlensCmd, stdout=wordLensFile,
    stderr=logFile, shell=True)
  makeWordlensProc.communicate()
  retCode = makeWordlensProc.poll()
  if retCode:
    raise KaldiError(logFile.name)

  wordLensFile.seek(0)

  with open(intwordlens, "w") as lensIntOut:
    with open(wordlens, "w") as lensOut:
      for line in wordLensFile:
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
  wordLensFile.close()
  



def decodeNbestFeats(directory, numHypotheses, featsfile, graphfile,
  wordsfile, lexiconfile, mdlfile, treefile, phonesfilealign, lexfstalign, beam,
  allowpartial, acousticscale):

  hypdir = path.join(directory, "nbest-hypotheses")
  (hypCollection, idxFile) = _getCachedObject(hypdir, str(locals()))
  

  # check file modification times to see if refresh is required
  refreshRequired = False
  try:
    if int(path.getmtime(featsfile)) > hypCollection.featsfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(graphfile)) > hypCollection.graphfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(wordsfile)) > hypCollection.wordsfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(lexiconfile)) > hypCollection.lexiconfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(mdlfile)) > hypCollection.mdlfile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True
  try:
    if int(path.getmtime(treefile)) > hypCollection.treefile_time:
      refreshRequired = True
  except AttributeError:
    refreshRequired = True

  if phonesfilealign and lexfstalign:
    try:
      if int(path.getmtime(phonesfilealign)) > hypCollection.phonesfilealign_time:
        refreshRequired = True
    except AttributeError:
      refreshRequired = True
    try:
      if int(path.getmtime(lexfstalign)) > hypCollection.lexfstalign_time:
        refreshRequired = True
    except AttributeError:
      refreshRequired = True

  if not refreshRequired:
    return hypCollection


  # remove old files
  try:
    remove(hypCollection.filename)
  except (OSError, AttributeError):
    pass
  try:
    remove(hypCollection.intfilename)
  except (OSError, AttributeError):
    pass
  try:
    remove(hypCollection.wordlens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hypCollection.intwordlens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hypCollection.phonelens)
  except (OSError, AttributeError):
    pass
  try:
    remove(hypCollection.intphonelens)
  except (OSError, AttributeError):
    pass


  hypCollection.featsfile_time = int(path.getmtime(featsfile))
  hypCollection.graphfile_time = int(path.getmtime(graphfile))
  hypCollection.wordsfile_time = int(path.getmtime(wordsfile))
  hypCollection.lexiconfile_time = int(path.getmtime(lexiconfile))
  hypCollection.mdlfile_time = int(path.getmtime(mdlfile))
  hypCollection.treefile_time = int(path.getmtime(treefile))
  if phonesfilealign and lexfstalign:
    hypCollection.phonesfilealign_time = int(path.getmtime(phonesfilealign))
    hypCollection.lexfstalign_time = int(path.getmtime(lexfstalign))
  
  

  hypCollection.filename = path.join(hypdir, _randFilename("hyp-", ".txt"))
  hypCollection.intfilename = path.join(hypdir, _randFilename("hyp-", ".int"))
  if phonesfilealign and lexfstalign:
    hypCollection.wordlens = path.join(hypdir, _randFilename("wordlens-", ".txt"))
    hypCollection.intwordlens = path.join(hypdir, _randFilename("wordlens-", ".int"))
    hypCollection.phonelens = path.join(hypdir, _randFilename("phonelens-", ".txt"))
    hypCollection.intphonelens = path.join(hypdir, _randFilename("phonelens-", ".int"))


  # prepare lattice generator command
  tmp = NamedTemporaryFile(suffix=".ark", delete=False)
  latFile = tmp.name
  tmp.close()

  latgenCmd = "{0} --beam={1} --allow-partial={2} \
    --acoustic-scale={3} {4} {5} \"ark:{6}\" ark:- | \
    {7} --acoustic-scale={3} --n={8} ark:- \"ark:{9}\"".format(config.gmmlatgen,
    beam, str(allowpartial).lower(), acousticscale, mdlfile,
    graphfile, featsfile, config.latticetonbest, numHypotheses, latFile)


  logFile = open(path.join(hypdir, _randFilename(suffix=".log")), "w")

  try:
    latgenProc = Popen(latgenCmd, stderr=logFile, shell=True)
    latgenProc.communicate()
    retCode = latgenProc.poll()
    if retCode:
      raise KaldiError(logFile.name)


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



    tmp = NamedTemporaryFile(suffix=".ark", delete=False)
    alignFile = tmp.name
    tmp.close()

    decodeCmd = "{0} \"ark:{1}\" \"ark:{2}\" ark,t:-".format(config.nbesttolinear,
      latFile, alignFile)

    # decode hypothesis transcripts and translate to text
    decodedFile = NamedTemporaryFile(mode="w+", suffix=".txt")
    decodeProc = Popen(decodeCmd, stdout=decodedFile, stderr=logFile, shell=True)
    decodeProc.communicate()
    retCode = decodeProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

    decodedFile.seek(0)
    
    with open(hypCollection.intfilename, "w") as hypIntOut:
      with open(hypCollection.filename, "w") as hypOut:
        for line in decodedFile:
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
    decodedFile.close()
    


    # if alignment symbols were given, compute word and phone lengths
    if phonesfilealign and lexfstalign:
      _align(logFile, mdlfile, hypCollection.intfilename, lexfstalign,
        alignFile, hypCollection.intphonelens, hypCollection.phonelens, hypCollection.intwordlens,
        hypCollection.wordlens, phoneSymbols, wordSymbols, wordLeftSym, wordRightSym)


  finally:
    logFile.close()


  remove(alignFile)


  return _cacheObject(hypCollection, idxFile)







def decodeFeats(directory, featsfile, graphfile, wordsfile, mdlfile,
  treefile, phonesfilealign, lexfstalign, beam, allowpartial,
  acousticscale, numHypotheses=1):

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
    decodedFile = NamedTemporaryFile(mode="w+", suffix=".txt")
    decodeProc = Popen(decodeCmd, stdout=decodedFile, stderr=logFile, shell=True)
    decodeProc.communicate()
    retCode = decodeProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

    decodedFile.seek(0)
    
    with open(hyp.intfilename, "w") as hypIntOut:
      with open(hyp.filename, "w") as hypOut:
        for line in decodedFile:
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
    decodedFile.close()
    


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
  hypFile = NamedTemporaryFile(mode="w+", suffix=".txt")

  
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


  # translate transcripts to int symbols
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
        hypFile.write(translated)
    
  try:
    hypFile.seek(0)
    alignProc = Popen(alignCmd, stdin=hypFile, stderr=logFile, shell=True)
    alignProc.communicate()
    retCode = alignProc.poll()
    if retCode:
      raise KaldiError(logFile.name)


    _align(logFile, mdlfile, hyp.intfilename, lexfstalign,
        alignFile, hyp.intphonelens, hyp.phonelens, hyp.intwordlens,
        hyp.wordlens, phoneSymbols, wordSymbols, wordLeftSym, wordRightSym)
      

  finally:
    hypFile.close()
    logFile.close()


  remove(alignFile)


  return _cacheObject(hyp, idxFile)

