import sys
from pathlib import Path

_RWV_DIR = Path(__file__).parent
if str(_RWV_DIR) not in sys.path:
    sys.path.insert(0, str(_RWV_DIR))