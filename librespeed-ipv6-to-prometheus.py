#!/usr/bin/python3

import subprocess
from subprocess import PIPE
import json

from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from random import randrange
import time
import timeit
from urllib.parse import parse_qs, urlparse
import threading

import sys

from prometheus_client import start_http_server
from prometheus_client import Counter, Summary, Gauge

def data():

    while True:

        global ping
        #global download
        #global upload

        speedtest = subprocess.run("/usr/local/bin/librespeed_speedtest-cli/librespeed-cli --json --share --chunks 1000 --timeout 60 --secure --local-json /usr/local/bin/librespeed_speedtest-cli/custom-sv-ipv6.json --telemetry-json /usr/local/bin/librespeed_speedtest-cli/telemetry.json", shell=True, stdout=PIPE, stderr=PIPE, text=True)
        speedtest_result = speedtest.stdout
        #Debug print
        #print('{}'.format(speedtest_json)

        speedtest_json = json.loads(speedtest_result)

        #Debug print
        #print(speedtest_json)

        #data get and input
        ping = speedtest_json['ping']
        download = speedtest_json['download']
        upload = speedtest_json['upload']

        #Debug print
        print(ping)
        print(download)
        print(upload)

        ping_gauge.set(ping)
        download_gauge.set(download)
        upload_gauge.set(upload)

        time.sleep(300)

ping_gauge = Gauge('my_home_internet_ping_inonius_ipv6', 'My Home Internet Ping')
download_gauge = Gauge('my_home_internet_download_inonius_ipv6', 'My Home Internet Download')
upload_gauge = Gauge('my_home_internet_upload_inonius_ipv6', 'My Home Internet Upload')

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path.endswith('/error'):
            raise Exception('Error')

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'Hello World!! from {self.path} as GET'.encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path.endswith('/error'):
            raise Exception('Error')

        content_length = int(self.headers['content-length'])
        body = self.rfile.read(content_length).decode('utf-8')

        print(f'body = {body}')

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'Hello World!! from {self.path} as POST'.encode('utf-8'))

if __name__ == '__main__':
    thread_1 = threading.Thread(target=data)
    thread_1.start()
    start_http_server(8002)

    with ThreadingHTTPServer(('0.0.0.0', 8082), MyHTTPRequestHandler) as server:
        print(f'[{datetime.now()}] Server startup.')
        server.serve_forever()
