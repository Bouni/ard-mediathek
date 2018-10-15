#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import requests
import argparse
import pycaption
import contextlib
from collections import defaultdict

from progress.bar import IncrementalBar

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
        doc_id_result = re.search(r'documentId=(\d+)', self.url)

        if doc_id_result is None:
            raise RuntimeError("The document id could not be found.")
        doc_id = doc_id_result.group(1)

        json = self._get_media_json_by_document_id(doc_id)

        # get subtitle URL from JSON
        if '_subtitleUrl' in json:
            self.subtitle_url = json['_subtitleUrl']

        video_url = self._get_video_url(json)

        # request and store video_url
        r = requests.get(video_url, stream=True)

        chunk_size = 4096
        with open(self.filename, 'wb') as fd:
            filesize = int(r.headers['content-length'])/1024**2
            done = 0
            print(f"Downloading video. Download size: {filesize:.2f}MB")
            print(f"Downloading destination:{self.filename}")
            bar = IncrementalBar('Downloading', suffix='%(percent).2f%% %(index).2fMB/%(max).2fMB', max=filesize)

            for chunk in r.iter_content(chunk_size=chunk_size):
                done = done + chunk_size/1024**2
                bar.goto(done)
                fd.write(chunk)
            bar.finish()

    def _get_media_json_by_document_id(self, doc_id):
        # request json file from Mediathek
        r = requests.get(f"http://www.ardmediathek.de/play/media/{doc_id}?devicetype=pc&features")
        if not 'application/json' in r.headers.get('content-type'):
            raise RuntimeError("The server didn't reply with JSON which indicates that an error occured.")
        json = r.json()
        return json

    def _get_video_url(self, json):
        # if video is available in the desired quality, get that url, else get the best available
        media = json['_mediaArray']
        return self._get_video_by_quality(media)

    def _get_video_by_quality(self, media):
        medias = self._get_all_stream_urls_grouped_by_quality(media)
        if self.quality in medias:
            url = next(iter(medias[self.quality]))
            if not url.startswith('http:') and not url.startswith('https:'):
                url = "http:" + url

            return url
        else:
            raise RuntimeError(f"Cannot find a video for quality. Available Qualities are:{medias.keys()}")

    def _get_all_stream_urls_grouped_by_quality(self, medias):
        res = defaultdict(set)
        for medium in medias:
            streams = medium['_mediaStreamArray']
            for stream in streams:
                stream_url_or_list_of_urls = stream['_stream']
                if "," in stream_url_or_list_of_urls:
                    continue
                quality = stream['_quality']
                if type(stream_url_or_list_of_urls) == str:
                    res[quality].add(stream_url_or_list_of_urls)
                else:
                    for stream_url in stream_url_or_list_of_urls:
                        if "," in stream_url:
                            continue
                        res[quality].add(stream_url)
        return res

    def set_filename(self, filename):
        """
        Checks and sets the filename where the filename consists of the path *and* the filename.
        If the path does not exist yet, this method will try to build it.

        Returns the filename or None.
        """
        if not filename:
            return None
        
        self.filename = os.path.abspath(os.path.expanduser(filename))
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
    with contextlib.suppress(KeyboardInterrupt):
        amd.download()
        if args.subtitles:
            amd.get_subtitles()



if __name__ == "__main__":
    main(sys.argv)
