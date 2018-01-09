import sys
import os
import argparse
import socket
import logging
import time
import email.utils
import urllib.parse
import posixpath
import threading

__version__ = "0.1"

# Default error message template
DEFAULT_ERROR_MESSAGE = """\
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>404 - Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <p>Message: %(message)s</p>
    </body>
</html>
"""

DEFAULT_ERROR_CONTENT_TYPE = "text/html;charset=utf-8"


class HTTPServer:

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5

    def __init__(self, server_address, RequestHandlerClass,
                 max_workers,
                 document_root):

        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.max_workers = max_workers
        self.document_root = document_root
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

        self.socket.listen(self.request_queue_size)

    def serve_forever(self):
        logging.info("Server is running on {0}".format(self.server_address))
        print("\nPress Ctrl+C to shut down server")
        for _ in range(self.max_workers):
            client_handler = threading.Thread(
                target=self.handle_client_connection)
            client_handler.start()

    def handle_client_connection(self):
        while True:
            conn, client_address = self.socket.accept()
            logging.info("Recived connection {0}".format(client_address))
            self.process_request(conn)

    def process_request(self, conn):
        MainHTTPHandler(conn, self.document_root)

    def __enter__(self):
        return self

    def __exit__(self, *agrs):
        self.server_close()

    def server_close(self):
        #self.socket.close()
        #self.socket = None
        pass


class MainHTTPHandler:
    """
    The order to create a response:
        1. call start_response
        2. call set_header (a function to set one header)
        3. call end_headers
        3. set value of self.body
        3. call build_response
        4. call send_response

    """

    extensions_map = {
        '': 'application/octet-stream',
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'text/javascript',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.swf': 'application/x-shockwave-flash',
    }

    sys_version = "Python/" + sys.version.split()[0]
    server_version = "HTTPServer/" + __version__
    protocol_version = "HTTP/1.1"
    error_message = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    def __init__(self, conn, document_root):
        self.conn = conn
        self.document_root = document_root
        self.headers = []
        self.response = b""
        self.body = b""
        self.handle()

    def handle(self):
        try:
            self.read_request()
        except Exception:
            self.send_error(400, 'Bad Request')
            return

        logging.info("Request line: {0}".format(self.request_line))
        try:
            self.parse_request()
        except Exception:
            self.send_error(400, 'Bad Request')
            return

        logging.info("method:{0}, location:{1}, version:{2}".format
                     (self.method, self.location, self.protocol_version))

        if self.method in ('GET', 'HEAD'):
            self.process_location()
        else:
            self.send_error(405, 'Method Not Allowed')

    def process_location(self):
        """Common code for GET and HEAD commands"""
        path = self.translate_path(self.location)
        logging.info("Path: {0}".format(path))
        f = None
        if os.path.isdir(path):
            index = os.path.join(path, "index.html")
            if os.path.exists(index):
                path = index
                logging.info("Path after edit: {0}".format(path))
            else:
                self.send_error(403, 'Forbidden')
                return

        mimetype = self.get_mimetype(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, 'File not found')
            return
        try:
            self.start_response(self.protocol_version, 200, 'OK')
            self.set_header("Content-Type", mimetype)
            fs = os.fstat(f.fileno())
            self.set_header("Content-Length", str(fs[6]))
            self.end_headers()
            if self.method == 'GET':
                self.body = f.read()
            self.build_response()
            self.send_response()
            f.close()
        except Exception:
            f.close()
            raise

    def get_mimetype(self, path):
        """Guess mimetype of a file by its extension."""
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    def build_response(self):
        """Join request line, list of headers and body into binary string"""
        self.response = b"".join(self.headers)
        if self.body:
            self.response += self.body

    def send_response(self):
        """Send rensponse and close client socket"""
        logging.info("Response first line: {0}".format(self.headers[0]))
        self.conn.sendall(self.response)
        self.conn.close()

    def send_error(self, code, message):
        """Send an error replay.

        Arguments are
        * code: an HTTP error code 3 digits
        * message: one line reason phrase

        """
        self.start_response(self.protocol_version, code, message)
        content = (self.error_message % {
            'code': code,
            'message': message,
        })
        self.body = content.encode('utf-8', 'replace')
        self.set_header("Content-Length", str(len(self.body)))
        self.set_header("Content-Type", self.error_content_type)
        self.end_headers()
        self.build_response()
        self.send_response()

    def read_request(self):
        """Read request from the client socket"""
        data = b''
        while True:
            r = self.conn.recv(25)
            # r is empty if socket is closed
            if not r:
                break
            data += r
            if data[-4:] == b'\r\n\r\n':
                break

        self.request_line = data.splitlines()[0]

    def parse_request(self):
        """Parse a request.
        The request should be stored in self.raw_requestline; the results
        are in self.method, self.location, self.protocol_version."""
        self.method, self.location, self.http_version = \
            self.request_line.decode("utf-8").split()

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax."""
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]

        trailing_slash = path.rstrip().endswith('/')
        path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = self.document_root
        for word in words:
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    def start_response(self, http_version, code, message):
        self.headers.append(("%s %d %s\r\n" % (http_version, code,
                                               message)).encode("utf-8"))
        self.set_header("Server", self.version_string())
        self.set_header("Connection", "Close")
        self.set_header("Date", self.date_time_string())

    def set_header(self, keyword, value):
        self.headers.append(("%s: %s\r\n" % (keyword, value)).encode("utf-8"))

    def end_headers(self):
        self.headers.append(b"\r\n")

    def date_time_string(self, timestamp=None):
        """Return the current date and time formatted for a message header."""
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    def version_string(self):
        """Return the server software version string."""
        return self.server_version + ' ' + self.sys_version


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port',
        '-p',
        type=int,
        default=80,
        help='Specify alternate port [default: 8000]'
    )
    parser.add_argument(
        '--bind',
        '-b',
        default='',
        help='Specify alternate bind address '
        '[default:all interfaces]')

    base_dir = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument(
        '--root',
        '-r',
        default=base_dir,
        help='Specify document root')

    parser.add_argument(
        '--log',
        '-l',
        default=None,
        help='Specify path for logfile'
    )

    parser.add_argument(
        '--workers',
        '-w',
        type=int,
        default=10,
        help='Specify max value of workers'
     )

    args = parser.parse_args()
    server_address = (args.bind, args.port)

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
        filename=args.log
    )

    with HTTPServer(server_address,
                    MainHTTPHandler,
                    args.workers,
                    args.root) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt recieved, exiting.")
            sys.exit(0)
