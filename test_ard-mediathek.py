import pytest
import ard_media_downloader
import json


_URL = "https://www.ardmediathek.de/tv/NaturNah/Der-%C3%96-Kuh-Hof/NDR-Fernsehen/Video?bcastId=14049240&documentId=48330046"

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

@pytest.fixture(scope="session")
def downloader():
    yield ard_media_downloader.ArdMediathekDownloader(_URL)

@pytest.fixture(scope="session")
def media_json():
    response = '{"_type":"video","_isLive":false,"_defaultQuality":["auto",2,4,3,1,0],"_previewImage":"https://img.ardmediathek.de/standard/00/56/74/70/90/2121327408/16x9/960?mandant=ard","_subtitleUrl":"https://www.ardmediathek.de/subtitle/259489","_subtitleOffset":0,"_mediaArray":[{"_plugin":0,"_mediaStreamArray":[{"_quality":"auto","_server":"","_cdn":"akamai","_stream":"https://dasersteuni-vh.akamaihd.net/z/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/,640-1,512-1,960-1,.mp4.csmil/manifest.f4m"},{"_quality":2,"_server":"","_cdn":"akamai","_width":640,"_height":360,"_stream":"https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/640-1.mp4"}]},{"_plugin":1,"_mediaStreamArray":[{"_quality":"auto","_stream":["https://dasersteuni-vh.akamaihd.net/i/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/,640-1,512-1,320-1,480-1,960-1,1280-1,.mp4.csmil/master.m3u8","https://dasersteuni-vh.akamaihd.net/i/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/,640-1,512-1,320-1,480-1,960-1,.mp4.csmil/master.m3u8"]},{"_quality":0,"_server":"","_cdn":"akamai","_stream":"https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/320-1.mp4"},{"_quality":1,"_stream":["https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/512-1.mp4","https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/480-1.mp4"]},{"_quality":2,"_stream":["https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/640-1.mp4","https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/960-1.mp4"]},{"_quality":3,"_server":"","_cdn":"akamai","_width":960,"_height":540,"_stream":"https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/960-1.mp4"}]}],"_alternativeMediaArray":[],"_sortierArray":[1,0],"_duration":5310,"_dvrEnabled":false,"_geoblocked":false}'
    yield json.loads(response)


@pytest.mark.parametrize("quality, expected_url", [
    (1, "https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/512-1.mp4"),
    (2, "https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/640-1.mp4"),
    (3, "https://pdvideosdaserste-a.akamaihd.net/int/2018/10/01/d5d97d8f-15e1-40cf-94f3-bf113577a01a/960-1.mp4"),
])
def test_read_streams(downloader, media_json, quality, expected_url):
    downloader.set_quality(quality)
    url = downloader._get_video_url(media_json)
    assert url == expected_url
