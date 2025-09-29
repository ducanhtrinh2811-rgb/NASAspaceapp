import yaml
from dotenv import load_dotenv
import os

load_dotenv()

CONFIG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'config', 
        'config.yaml'
    )
)

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    raw_config = yaml.safe_load(f)

def replace_vars(obj):
    if isinstance(obj, dict):
        return {k: replace_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_vars(v) for v in obj]
    elif isinstance(obj, str):
        if obj.startswith('${') and obj.endswith('}'):
            var_name = obj[2:-1]
            var = os.getenv(var_name)
            if var:
                return var
        return obj
    else:
        return obj

config = replace_vars(raw_config)

WEAVIATE_CONFIG = config['weaviate']

INGESTION_CONFIG = config['ingestion']

HUGGING_FACE_MODEL_NAME = config['embedders']['hugging_face']['model_name']

POSTGRES_CONFIG = config['postgres']