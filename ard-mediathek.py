#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import requests
import argparse
import pycaption

VERSION = "1.1"

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
        self.subtitle_url = None
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
            print(f"Since no filename was given the default value '{os.path.basename(self.filename)}' will be used.")

        # get documentId from HTML
        doc_id = re.search(r'documentId=(\d+)', self.url)

        if doc_id is None:
            raise RuntimeError("The document id could not be found.")

        # request json file from Mediathek
        r  = requests.get(f"http://www.ardmediathek.de/play/media/{doc_id.group(1)}?devicetype=pc&features")
      
        if not 'application/json' in r.headers.get('content-type'):
            raise RuntimeError("The server didn't reply with JSON which indicates that an error occured.")

        json = r.json()

        # get subtitle URL from JSON
        if '_subtitleUrl' in json:
            self.subtitle_url = json['_subtitleUrl']


        # if video is available in the desired quality, get that url, else get the best available
        if len(json['_mediaArray'][0]['_mediaStreamArray']) >= self.quality + 1:
            video = json['_mediaArray'][0]['_mediaStreamArray'][self.quality]['_stream']
        else:
            video = json['_mediaArray'][0]['_mediaStreamArray'][-1]['_stream']

        if not video.startswith('http:'):
            video = "http:" + video

        # request and store video
        r = requests.get(video, stream=True)

        with open(self.filename, 'wb') as fd:
            filesize = int(r.headers['content-length'])/1024**2
            done = 0
            print(f"Downloading video. Download size: {filesize:.2f}MB")
            print(f"Downloading destination:{self.filename}")
            for chunk in r.iter_content(chunk_size=128):
                done = done + 128/1024**2 
                print(f"Downloaded {done:.2f}MB of {filesize:.2f}MB", end="\r")
                fd.write(chunk)

    def set_filename(self, filename):
        """
        Checks and sets the filename where the filename consists of the path *and* the filename.
        If the path does not exist yet, this method will try to build it.

        Returns the filename or None. If building the path does not work, this method will raise a RuntimeError.
        """
        if filename is None:
            return None
        if not os.path.isdir(os.path.dirname(filename)):
            print(f"Destination path '{os.path.dirname(filename)}' does not exist. Try to create it ...")
            try:
                os.makedirs(os.path.dirname(filename))
            except:
                raise RuntimeError("The destination path could not be built. Aborting.")
            print("Destination path was successfully created.")

        self.filename = filename
        return self.filename
       
    def set_quality(self, quality):
        """
        Set the desired video quality
        """
        self.quality = quality

    def get_subtitles(self):
    
        """
        download subtitles in srt format
        """
        
        if not self.subtitle_url:
            raise RuntimeError("Video does not contain subtitles")
        
        ut_file = requests.get(self.subtitle_url).text
        with open(os.path.splitext(self.filename)[0]+'.srt','w') as f:
            f.write(ut_file)
        print(f"subtitles saved as {(os.path.splitext(os.path.basename(self.filename))[0]+'.srt')}")

        # subtitles are in Timed Text Authoring Format V1.0 (DFXP http://www.w3.org/2006/10/ttaf1)
        # ut = pycaption.DFXPReader().read(ut_file)
        # for some reason there is a 10 hour offset on the subtitle timestamp (= 10*60*60*1000000 us)
        # ut.adjust_caption_timing(offset=-10*60*60*1000000)
       
        #if self.filename is None: # no filename was given - override it with default value
        #    self.filename = os.path.join(os.getcwd(), self.default_filename)
        #    
        #with open(os.path.splitext(self.filename)[0]+'.srt', 'wb') as f:    
        #    f.write(pycaption.SRTWriter().write(ut))
        #print(f"subtitles saved as {(os.path.splitext(os.path.basename(self.filename))[0]+'.srt')}")

def main(argv):
    parser = argparse.ArgumentParser(description='Commandline python script tool to download videos from the online ARD mediathek. Version: %s' % VERSION)

    parser.add_argument('url', type=str, help='URL pointing to the mediathek video')
    parser.add_argument('--filename', '-f', type=str, default=None, help='target filename')
    parser.add_argument('--quality', '-q', type=int, help='set the desired video quality', default=3, choices=[1,2,3])
    parser.add_argument('--subtitles', '-ut', action = "store_true", help='download subtitle in srt format')

    args = parser.parse_args()

    amd = ArdMediathekDownloader(args.url)
    amd.set_filename(args.filename)
    amd.set_quality(args.quality)
    amd.download()

    if args.subtitles:
        amd.get_subtitles()

if __name__ == "__main__":
    main(sys.argv)
