SAIL Kaldi Interface for Python (SKIP)
====



Overview
----
Version: 0.1

SKIP is a Python module providing a simple interface to various
Kaldi functions. It accomplishes this by launching Kaldi binaries
as separate processes rather than linking with Kaldi
code. Because of this, the module code is pure Python.

Function results are stored so that subsequent calls to the same
function on unmodified files yield cached results immediately.


Currently the following functions are supported:

* FST generation (L, G, HCLG)
* Adding existing graphs and models
* Creating/segmenting MFCC features
* Decoding to text
* Word- and phone- level alignment



License
----
This project is released under the Apache License, Version 2.0.
See the file LICENSE for more details.



Requirements
----
Requires Python 2.6 - 2.7 and [KALDI](http://kaldi.sourceforge.net/) (should be
latest version).




Getting Started
----
First download the project and be sure it is in Python's module search path.
Then import the module and initialize a context.

The following example shows how to decode a set of wave files using existing graphs and models. The wave files must be specified as a text scp file for Kaldi.


```python
from skip import KaldiContext

context = KaldiContext("example", "./kaldi-trunk")

mdl = context.addGMM("final.mdl", "tree")
L = context.addL("L.fst", "phones.tab", "words.tab")
HCLG = context.addHCLG("HCLG.fst")
feats = context.makeFeatures("wav.scp")
hyp = context.decode(feats, HCLG, L, mdl)
...
```


The following command generates a grammar FST from an existing ARPA language model
and makes a decoding graph from it:


```python
...
G = context.makeG(words.txt, "lm.arpa")
HCLG = context.makeHCLG(L, G, mdl)
...
```



To interact with the text after features have been decoded, open and read the hypothesis file as a regular text file:


```python
...
hyp = context.decode(feats, HCLG, L, mdl)

with open(hyp.filename) as f:
	for line in f:
		print line

```


