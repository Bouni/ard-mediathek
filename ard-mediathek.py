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
