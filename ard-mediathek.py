#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import contextlib
import sys

from ard_media_downloader import ArdMediathekDownloader

VERSION = "1.1"



def main(argv):
    parser = argparse.ArgumentParser(description='Commandline python script tool to download videos from the online ARD mediathek. Version: %s' % VERSION)

    parser.add_argument('url', type=str, help='URL pointing to the mediathek video')
    parser.add_argument('--filename', '-f', type=str, default=None, help='target filename')
    parser.add_argument('--quality', '-q', type=int, help='set the desired video quality', default=3, choices=[1,2,3])
    parser.add_argument('--subtitles', '-ut', action = "store_true", help='download subtitle in srt format')
    parser.add_argument('--derivefilename', '-dft', action="store_true", default=False, help='Get the video title from the video')

    args = parser.parse_args()

    if "documentId" not in args.url:
        print("ERROR: The URL does not contain a documentId. Start searching your video from "
            "http://mediathek.daserste.de/ to get an URL with documentId.")
        return

    amd = ArdMediathekDownloader(args.url)
    amd.filename = args.filename
    amd.quality = args.quality
    amd.derive_filename = args.derivefilename
    with contextlib.suppress(KeyboardInterrupt):
        amd.download()
        if args.subtitles:
            amd.get_subtitles()



if __name__ == "__main__":
    main(sys.argv)
