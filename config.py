import os
import sys
import json
from pathlib import Path

APP_NAME = "CaoLector"

def get_asset_path(filename: str) -> Path:
    """Garante que a imagem do ícone é encontrada mesmo dentro do .exe gerado."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / filename
    return Path(__file__).parent / filename

def get_user_data_path() -> Path:
    """Cria a pasta no %APPDATA% do Windows com permissão total de leitura/escrita."""
    base_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~")))
    app_dir = base_dir / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

# Definição dos caminhos absolutos
USER_DATA_DIR = get_user_data_path()
BACKUP_FILE = USER_DATA_DIR / "backup.json"
SETTINGS_FILE = USER_DATA_DIR / "settings.json"
LOG_FILE = USER_DATA_DIR / "caolector.log"

def load_settings() -> dict:
    """Carrega as configurações (como o atalho escolhido pelo usuário)."""
    default_settings = {"hotkey": "f9"}
    if not SETTINGS_FILE.exists():
        save_settings(default_settings)
        return default_settings
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_settings

def save_settings(settings: dict) -> None:
    """Salva o novo atalho escolhido no disco."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)