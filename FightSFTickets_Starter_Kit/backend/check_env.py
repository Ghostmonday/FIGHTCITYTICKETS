import os
from pathlib import Path
from dotenv import load_dotenv

# Try loading .env from current directory
env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)
    print("Loaded .env from: {env_file.absolute()}")
else:
    # Try parent directory
    env_file = Path('..') / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print("Loaded .env from: {env_file.absolute()}")
    else:
        print("No .env file found")

print("DEEPSEEK_API_KEY set: {'DEEPSEEK_API_KEY' in os.environ}")
if 'DEEPSEEK_API_KEY' in os.environ:
    key = os.environ['DEEPSEEK_API_KEY']
    print("Key length: {len(key)}")
    print("Key starts with: {key[:10]}...")

