#!/usr/bin/env python
"""
Creates OpenFST symbol table and lexicon text files
from the CMU Pronouncing Dictionary v0.7a.
"""
from os import path
from sys import argv,stderr
from collections import deque
from string import strip,split


# default parameters
addSilNoise = True
addPositionMarkers = True
addEmptyWord = True
addUnknownWord = True
addDisambigSymbols = True
addWordBoundaries = False
silencePhone = "SIL"
spkNoisePhone = "SPN"
nonspkNoisePhone = "NSN"
silenceWord = "!SIL"
spkNoiseWord = "<SPOKEN-NOISE>"
nonspkNoiseWord = "<NOISE>"
emptyStartWord = "<s>"
emptyEndWord = "</s>"
unknownWord = "<UNK>"
wordDisambig = "#0"
wboundLeft = "#1"
wboundRight = "#2"


def main():
  # process command line args
  arguments = deque(argv[1:])
  usageError = False
  options = []
  params = []
  while len(arguments) > 0:
    arg = arguments.popleft()
    if arg.startswith("--"):
      if len(params) == 0:
        options.append(arg)
      else:
        usageError = True
    else:
      params.append(arg)

  if len(params) < 4:
    usageError = True
  else:
    cmuDictDirIn = params[0]
    wordsFileOut = params[1]
    phonesFileOut = params[2]
    lexiconFileOut = params[3]

  for opt in options:
    try:
      choice = opt[opt.index("=")+1:]
      if len(choice) == 0:
        raise ValueError
      choice = (choice.lower() == "true" or choice == 1 or choice == "1")
    except ValueError:
      usageError = True
      break

    if opt.startswith("--add-silnoise="):
      addSilNoise = choice
    elif opt.startswith("--add-unknown="):
      addUnknownWord = choice
    elif opt.startswith("--add-empty="):
      addEmptyWord = choice
    elif opt.startswith("--add-position="):
      addPositionMarkers = choice
    elif opt.startswith("--add-disambig="):
      addDisambigSymbols = choice
    elif opt.startswith("--add-word-bounds="):
      addWordBoundaries = choice
    else:
      usageError = True


  if usageError:
    sp = 30
    stderr.write("Reads the CMU pronouncing dictionary and outputs symbol table and lexicon files.\n")
    stderr.write("Usage: {0} [OPTIONS] <in_dict_dir> <out_words.txt> <out_phones.txt> <out_lexicon.txt>\n\n".format(argv[0]))
    stderr.write("OPTIONS:\n")
    stderr.write("{0}{1}\n".format("--add-silnoise=true|false".ljust(sp), "Adds silence and noise symbols. Default=true."))
    stderr.write("{0}{1}\n".format("--add-unknown=true|false".ljust(sp), "Adds an unknown word symbol. Default=true."))
    stderr.write("{0}{1}\n".format("--add-empty=true|false".ljust(sp), "Adds empty word symbols. Default=true."))
    stderr.write("{0}{1}\n".format("--add-position=true|false".ljust(sp), "Adds beginning/end/singleton markers to phones. Default=true."))
    stderr.write("{0}{1}\n".format("--add-disambig=true|false".ljust(sp), "Adds disambiguation symbols. Default=true."))
    stderr.write("{0}{1}\n".format("--add-word-bounds=true|false".ljust(sp), "Adds boundary symbols to word pronunciations. Default=false."))
    quit(1)


  # prepare pronunciations from dictionary
  pronunciationMap = {}
  if addSilNoise:
    pronunciationMap[silenceWord] = silencePhone
    pronunciationMap[spkNoiseWord] = spkNoisePhone
    pronunciationMap[nonspkNoiseWord] = nonspkNoisePhone
  if addUnknownWord:
    pronunciationMap[unknownWord] = spkNoisePhone
  if addEmptyWord:
    pronunciationMap[emptyStartWord] = ""
    pronunciationMap[emptyEndWord] = ""

  with open(path.join(cmuDictDirIn, "cmudict.0.7a"), "r") as wordsIn:
    for line in wordsIn:
      if line.startswith(";;;"):
        continue
      sp = line.index(" ")
      word = strip(line[:sp])
      proParts = split(strip(line[sp:]))
      if addPositionMarkers:
        if len(proParts) == 1:
          pronunciation = "{0}_S".format(proParts[0])
        else:
          proParts[0] = "{0}_B".format(proParts[0])
          proParts[-1] = "{0}_E".format(proParts[-1])
      pronunciation = " ".join(proParts)
      pronunciationMap[word] = pronunciation


  # generate disambiguation symbols for repeated phone sequences
  seqCounts = {}
  for phoneSeq in pronunciationMap.values():
    seqParts = split(phoneSeq)
    if len(seqParts) == 0:
      if not "" in seqCounts:
        seqCounts[""] = 1
      else:
        seqCounts[""] += 1
    else:
      for i in range(len(seqParts)):
        prefix = " ".join(seqParts[:i+1])
        if not prefix in seqCounts:
          seqCounts[prefix] = 1
        else:
          seqCounts[prefix] += 1



  # write word symbols table and lexicon file
  maxDisambigId = 0
  curSymbolNumbers = {}
  wordsSorted = sorted(pronunciationMap.keys())
  with open(lexiconFileOut, "w") as lexiconOut:
    with open(wordsFileOut, "w") as wordsOut:
      wordsOut.write("{0} {1}\n".format("<eps>", 0))
      wordId = 1

      for word in wordsSorted:
        pronunciation = pronunciationMap[word]
        disambigStr = ""
        if addDisambigSymbols and seqCounts[pronunciation] > 1:
          if not pronunciation in curSymbolNumbers:
            if addWordBoundaries:
              curSymbolNumbers[pronunciation] = 3
            else:
              curSymbolNumbers[pronunciation] = 1

          disambigId = curSymbolNumbers[pronunciation]
          curSymbolNumbers[pronunciation] += 1
          disambigStr = " #{0}".format(disambigId)
          if disambigId > maxDisambigId:
            maxDisambigId = disambigId

        # remove parenthetical notations
        if "(" in word:
          if word.rindex("(") != 0:
            word = word[:word[1:].index("(") + 1]

        lboundStr = ""
        rboundStr = ""
        if addWordBoundaries:
          lboundStr = "{0} ".format(wboundLeft)
          rboundStr = " {0}".format(wboundRight)
        lexiconOut.write("{0} {1}{2}{3}{4}\n".format(word, lboundStr,
          pronunciation, disambigStr, rboundStr))
        wordsOut.write("{0} {1}\n".format(word, wordId))
        wordId += 1

      # always write word disambig symbol
      wordsOut.write("{0} {1}\n".format(wordDisambig, wordId))
      wordId += 1



  # write phone symbols table
  with open(phonesFileOut, "w") as phonesOut:
    phonesOut.write("{0} {1}\n".format("<eps>", 0))
    symbolId = 1
    if addSilNoise:
      phonesOut.write("{0} {1}\n".format(silencePhone, symbolId))
      symbolId += 1
      phonesOut.write("{0} {1}\n".format(spkNoisePhone, symbolId))
      symbolId += 1
      phonesOut.write("{0} {1}\n".format(nonspkNoisePhone, symbolId))
      symbolId += 1
    with open(path.join(cmuDictDirIn, "cmudict.0.7a.symbols"), "r") as symbolsIn:
        for line in symbolsIn:
          sym = strip(line)
          phonesOut.write("{0} {1}\n".format(sym, symbolId))
          symbolId += 1
          if addPositionMarkers:
            phonesOut.write("{0}_B {1}\n".format(sym, symbolId))
            symbolId += 1
            phonesOut.write("{0}_E {1}\n".format(sym, symbolId))
            symbolId += 1
            phonesOut.write("{0}_S {1}\n".format(sym, symbolId))
            symbolId += 1
        # write disambig symbols
        phonesOut.write("#{0} {1}\n".format(0, symbolId))
        symbolId += 1
        nextSym = 1
        if addWordBoundaries:
          phonesOut.write("#{0} {1}\n".format(1, symbolId))
          symbolId += 1
          phonesOut.write("#{0} {1}\n".format(2, symbolId))
          symbolId += 1
          nextSym += 2
        if addDisambigSymbols:
          for i in range(nextSym, maxDisambigId + 1):
            phonesOut.write("#{0} {1}\n".format(i, symbolId))
            symbolId += 1
            


if __name__ == "__main__":
  main()

