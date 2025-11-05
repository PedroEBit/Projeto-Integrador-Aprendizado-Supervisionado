"""
Configurações do projeto
"""
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
CONFIG_DIR = BASE_DIR / 'config'

# Diretórios de dados
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
ENCRYPTED_DATA_DIR = DATA_DIR / 'encrypted'
MODEL_DIR = DATA_DIR / 'models'

# Configurações de upload
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {'csv'}

# Configurações de modelo
DEFAULT_MODEL_TYPE = 'classification'
DEFAULT_ALGORITHM = 'random_forest'
DEFAULT_TEST_SIZE = 0.2
DEFAULT_RANDOM_STATE = 42

# Configurações de API
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

# Chave de criptografia
ENCRYPTION_KEY_PATH = CONFIG_DIR / 'encryption.key'
