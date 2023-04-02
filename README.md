# pyQRExfil

## Usage

*Encode a file into QR codes and create a GIF*

`python file2QRgif.py filename`

*Encode all files form a directory into QR codes and create a GIF*
`python file2QRgif.py ./directory/`

This creates a GIF fodler with a `final.gif` file containing all QR codes.

*Decode and reassemble files*
`python decoder2.py -g="./gifs/final.gif" -o="output.json"

This will recover the original files
