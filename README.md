# pyQRExfil

**Encode a file into QR codes and create a GIF**

`python file2QRgif.py ./test_files/test_file.py`

**Encode all files form a directory into QR codes and create a GIF**

`python file2QRgif.py ./test_files/`

This creates a GIF fodler with a `final.gif` file containing all QR codes.

**Decode and reassemble files**

`python decoder2.py -g="./gifs/final.gif" -o="output.json"

This will recover the original files into a new folder *Decoded* 


## TODO 
- Readme file
- Encode / Decode ZIP, binaries, ... (problems with characters encoding scheme)
- Add option to create one GIF per file instead of on GIF for all
- Add options to modify the data blocks in which the files are split (currently 50Bytes, for no reason)
- Need to test how it behaves for large files (max number of QR codes per GIF?)
