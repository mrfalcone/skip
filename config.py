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
Defines a configuration object that stores paths and constants.
"""

from os import path

class ConfigObject(object):
  """
  Represents a collection of configuration variables as members.
  """

  def __str__(self):
    """
    Returns a string representation of the config.
    """
    return str(map(str, self.__dict__))

  def __init__(self, kaldiDir, userValues=None):
    """
    Constructs a new config object. *kaldiDir* must be the
    root directory of Kaldi. If *userValues* is not None,
    it must be a dictionary object containing key/value pairs
    that will be added to the config object.
    """

    configMap = {}

    # symbol configurations
    configMap["SIL_PHONE"] = "SIL"
    configMap["SIL_WORD"] = "<SILENCE>"
    configMap["SPN_PHONE"] = "SPN"
    configMap["NSN_PHONE"] = "NSN"
    configMap["EPS"] = "<eps>"
    configMap["UNKNOWN_WORD"] = "<UNK>"
    configMap["SOS_WORD"] = "<s>"
    configMap["EOS_WORD"] = "</s>"
    configMap["EPS_G"] = "#0"
    configMap["WORD_BOUND_L"] = "#1"
    configMap["WORD_BOUND_R"] = "#2"
    configMap["DECODE_OOV_WORD"] = "<SPOKEN_NOISE>"
    configMap["DECODE_OOV_PHONE"] = "SPN"

    # paths
    configMap["KALDI_DIR"] = kaldiDir
    configMap["CONTEXTS_DIR"] = path.join(path.dirname(__file__), "contexts")
    configMap["OPENFST_DIR"] = "{0}/tools/openfst".format(configMap["KALDI_DIR"])
    configMap["fstcompile"] = "{0}/src/bin/fstcompile".format(configMap["OPENFST_DIR"])
    configMap["fstarcsort"] = "{0}/src/bin/fstarcsort".format(configMap["OPENFST_DIR"])
    configMap["fstaddselfloops"] = "{0}/src/fstbin/fstaddselfloops".format(configMap["KALDI_DIR"])
    configMap["arpa2fst"] = "{0}/src/bin/arpa2fst".format(configMap["KALDI_DIR"])
    configMap["fstprint"] = "{0}/src/bin/fstprint".format(configMap["OPENFST_DIR"])
    configMap["fstrmepsilon"] = "{0}/src/bin/fstrmepsilon".format(configMap["OPENFST_DIR"])
    configMap["makehtransducer"] = "{0}/src/bin/make-h-transducer".format(configMap["KALDI_DIR"])
    configMap["fsttablecompose"] = "{0}/src/fstbin/fsttablecompose".format(configMap["KALDI_DIR"])
    configMap["fstdeterminizestar"] = "{0}/src/fstbin/fstdeterminizestar".format(configMap["KALDI_DIR"])
    configMap["fstminimizeencoded"] = "{0}/src/fstbin/fstminimizeencoded".format(configMap["KALDI_DIR"])
    configMap["fstcomposecontext"] = "{0}/src/fstbin/fstcomposecontext".format(configMap["KALDI_DIR"])
    configMap["fstrmsymbols"] = "{0}/src/fstbin/fstrmsymbols".format(configMap["KALDI_DIR"])
    configMap["fstrmepslocal"] = "{0}/src/fstbin/fstrmepslocal".format(configMap["KALDI_DIR"])
    configMap["addselfloops"] = "{0}/src/bin/add-self-loops".format(configMap["KALDI_DIR"])
    configMap["computemfccfeats"] = "{0}/src/featbin/compute-mfcc-feats".format(configMap["KALDI_DIR"])
    configMap["adddeltas"] = "{0}/src/featbin/add-deltas".format(configMap["KALDI_DIR"])
    configMap["extractsegments"] = "{0}/src/featbin/extract-segments".format(configMap["KALDI_DIR"])
    configMap["extractfeaturesegments"] = "{0}/src/featbin/extract-feature-segments".format(configMap["KALDI_DIR"])
    configMap["computecmvnstats"] = "{0}/src/featbin/compute-cmvn-stats".format(configMap["KALDI_DIR"])
    configMap["applycmvn"] = "{0}/src/featbin/apply-cmvn".format(configMap["KALDI_DIR"])
    configMap["gmmdecode"] = "{0}/src/gmmbin/gmm-decode-faster".format(configMap["KALDI_DIR"])
    configMap["gmmlatgen"] = "{0}/src/gmmbin/gmm-latgen-faster".format(configMap["KALDI_DIR"])
    configMap["latticewordalign"] = "{0}/src/latbin/lattice-word-align".format(configMap["KALDI_DIR"])
    configMap["latticetonbest"] = "{0}/src/latbin/lattice-to-nbest".format(configMap["KALDI_DIR"])
    configMap["latticembrdecode"] = "{0}/src/latbin/lattice-mbr-decode".format(configMap["KALDI_DIR"])
    configMap["nbesttolinear"] = "{0}/src/latbin/nbest-to-linear".format(configMap["KALDI_DIR"])
    configMap["gmmalign"] = "{0}/src/gmmbin/gmm-align".format(configMap["KALDI_DIR"])
    configMap["alitophones"] = "{0}/src/bin/ali-to-phones".format(configMap["KALDI_DIR"])
    configMap["phonestoprons"] = "{0}/src/bin/phones-to-prons".format(configMap["KALDI_DIR"])
    configMap["pronstowordali"] = "{0}/src/bin/prons-to-wordali".format(configMap["KALDI_DIR"])


    if userValues:
      configMap.update(userValues)

    self.__dict__.update(configMap)




