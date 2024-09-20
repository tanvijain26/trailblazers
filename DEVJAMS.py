import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import urllib.parse

UPLOAD_DIR = "uploads"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _render_page(self, content):
        """Helper method to generate HTML with Bootstrap."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <title>MyEvents</title>
            <style>
                body {{
                    background-color: #f4f4f4;
                    font-family: Arial, sans-serif;
                }}
                h2 {{
                    margin-top: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    background: #fff;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    color: #888;
                }}
                a {{
                    color: #007bff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center">MyEvents</h1>
                {content}
            </div>
            <div class="footer">
                <p>&copy; 2024 Python Server | Designed with ❤️</p>
            </div>
        </body>
        </html>"""
        self.wfile.write(html.encode())

    def do_GET(self):
        """Handle GET requests for different endpoints."""
        if self.path == "/":
            # Main page with navigation
            self._render_page("""
            <h2></h2>
            <ul class="list-group">
                <li class="list-group-item"><a href='/upload'>Upload Reel</a></li>
                <li class="list-group-item"><a href='/chat'>Chat Room</a></li>
                <li class="list-group-item"><a href='/events'>Upcoming Events</a></li>
            </ul>
            """)
        elif self.path == "/upload":
            # Upload form with Bootstrap
            self._render_page("""
            <h2>Upload a Reel</h2>
            <form enctype="multipart/form-data" method="POST" action="/upload">
                <div class="form-group">
                    <label>Select video file to upload</label>
                    <input type="file" class="form-control-file" name="file">
                </div>
                <button type="submit" class="btn btn-primary btn-block">Upload</button>
            </form>
            <a href="/" class="btn btn-secondary btn-block mt-3">Go Back</a>
            """)
        elif self.path == "/chat":
            # Chat room page
            self._render_page("""
            <h2>Chat Room</h2>
            <form method="POST" action="/chat">
                <div class="form-group">
                    <input type="text" class="form-control" name="message" placeholder="Enter your message">
                </div>
                <button type="submit" class="btn btn-primary btn-block">Send</button>
            </form>
            <h3>Chat History</h3>
            <ul class="list-group">
                <li class="list-group-item">User1: Hello</li>
                <li class="list-group-item">User2: Hi there!</li>
            </ul>
            <a href="/" class="btn btn-secondary btn-block mt-3">Go Back</a>
            """)
        elif self.path == "/events":
            # Static events page
            self._render_page("""
            <h2>Upcoming Events</h2>
            <ul class="list-group">
                <li class="list-group-item">Python Workshop - Sept 25</li>
                <li class="list-group-item">Web Development Bootcamp - Oct 10</li>
            </ul>
            <a href="/" class="btn btn-secondary btn-block mt-3">Go Back</a>
            """)

    def do_POST(self):
        """Handle POST requests for file uploads and chat messages."""
        if self.path == "/upload":
            # Handle file upload
            content_type, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if content_type == 'multipart/form-data':
                form_data = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                file_item = form_data['file']

                # Save the file
                if file_item.filename:
                    file_path = os.path.join(UPLOAD_DIR, file_item.filename)
                    with open(file_path, 'wb') as f:
                        f.write(file_item.file.read())

                    self._render_page(f"""
                    <h2>Upload Successful!</h2>
                    <p>File saved as: {file_item.filename}</p>
                    <a href='/upload' class="btn btn-success btn-block">Upload another file</a>
                    """)
                else:
                    self._render_page("""
                    <h2>Upload Failed!</h2>
                    <p>No file provided.</p>
                    <a href='/upload' class="btn btn-danger btn-block">Try again</a>
                    """)
        
        elif self.path == "/chat":
            # Handle chat message
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()

            # Use urllib.parse instead of cgi to parse the POST data
            parsed_data = urllib.parse.parse_qs(post_data)
            message = parsed_data.get('message', [''])[0]

            # For simplicity, print message to console (or save it to a file)
            print(f"New chat message: {message}")

            self._render_page(f"""
            <h2>Chat Room</h2>
            <form method="POST" action="/chat">
                <div class="form-group">
                    <input type="text" class="form-control" name="message" placeholder="Enter your message">
                </div>
                <button type="submit" class="btn btn-primary btn-block">Send</button>
            </form>
            <h3>Chat History</h3>
            <ul class="list-group">
                <li class="list-group-item">You: {message}</li>
                <li class="list-group-item">User1: Hello</li>
                <li class="list-group-item">User2: Hi there!</li>
            </ul>
            <a href="/" class="btn btn-secondary btn-block mt-3">Go Back</a>
            """)

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    """Run the server."""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()