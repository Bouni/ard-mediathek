import json

import pytest

import ard_media_downloader

_URL = "https://www.ardmediathek.de/tv/Babylon-Berlin/Folge-10/Das-Erste/Video?bcastId=54319834&documentId=57001826"


@pytest.mark.parametrize("url,expected", [
    (_URL, False),
    ("http:/google.de", True),
    ("", True),
    ("asdasd", True),
])
def test_validate_url(url, expected):
    if expected:
        with pytest.raises(ValueError):
            ard_media_downloader.ArdMediathekDownloader(url)
    else:
        ard_media_downloader.ArdMediathekDownloader(url)


@pytest.mark.vcr()
@pytest.fixture()
def downloader():
    yield ard_media_downloader.ArdMediathekDownloader(url=_URL)


@pytest.fixture()
def media_json():
    response = '{"_type":"video","_isLive":false,"_defaultQuality":["auto",2,4,3,1,0],"_previewImage":"https://img.ardmediathek.de/standard/00/56/74/70/90/2121327408/16x9/960?mandant=ard","_subtitleUrl":"https://www.ardmediathek.de/subtitle/259489","_subtitleOffset":0,"_mediaArray":[{"_plugin":0,"_mediaStreamArray":[{"_quality":"auto","_server":"","_cdn":"akamai","_stream":"https://dasersteuni-vh.akamaihd.net/z/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/,640-1,512-1,960-1,.mp4.csmil/manifest.f4m"},{"_quality":2,"_server":"","_cdn":"akamai","_width":640,"_height":360,"_stream":"https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/640-1.mp4"}]},{"_plugin":1,"_mediaStreamArray":[{"_quality":"auto","_stream":["https://dasersteuni-vh.akamaihd.net/i/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/,640-1,512-1,320-1,480-1,960-1,1280-1,.mp4.csmil/master.m3u8","https://dasersteuni-vh.akamaihd.net/i/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/,640-1,512-1,320-1,480-1,960-1,.mp4.csmil/master.m3u8"]},{"_quality":0,"_server":"","_cdn":"akamai","_stream":"https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/320-1.mp4"},{"_quality":1,"_stream":["https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/512-1.mp4","https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/480-1.mp4"]},{"_quality":2,"_stream":["https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/640-1.mp4","https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/960-1.mp4"]},{"_quality":3,"_server":"","_cdn":"akamai","_width":960,"_height":540,"_stream":"https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/960-1.mp4"}]}],"_alternativeMediaArray":[],"_sortierArray":[1,0],"_duration":5310,"_dvrEnabled":false,"_geoblocked":false}'
    yield json.loads(response)


@pytest.mark.parametrize("quality, expected_url", [
    (1, "https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/512-1.mp4"),
    (2, "https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/640-1.mp4"),
    (3, "https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/960-1.mp4"),
])
@pytest.mark.vcr()
def test_read_streams(downloader, media_json, quality, expected_url):
    downloader.quality = quality
    url = downloader._get_video_url(media_json)
    assert url == expected_url


_URL_PREFIX = "https://pdvideosdaserste-a.akamaihd.net/de/2018/10/01/bbf4b89c-9a7c-4f33-ade5-2e12d36df44d/"


@pytest.mark.vcr()
@pytest.mark.parametrize("quality, expected_url", [
    (1, _URL_PREFIX + "640-1.mp4"),
    (2, _URL_PREFIX + "960-1.mp4"),
    (3, _URL_PREFIX + "1280-1.mp4"),
])
def test_quality_yields_correct_url(downloader, quality, expected_url):
    downloader.quality = quality
    url = downloader.get_video_url()
    assert url == expected_url


def test_filename_default(downloader):
    downloader._determine_filename()
    assert downloader.filename.endswith("video.mp4")


def test_filename_derived(downloader):
    downloader.derive_filename = True
    downloader._determine_filename()
    assert downloader.filename.endswith("folge-10.mp4")

def test_filename_given(downloader):
    downloader.filename = "babylon-berlin.mp4"
    downloader._determine_filename()
    assert downloader.filename.endswith("babylon-berlin.mp4")