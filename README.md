ard-mediathek
===============

The german public TV station "ARD" has a nice mediathek (video on demand) where they offer all their movies/documentations etc.
Sadly they delete or at least takte them offline after 7 days.

There is no official way for downloading the videos.

Therefore i've written ard-mediathek.py, a simple commandline python script for downloading the videos.

## Usage

`./ard-mediathek.py url [filename]`

 - go to the ARD mediathek and open the page witgh the video you want to download.
 - copy the URL from your browser, for example (http://mediathek.daserste.de/sendungen_a-z/799280_reportage-dokumentation/15880804_unser-wirtschaftswunder-die-wahre-geschichte)
 - run the script as shown above
 - you can optinaly pass a filename as second parameter if you don't want the cryptically filename of the ortiginal file
 - wait for the download to complete :-)

