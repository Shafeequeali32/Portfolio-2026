import http.server
import socketserver
import os
import sys

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SPAHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Resolve path
        clean_path = self.path.split('?')[0].split('#')[0]
        file_path = os.path.join(DIRECTORY, clean_path.lstrip('/'))
        
        # If path is a SPA route and not a physical asset, serve index.html
        if not os.path.exists(file_path) and not '.' in os.path.basename(clean_path):
            self.path = '/index.html'
            
        return super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        if self.path.endswith('.jpg') or self.path.endswith('.jpeg') or self.path.endswith('.png') or self.path.endswith('.webp'):
            self.send_header('Cache-Control', 'public, max-age=86400')
        else:
            self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, format, *args):
        # Keep image logs quiet
        if args and any(arg.endswith('.jpg') for arg in str(args[0]).split()):
            return
        super().log_message(format, *args)

def run_server():
    port = PORT
    for attempt in range(5):
        try:
            with socketserver.TCPServer(("", port), SPAHTTPHandler) as httpd:
                print(f"SERVER_READY:http://localhost:{port}", flush=True)
                httpd.serve_forever()
        except OSError as e:
            if "address already in use" in str(e).lower() or e.errno in (48, 98, 10048):
                port += 1
            else:
                raise e

if __name__ == '__main__':
    run_server()
