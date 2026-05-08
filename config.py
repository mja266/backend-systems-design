import os
# Imports Python's os module so we can read environment variables


SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
# Reads SECRET_KEY from environment variables
# If not found, uses a default local-development value


TOKEN_EXPIRATION_HOURS = int(os.getenv("TOKEN_EXPIRATION_HOURS", 1))
# Reads token expiration length from environment variables
# Defaults to 1 hour if not provided


DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")
# Reads database file path from environment variables
# Defaults to local SQLite database.db