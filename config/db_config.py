import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DBConfig:
    """
    Centralized database configuration settings.
    """

    # Database connection settings
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = int(os.getenv('DB_PORT', 3306))  # Default MySQL port
    USER = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DATABASE = os.getenv('DB_NAME', 'mainstreet_data_pipeline')

    # Connection pool settings (optional)
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))  # Number of connections in the pool
    POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 3600))  # Recycle connections after 1 hour

    @classmethod
    def get_config(cls):
        """
        Return the database configuration as a dictionary.
        """
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE,
            'pool_size': cls.POOL_SIZE,
            'pool_recycle': cls.POOL_RECYCLE
        }

    @classmethod
    def validate(cls):
        """
        Validate the database configuration.
        Raises a ValueError if any required setting is missing or invalid.
        """
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Missing required environment variable: {var}")

        if not isinstance(cls.PORT, int) or cls.PORT <= 0:
            raise ValueError("DB_PORT must be a positive integer.")

        if not isinstance(cls.POOL_SIZE, int) or cls.POOL_SIZE <= 0:
            raise ValueError("DB_POOL_SIZE must be a positive integer.")

        if not isinstance(cls.POOL_RECYCLE, int) or cls.POOL_RECYCLE <= 0:
            raise ValueError("DB_POOL_RECYCLE must be a positive integer.")


# Validate configuration on import
DBConfig.validate()

# Export the database configuration as a dictionary
DB_CONFIG = DBConfig.get_config()