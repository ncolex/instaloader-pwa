#!/usr/bin/env python3
"""
Simple HTTP server for serving the PWA
"""

import http.server
import socketserver
import os
from functools import partial

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def serve_pwa(port=8080, directory='instaloader_pwa'):
    handler = partial(CORSHandler, directory=directory)
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving PWA at http://localhost:{port}")
        print(f"Serving from directory: {os.path.join(os.getcwd(), directory)}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    serve_pwa(port)