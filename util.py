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
Defines utility methods for caching kaldi objects.
"""

from os import path,listdir,makedirs,remove
from ast import literal_eval
from uuid import uuid4
from string import strip


class KaldiError(Exception):
  """
  Raised when a Kaldi binary exits without success.
  """
  msg = ""
  def __init__(self, logfilename):
    self.msg = "Kaldi exited with error. Log file: {0}.".format(logfilename)
    self.logfilename = logfilename
  def __str__(self):
    return self.msg


class KaldiObject(object):
  """
  Represents a Kaldi object, typically a file.
  """
  filename = ""




def _randFilename(prefix="", suffix=""):
  return "{0}{1}{2}".format(prefix, str(uuid4()), suffix)




def _getCachedObject(directory, params):
  """
  Returns a tuple containing in the first element an object
  cached from the given parameters, or an empty object if a cached
  object doesn't exist. The second element in the tuple is
  the name of the file in *directory* to be used for caching
  updates to the object. *params* should be a string.
  """
  try:
    for fname in listdir(directory):
      fname = path.join(directory, fname)
      if fname.endswith(".idx"):
        with open(fname, "r") as f:
          if strip(f.readline()) == "$skipidx":
            if strip(f.readline()) == params:
              objMembers = strip(f.readline())
              if len(objMembers) > 0:
                obj = KaldiObject()
                obj.__dict__.update(literal_eval(objMembers))
                return (obj, fname)
  except OSError:
    try:
      makedirs(directory)
    except OSError:
      pass

  idxFile = path.join(directory, _randFilename(suffix=".idx"))
  with open(idxFile, "w") as f:
    f.write("$skipidx\n")
    f.write("{0}\n".format(params))

  return (KaldiObject(), idxFile)





def _cacheObject(obj, idxFile):
  """
  Updates the specified *idxFile* with *obj*.
  Returns the object.
  """
  with open(idxFile, "r") as f:
    if strip(f.readline()) == "$skipidx":
      params = strip(f.readline())
  with open(idxFile, "w") as f:
    f.write("$skipidx\n")
    f.write("{0}\n".format(params))
    f.write("{0}\n".format(str(obj.__dict__)))

  return obj





def _refreshRequired(fnamepairs, deleteOld=True):
  """
  Tests the filename pairs in *fnamepairs* to see if a refresh
  of the cached files is required. A refresh is required
  if the first element is newer than the second element
  or if the second element does not exist. If *deleteOld*
  is True, when a refresh is required the existing old files,
  which are the second elements in the pairs, are deleted.
  """
  refreshRequired = False

  for pair in fnamepairs:
    if pair[1] is None:
      refreshRequired = True
      break
    elif not pair[0] or not pair[1]:
      refreshRequired = True
      break
    else:
      mtime = int(path.getmtime(pair[0]))
      try:
        if mtime > int(path.getmtime(pair[1])):
          refreshRequired = True
          break
      except OSError:
        refreshRequired = True
        break

  if refreshRequired and deleteOld:
    for pair in fnamepairs:
      try:
        remove(pair[1])
      except (OSError, TypeError):
        pass

  return refreshRequired

