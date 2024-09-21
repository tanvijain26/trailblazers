import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
from urllib.parse import parse_qs

UPLOAD_DIR = "uploads"

# Simulated user database
USER_CREDENTIALS = {
    'testuser': 'password123'
}

# Simulated session store for logged-in users
LOGGED_IN_USERS = {}

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

    def _is_logged_in(self):
        """Check if the user is logged in by checking cookies."""
        cookies = self.headers.get('Cookie')
        if cookies:
            username = cookies.split('=')[1]
            if username in LOGGED_IN_USERS:
                return username
        return None

    def do_GET(self):
        """Handle GET requests for different endpoints."""
        username = self._is_logged_in()

        if self.path == "/":
            # Main page with options
            if username:
                content = f"""
                <h2>Welcome, {username}!</h2>
                <ul class="list-group">
                    <li class="list-group-item"><a href='/upload'>Upload a Reel</a></li>
                    <li class="list-group-item"><a href='/chat'>Chat Room</a></li>
                    <li class="list-group-item"><a href='/events'>Upcoming Events</a></li>
                    <li class="list-group-item"><a href='/logout'>Logout</a></li>
                </ul>
                """
            else:
                content = """
                <h2>Please Login or Sign Up to Access Features</h2>
                <ul class="list-group">
                    <li class="list-group-item"><a href='/login'>Login</a></li>
                    <li class="list-group-item"><a href='/signup'>Sign Up</a></li>
                </ul>
                """
            self._render_page(content)

        elif self.path == "/login":
            self._render_page("""
            <h2>Login</h2>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" class="form-control" name="username" id="username" placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" class="form-control" name="password" id="password" placeholder="Enter password">
                </div>
                <button type="submit" class="btn btn-primary btn-block">Login</button>
            </form>
            """)

        elif self.path == "/signup":
            self._render_page("""
            <h2>Sign Up</h2>
            <form method="POST" action="/signup">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" class="form-control" name="username" id="username" placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" class="form-control" name="password" id="password" placeholder="Enter password">
                </div>
                <button type="submit" class="btn btn-primary btn-block">Sign Up</button>
            </form>
            """)

        elif self.path == "/upload":
            if not username:
                self._render_page("<h2 class='error'>You must be logged in to access this feature.</h2><a href='/login'>Login</a>")
            else:
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
            if not username:
                self._render_page("<h2 class='error'>You must be logged in to access this feature.</h2><a href='/login'>Login</a>")
            else:
                self._render_page("""
                <h2>Chat Room</h2>
                <form method="POST" action="/chat">
                    <div class="form-group">
                        <input type="text" class="form-control" name="message" placeholder="Enter your message">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Send</button>
                </form>
                <h3>Chat History</h3>
                <ul class="list-group" id="chat-history"></ul>
                <a href="/" class="btn btn-secondary btn-block mt-3">Go Back</a>
                """)

        elif self.path == "/events":
            self._render_page("""
            <h2>Upcoming Events</h2>
            <ul class="list-group">
                <li class="list-group-item">Python Workshop - Sept 25</li>
                <li class="list-group-item">Web Development Bootcamp - Oct 10</li>
            </ul>
            <a href="/" class="btn btn-secondary btn-block mt-3">Go Back</a>
            """)

        elif self.path == "/logout":
            if username:
                LOGGED_IN_USERS.pop(username)
                self.send_response(302)
                self.send_header('Set-Cookie', 'username=; expires=Thu, 01 Jan 1970 00:00:00 GMT')
                self.send_header('Location', '/')
                self.end_headers()

    def do_POST(self):
        """Handle POST requests for login, signup, file uploads, and chat."""
        if self.path == "/login":
            # Handle login
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data = parse_qs(post_data)

            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            # Validate user credentials
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                LOGGED_IN_USERS[username] = True
                self.send_response(302)
                self.send_header('Set-Cookie', f'username={username}')
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self._render_page("<h2 class='error'>Login Failed</h2><p>Invalid username or password.</p><a href='/login'>Try again</a>")

        elif self.path == "/signup":
            # Handle signup
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data = parse_qs(post_data)

            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            # Check if username is taken
            if username in USER_CREDENTIALS:
                self._render_page("<h2 class='error'>Signup Failed</h2><p>Username already exists. Please choose another.</p><a href='/signup'>Try again</a>")
            else:
                USER_CREDENTIALS[username] = password
                LOGGED_IN_USERS[username] = True
                self.send_response(302)
                self.send_header('Set-Cookie', f'username={username}')
                self.send_header('Location', '/')
                self.end_headers()

        elif self.path == "/upload":
            # Handle file upload
            if not self._is_logged_in():
                self.send_response(403)
                self.end_headers()
                return

            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            if 'file' in form:
                fileitem = form['file']
                if fileitem.filename:
                    filepath = os.path.join(UPLOAD_DIR, os.path.basename(fileitem.filename))
                    with open(filepath, 'wb') as f:
                        f.write(fileitem.file.read())
                    self._render_page("<h2>Upload Successful</h2><a href='/'>Go Home</a>")
                else:
                    self._render_page("<h2 class='error'>No file was uploaded.</h2><a href='/upload'>Try again</a>")

        elif self.path == "/chat":
            if not self._is_logged_in():
                self.send_response(403)
                self.end_headers()
                return
            
            # Handle chat message
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data = parse_qs(post_data)

            message = post_data.get('message', [''])[0]
            # Here you would append the message to a chat history or handle accordingly.

            # Respond with a success message or refresh the chat page
            self._render_page("<h2>Message Sent!</h2><a href='/chat'>Back to Chat</a>")

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
