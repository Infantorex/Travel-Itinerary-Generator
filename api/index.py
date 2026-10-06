import os
import sys

# Add project root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

class VercelPathMiddleware(object):
    """
    Middleware that ensures Vercel's serverless rewrite path (/api/index)
    is translated into the correct target route for Flask.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        matched_path = environ.get('HTTP_X_MATCHED_PATH') or environ.get('HTTP_X_VERCEL_MATCHED_PATH')
        
        if matched_path:
            environ['PATH_INFO'] = matched_path
        elif path_info.startswith('/api/index'):
            rest = path_info[len('/api/index'):]
            environ['PATH_INFO'] = rest if rest.startswith('/') else ('/' + rest if rest else '/')
        elif path_info in ['/api', '/api/']:
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

# Expose handler for Vercel
handler = app
