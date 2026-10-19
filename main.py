import os
import threading
from tkinter import filedialog
from datetime import datetime

import customtkinter as ctk
from plyer import notification
import pystray
from PIL import Image, ImageDraw

import config
from backend import TicketManager, ClipboardMonitor

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    """Interface gráfica do CãoLector."""
    
    def __init__(self):
        super().__init__()
        
        self.drag_data = {"y": 0, "item": None}
        self.title("CãoLector 🐾")
        
        icon_path = config.get_asset_path("icone.ico")
        if icon_path.exists():
            self.iconbitmap(icon_path)
            
        self.geometry("550x650")
        self.minsize(450, 450)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) 
        
        self.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.tray_icon = None
        
        self.manager = TicketManager()
        self.ticket_widgets = {}
        self.ticket_checkboxes = {}

        # ---------------- UI LAYOUT ----------------
        self.label_title = ctk.CTkLabel(self, text="CãoLector 🐾", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, pady=(20, 5), sticky="ew")

        # Painel de Configuração do Atalho
        self.hotkey_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.hotkey_frame.grid(row=1, column=0, pady=(0, 10))
        
        settings = config.load_settings()
        self.current_hotkey_str = ctk.StringVar(value=settings.get("hotkey", "f9").upper())
        
        self.lbl_hotkey = ctk.CTkLabel(self.hotkey_frame, text="Atalho de Captura:", font=ctk.CTkFont(size=13))
        self.lbl_hotkey.pack(side="left", padx=5)
        
        self.btn_hotkey = ctk.CTkButton(self.hotkey_frame, textvariable=self.current_hotkey_str, width=80, 
                                        command=self.ask_new_hotkey, fg_color="#34495e", hover_color="#2c3e50")
        self.btn_hotkey.pack(side="left", padx=5)

        self.label_instructions = ctk.CTkLabel(self, text="Selecione um texto em qualquer app e pressione o atalho para salvar.", font=ctk.CTkFont(size=12))
        self.label_instructions.grid(row=2, column=0, pady=(0, 10), sticky="ew")

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_export_txt = ctk.CTkButton(self.button_frame, text="Salvar .TXT", command=self.export_txt, fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_export_txt.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_export_csv = ctk.CTkButton(self.button_frame, text="Salvar Excel", command=self.export_csv, fg_color="#3498db", hover_color="#2980b9")
        self.btn_export_csv.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.btn_clear = ctk.CTkButton(self.button_frame, text="Limpar Lista", command=self.clear_tickets, fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_clear.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_delete_selected = ctk.CTkButton(self.button_frame, text="Excluir Selecionados", command=self.delete_selected, fg_color="#f39c12", hover_color="#d68910")
        self.btn_delete_selected.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.label_status = ctk.CTkLabel(self, text="", text_color="green", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_status.grid(row=5, column=0, pady=(0, 10))

        # Renderiza os tickets salvos anteriormente
        for t in self.manager.tickets:
            self.render_ticket_row(t)

        # Inicia o Monitoramento em Background
        self.monitor = ClipboardMonitor(self.on_clipboard_captured)

    # ---------------- LÓGICA DE AÇÕES ----------------
    def ask_new_hotkey(self):
        """Abre uma janela profissional para capturar a tecla fisicamente."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Configurar Atalho")
        dialog.geometry("350x180")
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.grab_set()
        
        lbl = ctk.CTkLabel(dialog, text="Pressione a tecla ou combinação desejada\n(Ex: F10, Ctrl+Q, Alt+S)", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(expand=True, pady=(20, 10))
        
        btn_cancel = ctk.CTkButton(dialog, text="Cancelar", command=dialog.destroy, fg_color="#e74c3c", hover_color="#c0392b")
        btn_cancel.pack(pady=(0, 20))
        
        def listen_key():
            import keyboard
            import time
            time.sleep(0.3)
            
            try:
                new_key = keyboard.read_hotkey(suppress=False)
                self.after(0, process_key, new_key, dialog)
            except Exception:
                pass
                
        def process_key(new_key, window):
            if window.winfo_exists():
                window.destroy()
                
            if new_key and new_key != "esc":
                if self.monitor.change_hotkey(new_key):
                    self.current_hotkey_str.set(new_key.upper())
                    self.show_status(f"Atalho alterado para [ {new_key.upper()} ]")
                else:
                    self.show_status("Tecla inválida ou do sistema!", error=True)

        threading.Thread(target=listen_key, daemon=True).start()

    def on_clipboard_captured(self, text):
        self.after(0, self._handle_capture, text)
        
    def _handle_capture(self, text):
        if text:
            ticket_data = self.manager.add_ticket(text)
            self.render_ticket_row(ticket_data)
            self.scrollable_frame._parent_canvas.yview_moveto(1.0)
            self.show_status("Copiado com sucesso!")
            notification.notify(title="Novo Texto Salvo 🐾", message="Adicionado à lista.", app_name="CãoLector", timeout=3)
        else:
            self.show_status("Nada copiado.", error=True)

    def render_ticket_row(self, ticket_data):
        ticket_id = ticket_data["id"]
        timestamp = ticket_data["Data/Hora"]
        text = ticket_data["Conteúdo"]

        row_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=5)
        row_frame.pack(fill="x", pady=2, padx=2)
        
        checkbox_var = ctk.BooleanVar(value=False)
        self.ticket_checkboxes[ticket_id] = checkbox_var
        self.ticket_widgets[ticket_id] = row_frame
        
        drag_handle = ctk.CTkLabel(row_frame, text=" ↕ ", font=ctk.CTkFont(size=16, weight="bold"), cursor="hand2", text_color="gray")
        drag_handle.pack(side="left", padx=(5, 5))
        
        checkbox = ctk.CTkCheckBox(row_frame, text="", variable=checkbox_var, width=20)
        checkbox.pack(side="left", padx=(5, 5))
        
        content_label = ctk.CTkLabel(row_frame, text=f"[{timestamp}] - {text}", font=ctk.CTkFont(size=13), anchor="w", justify="left", wraplength=350)
        content_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        drag_handle.bind("<ButtonPress-1>", lambda event, i=ticket_id: self.on_drag_start(event, i))
        drag_handle.bind("<ButtonRelease-1>", self.on_drag_release)

    def delete_selected(self):
        to_delete = [t_id for t_id, var in self.ticket_checkboxes.items() if var.get()]
        if not to_delete:
            self.show_status("Nenhum ticket selecionado.", error=True)
            return
        
        self.manager.remove_tickets(to_delete)
        for t_id in to_delete:
            self.ticket_widgets[t_id].destroy()
            self.ticket_widgets.pop(t_id)
            self.ticket_checkboxes.pop(t_id)
                
        self.show_status(f"{len(to_delete)} ticket(s) removido(s).")

    def clear_tickets(self):
        self.manager.clear_all()
        for w in self.ticket_widgets.values():
            w.destroy()
        self.ticket_widgets.clear()
        self.ticket_checkboxes.clear()
        self.show_status("Lista apagada.")

    # ---------------- ARRASTAR E SOLTAR ----------------
    def on_drag_start(self, event, ticket_id):
        self.drag_data["item"] = ticket_id
        self.drag_data["y"] = event.y_root
        self.ticket_widgets[ticket_id].configure(border_width=2, border_color="#3498db")

    def on_drag_release(self, event):
        ticket_id = self.drag_data["item"]
        if not ticket_id: return
        
        widget = self.ticket_widgets[ticket_id]
        widget.configure(border_width=0)
        
        delta_y = event.y_root - self.drag_data["y"]
        rows_moved = int(round(delta_y / 40.0))
        
        if rows_moved != 0:
            current_idx = next(i for i, t in enumerate(self.manager.tickets) if t["id"] == ticket_id)
            new_idx = max(0, min(len(self.manager.tickets) - 1, current_idx + rows_moved))
            
            if current_idx != new_idx:
                item = self.manager.tickets.pop(current_idx)
                self.manager.tickets.insert(new_idx, item)
                self.manager.save_backup()
                
                for w in self.ticket_widgets.values():
                    w.pack_forget()
                for t in self.manager.tickets:
                    self.ticket_widgets[t["id"]].pack(fill="x", pady=2, padx=2)

        self.drag_data["item"] = None

    # ---------------- EXPORTAÇÕES ----------------
    def export_txt(self):
        if not self.manager.tickets:
            self.show_status("Lista vazia!", error=True)
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"caolector_{datetime.now().strftime('%d_%m_%Y')}.txt")
        if filename:
            self.manager.export_txt(filename)
            self.show_status("TXT Salvo!")
            os.startfile(os.path.dirname(filename))

    def export_csv(self):
        if not self.manager.tickets:
            self.show_status("Lista vazia!", error=True)
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"caolector_{datetime.now().strftime('%d_%m_%Y')}.csv")
        if filename:
            self.manager.export_csv(filename)
            self.show_status("Excel Salvo!")
            os.startfile(os.path.dirname(filename))

    def show_status(self, message, error=False):
        color = "#e74c3c" if error else "#2ecc71"
        self.label_status.configure(text=message, text_color=color)
        self.after(3000, lambda: self.label_status.configure(text=""))

    # ---------------- TRAY (SEGUNDO PLANO) ----------------
    def create_image(self):
        icon_path = config.get_asset_path("icone.ico")
        if icon_path.exists():
            try: return Image.open(icon_path)
            except Exception: pass
        img = Image.new('RGB', (64, 64), color=(41, 128, 185))
        ImageDraw.Draw(img).rectangle([16, 16, 48, 48], outline=(255, 255, 255), width=4)
        return img

    def hide_window(self):
        self.withdraw()
        if not self.tray_icon:
            menu = pystray.Menu(pystray.MenuItem('Restaurar Janela', self.show_window, default=True), pystray.MenuItem('Sair', self.quit_window))
            self.tray_icon = pystray.Icon("CaoLector", self.create_image(), "CãoLector 🐾", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
            current_hotkey = self.current_hotkey_str.get()
            notification.notify(title="Em Segundo Plano", message=f"Rodando na bandeja. Pressione {current_hotkey} para salvar.", app_name="CãoLector", timeout=4)

    def show_window(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.after(0, self.deiconify)

    def quit_window(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
        self.after(0, self.destroy)

if __name__ == "__main__":
    app = App()
    app.mainloop()