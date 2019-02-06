
# QR 2 Modipy

This project aims to create a jukebox based of :

* Raspberry pi with its camera
* Modipy for as audio source
* Cards with QR code to encode Spotify URI of the songs to be played

# Installation

The installation steps assumes you are on Raspbian or a Debian flavor

## Mopidy

In order to install modipy refer to the official doc and setup spotify plugin

## Python dependencies
Install python depencies from the OS
```sudo apt-get install python-jsonrpclib python-opencv python-pil python-zbar```

# Run the application
To run the service with
```
python qr2mopidy.py
```

Or install [qr2mopidy.service](qr2mopidy.service) with systemd.

Or run the service in a container
```
docker run --device=/dev/video0:/dev/video0 \
    --env="LOG_LEVEL=DEBUG" \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" qr2modipy
```

Also, a [docker-compose file](docker-compose.yml) is provided and works with : https://github.com/bauagonzo/docker-mopidy
# TODO

* Classify code to request Modipy
* Add control to add a song to the playlist
* Capture errors (missing webcam, HTTP issues, etc.)
* Monkey patch jsonrpclib

# Sources

The source code is heavily inspired from https://github.com/havardgulldahl/mopidycli & https://github.com/allenywang/Real-Time-QR-Recognizer-Reader-and-Decoder

To generate the QR codes I personnaly used : https://www.qrcode-monkey.com/
