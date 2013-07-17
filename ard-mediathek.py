#!/usr/bin/python2
import os
import sys
import re
import urllib2

if len(sys.argv) < 2:
    print("Usage: python2 ard-mediathek.py url [filename]")
    sys.exit(1)

resource = urllib2.urlopen(sys.argv[1])

if resource == None: 
    print("URL not valid!")
    sys.exit(1)

filename = None

if len(sys.argv) == 3:
    filename = sys.argv[2]

link = None

for line in resource:
    link = re.search(r'^\s+mediaCollection\.addMediaStream\(1,\s2,\s"",\s"(.*)",\s"default"\);', line)
    if link != None:
        break

if link.group(1):
    print("Link to media: %s" % link.group(1))
else:
    print("No link to media found!")

link = link.group(1)
if filename == None:
    filename = link.split("/")[-1]
print("Receiving file info for %s" % link)

u = urllib2.urlopen(link)
f = open(filename, 'wb')
meta = u.info()
filesize = int(meta.getheaders("Content-Length")[0])
print("Downloading: %s, size: %sMB" % (filename, (filesize / 1024 / 1024)))

filesizedl = 0
blocksz = 8192
while True:
    buffer = u.read(blocksz)
    if not buffer:
        break
    filesizedl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (filesizedl, filesizedl * 100. / filesize)
    status = status + chr(8)*(len(status)+1)
    print status,

f.close()

print("Download finished%s" % (chr(32)*20))
