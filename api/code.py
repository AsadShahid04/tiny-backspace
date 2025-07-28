from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.code_processor import CodeProcessor
from app.api.routes import CodeRequest

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/code':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Create request object
                request = CodeRequest(
                    github_url=request_data['repoUrl'],
                    prompt=request_data['prompt']
                )
                
                # Set response headers
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                # Process the request
                processor = CodeProcessor()
                for update in processor.process_code_request(request):
                    self.wfile.write(f"data: {json.dumps(update)}\n\n".encode('utf-8'))
                    self.wfile.flush()
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 