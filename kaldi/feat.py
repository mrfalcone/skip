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
Defines methods for generating features with Kaldi.
"""

from os import path,remove
from shutil import copy2
from string import strip
from subprocess import Popen
from tempfile import NamedTemporaryFile

from skip.util import (KaldiObject, _randFilename, _getCachedObject,
  _cacheObject, _refreshRequired, KaldiError)
import skip.config as config



def makeMfccFeats(directory, wavscp, samplefreq, useenergy, applycmvn,
  normvars, utt2spk, spk2utt, deltaorder):

  Mfccdir = path.join(directory, "mfcc_feats")
  (feats, idxFile) = _getCachedObject(Mfccdir, str(locals()))
  

  # check wave files to make sure they are up to date
  wavsOld = False
  try:
    mtimes = feats.wav_times
    for wavFile in mtimes.keys():
      if int(path.getmtime(wavFile)) > mtimes[wavFile]:
        wavsOld = True
        break
  except AttributeError:
    pass


  # check file modification time to see if a refresh is required
  origNames = []
  copyNames = []
  try:
    origNames.append(wavscp)
    copyNames.append(feats.wavscp)
  except AttributeError:
    copyNames.append(None)

  if utt2spk and spk2utt:
    try:
      origNames.append(utt2spk)
      copyNames.append(feats.utt2spk)
    except AttributeError:
      copyNames.append(None)
    try:
      origNames.append(spk2utt)
      copyNames.append(feats.spk2utt)
    except AttributeError:
      copyNames.append(None)

  if not _refreshRequired(zip(origNames, copyNames)) and not wavsOld:
    return feats


  feats.filename = path.join(Mfccdir, _randFilename("feats-", ".ark"))
  feats.wavscp = path.join(Mfccdir, _randFilename("wav-", ".scp"))
  copy2(wavscp, feats.wavscp)

  feats.wav_times = {}
  with open(feats.wavscp, "r") as wavsIn:
    for line in wavsIn:
      if strip(line):
        if "|" not in line: # ignore commands in the table
          fname = strip(line[line.index(" "):])
          feats.wav_times[fname] = int(path.getmtime(fname))


  if utt2spk and spk2utt:
    feats.utt2spk = path.join(Mfccdir, _randFilename("utt2spk-", ".ark"))
    copy2(utt2spk, feats.utt2spk)
    feats.spk2utt = path.join(Mfccdir, _randFilename("spk2utt-", ".ark"))
    copy2(spk2utt, feats.spk2utt)


  tmp = NamedTemporaryFile(suffix=".ark", delete=False)
  rawfeatsFile = tmp.name
  tmp.close()


  # prepare commands
  rawfeatsDest = "\"ark:{0}\"".format(rawfeatsFile)
  deltaStr = ""
  if deltaorder > 0:
    deltaStr = "ark:- | {0} --delta-order={1} ark:-".format(config.adddeltas, deltaorder)
    if not applycmvn:
      rawfeatsDest = "{0} > \"{1}\"".format(deltaStr, feats.filename)
  elif not applycmvn:
    rawfeatsDest = "\"ark:{0}\"".format(feats.filename)

  makeRawFeatCmd = "{0} --sample-frequency={1} --use-energy={2} \
    \"scp:{3}\" {4}".format(config.computemfccfeats,
    samplefreq, str(useenergy).lower(), wavscp, rawfeatsDest)


  if applycmvn:
    spk2uttStr = ""
    utt2spkStr = ""
    if utt2spk and spk2utt:
      spk2uttStr = "--spk2utt=\"ark:{0}\"".format(spk2utt)
      utt2spkStr = "--utt2spk=\"ark:{0}\"".format(utt2spk)

    applyCmvnCmd = "{0} {1} \"ark:{2}\" ark:- | {3} --norm-vars={4} \
      {5} ark:- \"ark:{2}\" {6} \"ark:{7}\"".format(config.computecmvnstats,
      spk2uttStr, rawfeatsFile, config.applycmvn, str(normvars).lower(),
      utt2spkStr, deltaStr, feats.filename)


  # compute and return the features
  logFile = open(path.join(Mfccdir, _randFilename(suffix=".log")), "w")

  try:
    featProc = Popen(makeRawFeatCmd, stderr=logFile, shell=True)
    featProc.communicate()
    retCode = featProc.poll()
    if retCode:
      raise KaldiError(logFile.name)

    if applycmvn:
      featProc = Popen(applyCmvnCmd, stderr=logFile, shell=True)
      featProc.communicate()
      retCode = featProc.poll()
      if retCode:
        raise KaldiError(logFile.name)
  finally:
    logFile.close()

  remove(rawfeatsFile)


  return _cacheObject(feats, idxFile)


