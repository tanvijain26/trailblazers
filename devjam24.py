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

    def _render_page(self, title, content):
        """Helper method to generate a beautiful HTML page with CSS."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 0;
                }}
                header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 1rem;
                    text-align: center;
                }}
                main {{
                    margin: 2rem;
                    padding: 1rem;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                h1, h2 {{
                    color: #333;
                }}
                a {{
                    text-decoration: none;
                    color: #4CAF50;
                }}
                ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                li {{
                    margin: 10px 0;
                }}
                input[type="file"], input[type="text"], input[type="password"], textarea {{
                    width: 100%;
                    padding: 10px;
                    margin: 8px 0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
                button {{
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    text-align: center;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
                .error {{
                    color: red;
                }}
                .success {{
                    color: green;
                }}
            </style>
        </head>
        <body>
            <header>
                <h1>{title}</h1>
            </header>
            <main>
                {content}
            </main>
        </body>
        </html>
        """
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
                <ul>
                    <li><a href='/upload'>Upload a Reel</a></li>
                    <li><a href='/chat'>Join the Chat Room</a></li>
                    <li><a href='/events'>View Upcoming Events</a></li>
                    <li><a href='/logout'>Logout</a></li>
                </ul>
                """
            else:
                content = """
                <h2>Please Login or Sign Up to Access Features</h2>
                <ul>
                    <li><a href='/login'>Login</a></li>
                    <li><a href='/signup'>Sign Up</a></li>
                </ul>
                """
            self._render_page("Welcome to Python Web App", content)
        
        elif self.path == "/login":
            self._render_page("Login", """
            <h2>Login</h2>
            <form method="POST" action="/login">
                <label for="username">Username:</label><br>
                <input type="text" name="username" id="username" placeholder="Enter username"><br>
                <label for="password">Password:</label><br>
                <input type="password" name="password" id="password" placeholder="Enter password"><br>
                <button type="submit">Login</button>
            </form>
            """)

        elif self.path == "/signup":
            self._render_page("Sign Up", """
            <h2>Sign Up</h2>
            <form method="POST" action="/signup">
                <label for="username">Username:</label><br>
                <input type="text" name="username" id="username" placeholder="Enter username"><br>
                <label for="password">Password:</label><br>
                <input type="password" name="password" id="password" placeholder="Enter password"><br>
                <button type="submit">Sign Up</button>
            </form>
            """)

        elif self.path == "/upload":
            if not username:
                self._render_page("Access Denied", "<h2 class='error'>You must be logged in to access this feature.</h2><a href='/login'>Login</a>")
            else:
                self._render_page("Upload a Reel", """
                <h2>Upload a File</h2>
                <form enctype="multipart/form-data" method="POST" action="/upload">
                    <input type="file" name="file"><br>
                    <button type="submit">Upload</button>
                </form>
                """)

        elif self.path == "/chat":
            if not username:
                self._render_page("Access Denied", "<h2 class='error'>You must be logged in to access this feature.</h2><a href='/login'>Login</a>")
            else:
                self._render_page("Chat Room", """
                <h2>Chat Room</h2>
                <form method="POST" action="/chat">
                    <input type="text" name="message" placeholder="Your message"><br>
                    <button type="submit">Send</button>
                </form>
                """)
        
        elif self.path == "/events":
            # Upcoming events (for now, static content)
            self._render_page("Upcoming Events", """
            <h2>Upcoming Events</h2>
            <ul>
                <li>Event 1: Python Workshop - Sept 25</li>
                <li>Event 2: Web Development Bootcamp - Oct 10</li>
            </ul>
            """)

        elif self.path == "/logout":
            if username:
                LOGGED_IN_USERS.pop(username)
                self.send_response(302)
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
                self._render_page("Login Failed", """
                <h2 class="error">Login Failed</h2>
                <p>Invalid username or password.</p>
                <a href="/login">Try again</a>
                """)

        elif self.path == "/signup":
            # Handle signup
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data = parse_qs(post_data)

            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            # Check if username is taken
            if username in USER_CREDENTIALS:
                self._render_page("Signup Failed", """
                <h2 class="error">Signup Failed</h2>
                <p>Username already exists. Please choose another.</p>
                <a href="/signup">Try again</a>
                """)
            else:
                USER_CREDENTIALS[username] = password
                LOGGED_IN_USERS[username] = True
                self.send_response(302)
                self.send_header('Set-Cookie', f'username={username}')
                self.send_header('Location', '/')
                self.end_headers()

        elif self.path == "/upload":
            # Handle file upload
            username = self._is_logged_in()
            if not username:
                self._render_page("Access Denied", "<h2 class='error'>You must be logged in to access this feature.</h2><a href='/login'>Login</a>")
                return

            content_type, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if content_type == 'multipart/form-data':
                form_data = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                uploaded_file = form_data['file']

                if uploaded_file.filename:
                    file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.file.read())
                    self._render_page("File Uploaded", f"<h2 class='success'>File '{uploaded_file.filename}' uploaded successfully!</h2>")
                else:
                    self._render_page("Upload Failed", "<h2 class='error'>No file selected for upload.</h2>")

        elif self.path == "/chat":
            # Handle chat message submission
            username = self._is_logged_in()
            if not username:
                self._render_page("Access Denied", "<h2 class='error'>You must be logged in to access this feature.</h2><a href='/login'>Login</a>")
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data = parse_qs(post_data)

            message = post_data.get('message', [''])[0]
            self._render_page("Chat Room", f"<h2>Chat Room</h2><p><b>{username}:</b> {message}</p><a href='/chat'>Go back</a>")

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
