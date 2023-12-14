import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEST_DATA = os.path.join(BASE_DIR, 'tests', 'data')
