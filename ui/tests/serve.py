"""Serve the UI test build quietly: python ui/tests/serve.py PORT FOLDER."""

import functools
import http.server
import sys


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


port, folder = int(sys.argv[1]), sys.argv[2]
handler = functools.partial(Quiet, directory=folder)
http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
