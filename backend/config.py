from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("NANO_DB", str(ROOT / "runtime/nanoforensics.db")))
RUN_TIMEOUT = float(os.getenv("NANO_RUN_TIMEOUT", "30"))
JOB_TIMEOUT = float(os.getenv("NANO_JOB_TIMEOUT", "120"))
BUDGET = float(os.getenv("NANO_BUDGET", "1800"))
SEEDS = [42, 137, 271]
PUBLIC_RATE = 0.05
PUBLIC_TEMPERATURE = 0.05
