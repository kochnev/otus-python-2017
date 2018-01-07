import sys
import os
import argparse
import socket
import logging
import time
import email.utils
import urllib.parse
import posixpath

__version__ = "0.1"

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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.socket.bind(self.server_address)

        self.socket.listen(self.request_queue_size)

    def serve_forever(self):
        logging.info("Server is running on {0}".format(self.server_address))
        print("\nPress Ctrl+C to shut down server")
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
        self.socket.close()
        self.socket = None


class MainHTTPHandler:
    extensions_map = {
        '.html': 'text/html',
    }

    sys_version = "Python/" + sys.version.split()[0]
    server_version = "HTTPServer/" + __version__
    protocol_version = "HTTP/1.1"

    def __init__(self, conn, document_root):
        self.conn = conn
        self.document_root = document_root
        self.headers = []
        self.response = b""
        self.body = b""
        self.handle()

    def handle(self):
        self.read_request()
        logging.info(self.request_line)

        self.parse_request()
        logging.info("method:{0}, location:{1}, version:{2}".format
                     (self.method, self.location, self.protocol_version))

        if self.method == 'GET':
            f = self.process_location()
            if f:
                try:
                    self.body = f.read()
                finally:
                    f.close()

        elif self.method == 'HEAD':
            f = self.process_location()
            if f:
                f.close()
        else:
            self.start_response(self.protocol_version, 405, 'Method Not \
                                Allowed')
            self.end_headers()

        

        logging.info(self.response)
        self.build_response()
        self.send_response()
    
    def process_location(self):
        """Common code for GET and HEAD commands"""

        path = self.translate_path(self.location)
        logging.info(path)
        f = None
        if os.path.isdir(path):
            index = os.path.join(path, "index.html")
            if os.path.exists(index):
                path = index
        logging.info(path) 
        mimetype = self.get_mimetype(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.start_response(self.protocol_version, 404, 'File not found')
            self.end_headers()
            self.build_response()
            self.send_response()
            return None
        try:
            self.start_response(self.protocol_version, 200, 'OK')
            self.set_header("Server", self.version_string())
            self.set_header("Connection", "Close")
            self.set_header("Date", self.date_time_string())
            self.set_header("Content-Type", mimetype)
            fs = os.fstat(f.fileno())
            self.set_header("Content-Length", str(fs[6]))
            self.end_headers()
            return f
        except Exception:
            f.close()
            raise

    def get_mimetype(self, path):
        """Guess mimetype of a file by its extension."""
        base, ext = posixpath.splitext(path)
        return self.extensions_map[ext]

    def build_response(self):
        self.response = b"".join(self.headers)
        if self.body:
            self.response += self.body

    def send_response(self):
        self.conn.sendall(self.response)
        self.conn.close()
    
    def read_request(self):
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

        path = path.split('?',1)[0]
        path = path.split('#',1)[0]

        trailing_slash = path.rstrip().endswith('/')
        path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
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
        default=8000,
        help='Specify alternate port [default: 8000]'
    )
    parser.add_argument(
        '--bind',
        '-b',
        default='',
        help='Specify alternate bind address '
        '[default:all interfaces]')

    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(base_dir)
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
        default=3,
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

    with HTTPServer(server_address, MainHTTPHandler, args.workers, args.root) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt recieved, exiting.")
            sys.exit(0)
