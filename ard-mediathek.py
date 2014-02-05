#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import re
import urllib2
import argparse
import pycaption
from urlparse import urlparse, urljoin

VERSION = "1.0"

class ArdMediathekDownloader(object):
    """
    Commandline python script tool to download videos from the online ARD mediathek
    """

    def __init__(self, url):
        """
        Constructor.
        The URL will be checked already here.
        """
        self.url = self.validate_url(url)
        self.filename = None
        self.default_filename = "video.mp4"

    def validate_url(self, url):
        """
        Method to check if the URL is a valid URL or not.

        Returns the URL if everything is fine with it otherwise rises a ValueError.
        """
        regex = re.compile(
            r'^(?:http)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        try:
            return re.match(regex, url).group(0)
        except:
            raise ValueError("The given URL is not valid.")

    def download(self):
        """
        Downloads the video into its destination path.
        """
        if self.filename is None: # no filename was given - override it with default value
            self.filename = os.path.join(os.getcwd(), self.default_filename)
            self.print_("Since no filename was given the default value '%s' will be used." % os.path.basename(self.filename))

        resource = urllib2.urlopen(self.url)
        link = None
        for line in resource:
            res = re.search(r'^\s+mediaCollection\.addMediaStream\(1,\s2,\s"",\s"(.*)",\s"default"\);', line)
            try:
                link = res.group(1)
                break
            except AttributeError:
                continue
        if link is None:
            raise RuntimeError("The media link could not be found.")
        self.print_("Found media link url: %s" % link)

        u = urllib2.urlopen(link)
        with open(self.filename, 'wb') as f:
            meta = u.info() 
            filesize = int(meta.getheaders("Content-Length")[0]) 
            self.print_("Downloading video. Download size: %s MB" % (filesize/1024**2))
            self.print_("Downloading destination: %s" % self.filename)

            filesize_downloaded = 0
            blocksize = 8192

            while True:
                buffer = u.read(blocksize)
                if not buffer:
                    break
                filesize_downloaded += len(buffer)
                f.write(buffer)
                status = r"%10d  [%3.2f%%]" % (filesize_downloaded, filesize_downloaded * 100. / filesize)
                status = status + chr(8)*(len(status)+1)
                print status,

        self.print_("Download finished.%s" % (chr(32)*20))

    def print_(self, message):
        """
        Simple print method that appends a suffix in front of each printed line.
        """
        print "[%s] %s" % (os.path.basename(__file__), str(message))

    def set_filename(self, filename):
        """
        Checks and sets the filename where the filename consists of the path *and* the filename.
        If the path does not exist yet, this method will try to build it.

        Returns the filename or None. If building the path does not work, this method will raise a RuntimeError.
        """
        if filename is None:
            return None
        if not os.path.isdir(os.path.dirname(filename)):
            self.print_("Destination path '%s' does not exist. Try to create it ..." % os.path.dirname(filename))
            try:
                os.makedirs(os.path.dirname(filename))
            except:
                raise RuntimeError("The destination path could not be built. Aborting.")
            self.print_("Destination path was successfully created.")

        self.filename = filename
        return self.filename

    def get_filename(self, filename):
        """
        Getter method for the filename. 

        Returns the filename.
        """
        return self.filename
        
    def get_subtitles(self):
        """
        download subtitles in srt format
        """
        resource = urllib2.urlopen(self.url)
        link = None
        for line in resource:
            """ there are two ways in getting the subtiles one wit re search and the other assuming
            that the url of subtitles (/static/avportal/untertitel_mediathek/) does not change and using the document_id as the xml filename
            I'm using the first approach here"""
            res = re.search(r'mediaCollection\.setSubtitleUrl\(\"(.*)\"', line) # ^\s+
            try:               
                link = res.group(1)
                break
            except AttributeError:
                continue
        self.print_("getting subtitles")
        try:
            u = urllib2.urlopen(urljoin('http://'+urlparse(resource.url).hostname, link))
        except urllib2.HTTPError, (errno):
            if errno.code == 404:
                raise RuntimeError("Video does not contain subtitles")
        ut_file = u.read(u)
        # subtitles are in Timed Text Authoring Format V1.0 (DFXP http://www.w3.org/2006/10/ttaf1)
        ut = pycaption.DFXPReader().read(ut_file)
        # for some reason there is a 10 hour offset on the subtitle timestamp (= 10*60*60*1000000 us)
        ut.adjust_caption_timing(offset=-10*60*60*1000000)
       
        if self.filename is None: # no filename was given - override it with default value
            self.filename = os.path.join(os.getcwd(), self.default_filename)
            
        with open(os.path.splitext(self.filename)[0]+'.srt', 'wb') as f:    
            f.write(pycaption.SRTWriter().write(ut))
        self.print_("subtitles saved as %s" % (os.path.splitext(os.path.basename(self.filename))[0]+'.srt'))

def main(argv):
    parser = argparse.ArgumentParser(description='Commandline python script tool to download videos from the online ARD mediathek. Version: %s' % VERSION)

    parser.add_argument('url', type=str, help='URL pointing to the mediathek video')
    parser.add_argument('--filename', '-f', type=str, default=None, help='target filename')
    parser.add_argument('--subtitles', '-ut', action = "store_true", help='download subtitle in srt format')

    args = parser.parse_args()

    amd = ArdMediathekDownloader(args.url)
    amd.set_filename(args.filename)
    amd.download()

    if args.subtitles:
        amd.get_subtitles()

if __name__ == "__main__":
    main(sys.argv)
