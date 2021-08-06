# bip_czdz
Script for check updates on:
 [Czechowice-Dziedzice's BIP](https://www.bip.czechowice-dziedzice.pl/)
 [Czechowice-Dziedzice's eurzad](https://eurzad.finn.pl/gmczechowicedziedzice/#!/)
 [Czechowice-Dziedzice news page](https://www.czechowice-dziedzice.pl/)
Script gets content of pages and check with file if new version or new document is present on BIP.

New content is written to bip_new_found.txt file.
Known documents are stored in bip_docs.txt file.

Script use python 3.x
To run type in console python bip.py or double click

## known issues
- script does not check next pages on the BIP pages. However, lots of information was moved to the eurzad
