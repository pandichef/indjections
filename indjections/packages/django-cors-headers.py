settings = """
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE
CORS_ORIGIN_WHITELIST = ["http://localhost", "http://127.0.0.1"]  # e.g., React.js local development
"""
