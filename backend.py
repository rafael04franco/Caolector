import logging
import json
import pandas as pd
import pyperclip
import keyboard
import threading
from datetime import datetime

import config

# Sistema profissional de Logs (Registo de Erros invisíveis)
logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("caolector_backend")

class TicketManager:
    """Gere a lógica de guardar, carregar e exportar os tickets (JSON, TXT, CSV)."""
    
    def __init__(self):
        self.tickets = []
        self.load_backup()

    def load_backup(self):
        try:
            if config.BACKUP_FILE.exists():
                with open(config.BACKUP_FILE, 'r', encoding='utf-8') as f:
                    self.tickets = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar backup: {e}")

    def save_backup(self):
        try:
            with open(config.BACKUP_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tickets, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar backup: {e}")

    def add_ticket(self, text: str) -> dict:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ticket_id = f"{timestamp}_{len(self.tickets)}"
        ticket_data = {"id": ticket_id, "Data/Hora": timestamp, "Conteúdo": text}
        self.tickets.append(ticket_data)
        self.save_backup()
        return ticket_data

    def remove_tickets(self, ids_to_remove: list):
        self.tickets = [t for t in self.tickets if t["id"] not in ids_to_remove]
        self.save_backup()

    def clear_all(self):
        self.tickets.clear()
        self.save_backup()

    def export_txt(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== CÃOLECTOR ===\n")
            f.write(f"Data de Exportação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            for t in self.tickets:
                f.write(f"[{t['Data/Hora']}] - {t['Conteúdo']}\n")

    def export_csv(self, filename: str):
        df = pd.DataFrame(self.tickets)
        df.to_csv(filename, index=False, sep=";", encoding="utf-8-sig")

class ClipboardMonitor:
    """Escuta o teclado em background e altera o atalho dinamicamente."""
    
    def __init__(self, callback):
        self.callback = callback
        self.current_hotkey = config.load_settings().get("hotkey", "f9")
        self.listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        self.listener_thread.start()

    def _start_listener(self):
        self._bind_hotkey()
        keyboard.wait()

    def _bind_hotkey(self):
        keyboard.unhook_all_hotkeys()
        try:
            keyboard.add_hotkey(self.current_hotkey, self.on_hotkey_pressed, suppress=True)
            logger.info(f"Atalho configurado com sucesso: {self.current_hotkey}")
        except Exception as e:
            logger.error(f"Erro ao configurar atalho {self.current_hotkey}: {e}")
            keyboard.add_hotkey("f9", self.on_hotkey_pressed, suppress=True) # Fallback seguro

    def change_hotkey(self, new_hotkey: str) -> bool:
        try:
            # Valida se o atalho digitado existe no Windows
            keyboard.parse_hotkey(new_hotkey)
            self.current_hotkey = new_hotkey.lower()
            self._bind_hotkey()
            
            settings = config.load_settings()
            settings["hotkey"] = self.current_hotkey
            config.save_settings(settings)
            return True
        except Exception as e:
            logger.error(f"Atalho inválido digitado pelo usuário: {new_hotkey} - {e}")
            return False

    def on_hotkey_pressed(self):
        pyperclip.copy('')
        keyboard.send('ctrl+c')
        # Usa um timer mínimo para não congelar o listener e dar tempo ao SO
        threading.Timer(0.2, self.process_clipboard).start()

    def process_clipboard(self):
        try:
            copied_text = pyperclip.paste().strip()
            self.callback(copied_text)
        except Exception as e:
            logger.error(f"Erro ao processar clipboard: {e}")