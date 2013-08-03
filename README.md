SAIL Kaldi Interface for Python (SKIP)
====

Version 0.1


Overview
----
SKIP is a Python module providing a simple interface to various
Kaldi functions. It accomplishes this by launching Kaldi binaries
as separate processes and threads rather than linking with Kaldi
code. Because of this, the module code is pure Python.

Currently the following functions are supported:
* FST generation (L, G, HCLG)
* Decoding to text
* Word- and phone- level alignment



License
----
This project is released under the Apache License, Version 2.0.
See the file LICENSE for more details.



Requirements
----
Requires Python 2.6 - 2.7. In addition:

* [KALDI](http://kaldi.sourceforge.net/) - Required. Should be latest version.
* [SRILM](http://www.speech.sri.com/projects/srilm/) - Optional unless you want to generate language models directly from training data.



Installing and Configuring
----
1. Download the project and store in any location.
2. Configure directories using the `configure.sh` script.
3. Import the module and initialize a context.



Example Usage
----
TODO

