import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
from urllib.parse import parse_qs

UPLOAD_DIR = "uploads"

# Simulated user database
USER_CREDENTIALS = {
    'testuser': 'password123'
}

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

    def do_GET(self):
        """Handle GET requests for different endpoints."""
        if self.path == "/":
            # Main page with options
            self._render_page("Welcome to Python Web App", """
            <h2>Explore Our Features</h2>
            <ul>
                <li><a href='/login'>Login</a></li>
                <li><a href='/signup'>Sign Up</a></li>
                <li><a href='/upload'>Upload a Reel</a></li>
                <li><a href='/chat'>Join the Chat Room</a></li>
                <li><a href='/events'>View Upcoming Events</a></li>
            </ul>
            """)
        elif self.path == "/login":
            # Login page
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
            # Signup page
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

    def do_POST(self):
        """Handle POST requests for file uploads, chat messages, login, and signup."""
        if self.path == "/login":
            # Handle login POST request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data = parse_qs(post_data)

            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            # Validate the user credentials
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                self._render_page("Login Success", f"""
                <h2 class="success">Login Successful!</h2>
                <p>Welcome, {username}!</p>
                <a href="/">Go to Homepage</a>
                """)
            else:
                self._render_page("Login Failed", """
                <h2 class="error">Login Failed</h2>
                <p>Invalid username or password.</p>
                <a href="/login">Try again</a>
                """)

        elif self.path == "/signup":
            # Handle signup POST request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            post_data = parse_qs(post_data)

            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            # Check if username is already taken
            if username in USER_CREDENTIALS:
                self._render_page("Signup Failed", """
                <h2 class="error">Signup Failed</h2>
                <p>Username already exists. Please choose another.</p>
                <a href="/signup">Try again</a>
                """)
            else:
                # Add the new user to the simulated database
                USER_CREDENTIALS[username] = password
                self._render_page("Signup Success", f"""
                <h2 class="success">Signup Successful!</h2>
                <p>Welcome, {username}! You can now <a href="/login">log in</a>.</p>
                """)

        elif self.path == "/upload":
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

                    self._render_page("Upload Successful", f"""
                    <h2>Upload Successful!</h2>
                    <p>File saved as: {file_item.filename}</p>
                    <a href='/upload'>Upload another file</a>
                    """)
                else:
                    self._render_page("Upload Failed", "<h2>No file provided. Please try again.</h2><a href='/upload'>Try again</a>")

        elif self.path == "/chat":
            # Handle chat message
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            message = parse_qs(post_data).get('message', [''])[0]
            # Print message to console for now (can save to a file or database)
            print(f"New chat message: {message}")

            self._render_page("Chat Room", f"""
            <h2>Chat Room</h2>
            <form method="POST" action="/chat">
                <input type="text" name="message" placeholder="Your message" value="{message}"><br>
                <button type="submit">Send</button>
            </form>
            <div id="chat_logs">
                <h3>Chat History</h3>
                <ul>
                    <li><strong>You:</strong> {message}</li>
                    <li><strong>User1:</strong> Hello everyone!</li>
                    <li><strong>User2:</strong> Hi User1!</li>
                </ul>
            </div>
            """)

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    """Run the server."""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
