#FROM arm32v7/python
FROM arm32v7/debian


RUN apt-get update -y && \
    apt-get install -y python python-pip libzbar0 libzbar-dev

ADD qr2mopidy.py /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY headers.patch /
RUN patch /usr/local/lib/python2.7/site-packages/jsonrpclib/jsonrpc.py headers.patch

CMD [ "python", "/qr2mopidy.py" ]
