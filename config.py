import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://nnlaqmqvivdvxqjwtryx.supabase.co')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ubGFxbXF2aXZkdnhxand0cnl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDc5OTAsImV4cCI6MjA2OTk4Mzk5MH0.H7beydA_NCrid9J70YS_qtjUV0hjch3vQSiekPVOCFM')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your_super_secret_key_change_this_in_production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:[YOUR-PASSWORD]@db.nnlaqmqvivdvxqjwtryx.supabase.co:5432/postgres')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 