import sys
import os
import argparse
import socket
import logging
import time
import email.utils

class HTTPServer:

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5

    def __init__(self, server_address, RequestHandlerClass, max_workers):
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.max_workers = max_workers
 
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
        MainHTTPHandler(conn)             
              
    def __enter__(self):
        return self

    def __exit__(self, *agrs):
        self.server_close()

    def server_close(self):
        self.socket.close()
        self.socket = None


class MainHTTPHandler:
   
    sys_version = "Python/" + sys.version.split()[0]
    server_version = "HTTPServer/0.1"
    protocol_version = "HTTP/1.1"

    def __init__(self, conn):
        self.conn = conn
        self.headers = []
        self.status_line = ''
        self.handle()

    def handle(self):
        data = b''
       
        while True:
            r = self.conn.recv(25)
            # r is empty if socket is closed
            if not r: 
                break
            data += r
            if data[-4:] == b'\r\n\r\n':
                break

        
        request_line = data.splitlines()[0]
        logging.info(request_line)
        
        method, location, http_version = request_line.split()
        
        self.start_response(self.protocol_version, 200, "OK")
        self.set_header("Server", self.version_string())
        self.set_header("Connection", "Close")
        self.set_header("Date", self.date_time_string())
        self.set_header("Content-Type", "text/html; charset=utf-8")
       
        answer = """<!DOCTYPE html>"""
        answer += """<html><head><title>Time</title></head><body><h1>"""
        answer += time.strftime("%H:%M:%S %d.%m.%Y")
        answer += """</h1></body></html>"""

        self.set_header("Content-Length", str(len(answer)))
        
        self.end_headers()

        response = b"".join(self.headers)

        response += answer.encode("utf-8")

        logging.info(response)

        self.conn.sendall(response)

        self.conn.close()
 

    
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

    with HTTPServer(server_address, MainHTTPHandler, args.workers) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt recieved, exiting.")
            sys.exit(0)

