"""إدارة الإعدادات باستخدام YAML و متغيرات البيئة."""
from pathlib import Path
from typing import Any, Dict
import os

import yaml
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"


def load_config(config_name: str) -> Dict[str, Any]:
    """تحميل ملف إعدادات YAML."""
    config_path = CONFIG_DIR / config_name
    if not config_path.exists():
        raise FileNotFoundError(f"ملف الإعدادات غير موجود: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_env(key: str, default: str = "") -> str:
    """قراءة متغير بيئة مع قيمة افتراضية."""
    return os.getenv(key, default)