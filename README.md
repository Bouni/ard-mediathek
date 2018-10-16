ard-mediathek
===============

The German public TV station "ARD" has a nice mediathek (video on demand) where they offer all their movies/documentations and so on.
Sadly they delete or at least take them offline after 7 days.

There is no official way for downloading the videos.

Therefore [bouni](https://github.com/Bouni) has written ard-mediathek.py, a simple commandline python script for downloading the videos. It was extended by [dotcs](https://github.com/dotcs).

### Installation
```
pipenv install 
```
## Usage

    pipenv run python ard-mediathek.py <url> [--filename FILENAME]

 - Go to the ARD mediathek and open the page with the video you want to download.
 - Copy the URL from your browser, for example (http://mediathek.daserste.de/sendungen_a-z/799280_reportage-dokumentation/15880804_unser-wirtschaftswunder-die-wahre-geschichte)
 - Run the script as shown above
 - You can optionally pass a target filename as second parameter (otherwise `video.mp4` is used as the default filename)
 - if you set the parameter `--derivefilename`, the script will set the filename to the title of the URL which contains the video
 - Wait for the download to complete :-)

You can get also a quick overview by calling

    ./ard-mediathek.py --help
