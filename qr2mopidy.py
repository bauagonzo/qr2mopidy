from __future__ import unicode_literals
import os
import logging
import re

from PIL import Image
import jsonrpclib
import zbar
import cv2

logging.addLevelName(5,"VERBOSE")
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=logging.getLevelName(log_level))

def get_server():
    ip_addr = os.getenv('MOPIDY_SERVER', '127.0.0.1:6680')
    logging.info('Connect to %r', ip_addr)
    # TODO patch to set headers to vim /usr/lib/python2.7/dist-packages/jsonrpclib/jsonrpc.py
    return jsonrpclib.Server('http://{}/mopidy/rpc'.format(ip_addr))


def format_timeposition(milliseconds):
    seconds = milliseconds//1000.0
    min_part = seconds // 60.0
    sec_part = seconds % 60.0
    return '{:n}:{:02n}'.format(min_part, sec_part)


def state():
    '''Get The playback state: 'playing', 'paused', or 'stopped'.

    If PLAYING or PAUSED, show information on current track.

    Calls PlaybackController.get_state(), and if state is PLAYING or PAUSED, get
      PlaybackController.get_current_track() and
      PlaybackController.get_time_position()'''

    server = get_server()
    state = server.core.playback.get_state()
    logging.debug('Got playback state: %r', state)
    if state.upper() == 'STOPPED':
        print('Playback is currently stopped')
    else:
        track = server.core.playback.get_current_track()
        logging.debug('Track is %r', track)
        logging.debug('Track loaded is %r', jsonrpclib.jsonclass.load(track))
        pos = server.core.playback.get_time_position()
        logging.debug('Pos is %r', pos)
        print('{} track: "{}", by {} (at {})'.format(state.title(),
                                                     track['name'],
                                                     ','.join([a['name'] for a in track['artists']]),
                                                     format_timeposition(pos))
              )


def play():
    '''play the currently active track.

    Calls PlaybackController.play(None, None)'''

    return get_server().core.playback.play()


def pause():
    '''Pause playback.

    Calls PlaybackController.pause()'''

    server = get_server()
    server.core.playback.pause()
    pos = server.core.playback.get_time_position()
    print('Paused at {}'.format(format_timeposition(pos)))


def resume():
    '''If paused, resume playing the current track.

    Calls PlaybackController.resume()'''

    return get_server().core.playback.resume()


def next_track():
    '''Change to the next track.

    The current playback state will be kept.
    If it was playing, playing will continue. If it was paused, it will still be paused, etc.

    Calls PlaybackController.next()'''

    return get_server().core.playback.next()


def previous_track():
    '''Change to the previous track.

    The current playback state will be kept.
    If it was playing, playing will continue. If it was paused, it will still be paused, etc.

    Calls PlaybackController.previous()'''

    return get_server().core.playback.previous()


def tracklist():
    '''Get tracklist

    Calls TracklistController.get_tl_tracks()
    '''
    _c = 0
    server = get_server()
    _current = server.core.tracklist.index()
    for track in server.core.tracklist.get_tl_tracks():
        logging.debug('Got tl track: %r', track)
        currently = ' -- CURRENT' if track['tlid'] == _current else ''
        print('{}: {}{}'.format(track['tlid'], track['track']['name'], currently))
        _c = _c+1
    print('==='*6)
    print('{} tracks in tracklist'.format(_c))


def shuffle():
    '''Shuffles the entire tracklist.

    Calls TracklistController.shuffle(start=None, end=None)'''

    return get_server().core.tracklist.shuffle()


def play_backend_uri(uri=None):
    '''Get album or track from backend uri and play all tracks found.

    uri is a string which represents some directory belonging to a backend.

    Calls LibraryController.browse(uri) to get an album and LibraryController.lookup(uri)
    to get track'''
    server = get_server()
    hits = server.core.library.lookup(uri)
    logging.info('Got hits from lookup(): %r', hits)

    if len(hits) == 0:
        print('No hits for "{}"'.format(uri))
        return
    else:
        server.core.tracklist.clear()
        logging.debug('got special uris: %r', [t['uri'] for t in hits])
        server.core.tracklist.add(uris=[t['uri'] for t in hits])
        server.core.playback.play()


def main():
    '''
    Capture webcam video utilizing OpenCV. The video is then broken down into frames which
    are constantly displayed. The frame is then converted to grayscale for better contrast. Afterwards, the image
    is transformed into a numpy array using PIL. This is needed to create zbar image. This zbar image is then scanned
    utilizing zbar's image scanner and will then print the decodeed message of any QR or bar code. To quit the program,
    press "q".
    :return:
    '''
    logging.info('starting')
    # Begin capturing video. You can modify what video source to use with VideoCapture's argument. It's currently set
    # to be your webcam.
    capture = cv2.VideoCapture(0)
    previous_control = 'play'
    while True:
        # To quit this program press q.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Breaks down the video into frames
        _, frame = capture.read()

        # Displays the current frame
        #if logging.getLogger().isEnabledFor(logging.VERBOSE):
        #    cv2.imshow('Current', frame)

        # Converts image to grayscale.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Uses PIL to convert the grayscale image into a ndary array that ZBar can understand.
        image = Image.fromarray(gray)
        width, height = image.size
        zbar_image = zbar.Image(width, height, 'Y800', image.tobytes())

        # Scans the zbar image.
        scanner = zbar.ImageScanner()
        scanner.scan(zbar_image)

        # Prints data from image.
        for decoded in zbar_image:
            logging.debug(decoded.data)
            # TODO sleep that thing
            control = decoded.data
            if control == previous_control:
                logging.debug("same control")
                continue
            else:
                logging.info('new control: %r', control)
                previous_control = control
                if control == "play":
                    play()
                elif control == "pause":
                    pause()
                elif control == "next":
                    next_track()
                elif control == "previous":
                    previous_track()
                elif re.match(r"^spotify:", control):
                    logging.info('Play spotify uri: %r', control)
                    play_backend_uri(control)


if __name__ == "__main__":
    main()
