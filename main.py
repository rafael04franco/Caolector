import os
import threading
import json
from tkinter import filedialog
from datetime import datetime

import customtkinter as ctk # type: ignore
import keyboard # type: ignore
import pandas as pd # type: ignore
import pyperclip # type: ignore
from plyer import notification # type: ignore
from typing import Any
import pystray # type: ignore
from PIL import Image, ImageDraw # type: ignore

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class TicketTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Estado para arrastar e soltar (drag and drop)
        self.drag_data: dict[str, Any] = {"y": 0, "item": None}

        self.title("CãoLector 🐾")
        
        # Configurar icone na janela e barra de tarefas
        if os.path.exists("icone.ico"):
            self.iconbitmap("icone.ico")
            
        self.geometry("500x600")
        # Define o tamanho mínimo da janela para evitar que encolha demais
        self.minsize(400, 400)
        
        # Configura o grid da janela principal para permitir redimensionamento
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Faz o quadro rolável (scrollable frame) expandir
        
        # Intercepta o fechamento da janela para minimizar para a bandeja (tray)
        self.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.tray_icon: Any = None
        
        self.tickets: list[dict[str, str]] = []

        # Título
        self.label_title = ctk.CTkLabel(self, text="CãoLector 🐾", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        
        # Subtítulo de instruções
        self.label_instructions = ctk.CTkLabel(self, text="Pressione F9 para copiar e salvar um texto.", font=ctk.CTkFont(size=12))
        self.label_instructions.grid(row=1, column=0, pady=(0, 10), sticky="ew")

        # Quadro Rolável Principal para exibir os tickets
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
        
        # Dicionário para armazenar referência aos quadros dos widgets
        self.ticket_widgets: dict[str, ctk.CTkFrame] = {}

        # Quadro dos Botões
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, pady=10, sticky="ew")
        # Centraliza os botões no seu quadro
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Botões de Exportação (Linha 0)
        self.btn_export_txt = ctk.CTkButton(self.button_frame, text="Salvar .TXT", command=self.export_txt, fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_export_txt.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_export_csv = ctk.CTkButton(self.button_frame, text="Salvar Excel (.CSV)", command=self.export_csv, fg_color="#3498db", hover_color="#2980b9")
        self.btn_export_csv.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Botões de Ação (Linha 1)
        self.btn_clear = ctk.CTkButton(self.button_frame, text="Limpar Lista", command=self.clear_tickets, fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_clear.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Botão Excluir Selecionados
        self.btn_delete_selected = ctk.CTkButton(self.button_frame, text="Excluir Selecionados", command=self.delete_selected_tickets, fg_color="#f39c12", hover_color="#d68910")
        self.btn_delete_selected.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Rótulo de Status
        self.label_status = ctk.CTkLabel(self, text="", text_color="green", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_status.grid(row=4, column=0, pady=(0, 10))

        # Carrega o estado automaticamente se houver backup
        self.load_state()

        # Inicia o ouvinte de atalho do teclado em uma thread separada para não bloquear a interface
        self.listener_thread = threading.Thread(target=self.start_keyboard_listener, daemon=True)
        self.listener_thread.start()
        
    def get_backup_path(self):
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        folder = os.path.join(appdata, 'CaoLector')
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, 'backup.json')

    def save_state(self):
        try:
            with open(self.get_backup_path(), 'w', encoding='utf-8') as f:
                json.dump(self.tickets, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Erro ao salvar backup:", e)

    def load_state(self):
        try:
            path = self.get_backup_path()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    saved_tickets = json.load(f)
                    for t in saved_tickets:
                        self.tickets.append(t)
                        self.render_ticket_row(t)
        except Exception as e:
            print("Erro ao carregar backup:", e)

    def start_keyboard_listener(self):
        # Escuta o 'F9' globalmente, suprimindo o comportamento padrão do sistema
        keyboard.add_hotkey('f9', self.on_hotkey_pressed, suppress=True)
        keyboard.wait()
        
    def on_hotkey_pressed(self):
        # Limpa a área de transferência para evitar copiar texto antigo se nada estiver selecionado
        pyperclip.copy('')
        
        # Quando F9 é pressionado, envia Ctrl+C para copiar
        keyboard.send('ctrl+c')
        
        # Dá um tempo ao Sistema Operacional para atualizar a área de transferência
        self.after(200, self.process_clipboard)

    def process_clipboard(self):
        try:
            copied_text = pyperclip.paste().strip()
            if copied_text:
                self.add_ticket(copied_text)
                self.show_status("Copiado com sucesso!")
                # Send system notification
                notification.notify(
                    title="Novo Texto Salvo 🐾",
                    message="O texto selecionado foi adicionado à lista.",
                    app_name="CãoLector",
                    timeout=3
                )
            else:
                self.show_status("Nada copiado.", error=True)
        except Exception as e:
            print("Erro ao processar área de transferência:", e)
            
    def add_ticket(self, text):
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Gera um ID único para o ticket baseado na data/hora e no tamanho atual da lista
        ticket_id = f"{timestamp}_{len(self.tickets)}"
        
        ticket_data = {"id": ticket_id, "Data/Hora": timestamp, "Conteúdo": text}
        self.tickets.append(ticket_data)
        
        # Salva o estado atualizado
        self.save_state()
        
        self.render_ticket_row(ticket_data)
        
        # Rola a tela para baixo automaticamente
        self.scrollable_frame._parent_canvas.yview_moveto(1.0)

    def render_ticket_row(self, ticket_data):
        ticket_id = ticket_data["id"]
        timestamp = ticket_data["Data/Hora"]
        text = ticket_data["Conteúdo"]

        # Cria um quadro para a fileira
        row_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=5)
        row_frame.pack(fill="x", pady=2, padx=2)
        
        # Dicionário para armazenar variáveis das caixas de seleção
        # Inicializa se não existir
        if not hasattr(self, 'ticket_checkboxes'):
            self.ticket_checkboxes: dict[str, ctk.BooleanVar] = {}
        
        # Cria uma variável para a caixa de seleção
        checkbox_var = ctk.BooleanVar(value=False)
        self.ticket_checkboxes[ticket_id] = checkbox_var
        
        # Salva a referência
        self.ticket_widgets[ticket_id] = row_frame
        
        # Puxador para arrastar (drag handle)
        drag_handle = ctk.CTkLabel(row_frame, text=" ↕ ", font=ctk.CTkFont(size=16, weight="bold"), cursor="hand2", text_color="gray")
        drag_handle.pack(side="left", padx=(5, 5))
        
        # Caixa de seleção para exclusão
        checkbox = ctk.CTkCheckBox(row_frame, text="", variable=checkbox_var, width=20)
        checkbox.pack(side="left", padx=(5, 5))
        
        # Rótulo do Conteúdo - Quebra o texto para não empurrar os elementos para fora
        content_label = ctk.CTkLabel(row_frame, text=f"[{timestamp}] - {text}", font=ctk.CTkFont(size=13), anchor="w", justify="left", wraplength=350)
        content_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Vincula eventos de arrastar e soltar (drag and drop) no puxador e no quadro
        drag_handle.bind("<ButtonPress-1>", lambda event, i=ticket_id: self.on_drag_start(event, i))
        drag_handle.bind("<B1-Motion>", self.on_drag_motion)
        drag_handle.bind("<ButtonRelease-1>", self.on_drag_release)

    def delete_selected_tickets(self):
        if not hasattr(self, 'ticket_checkboxes') or not self.ticket_checkboxes:
            self.show_status("Nenhum ticket disponível para exclusão.", error=True)
            return
            
        tickets_to_delete = [t_id for t_id, var in self.ticket_checkboxes.items() if var.get()]
        
        if not tickets_to_delete:
            self.show_status("Nenhum ticket selecionado.", error=True)
            return
            
        # Remove da lista principal de tickets
        self.tickets = [t for t in self.tickets if t["id"] not in tickets_to_delete]
        
        # Destrói os widgets e limpa as variáveis
        for t_id in tickets_to_delete:
            ticket_id = str(t_id)
            if ticket_id in self.ticket_widgets:
                self.ticket_widgets[ticket_id].destroy()
                self.ticket_widgets.pop(ticket_id)
            if ticket_id in self.ticket_checkboxes:
                self.ticket_checkboxes.pop(ticket_id)
                
        # Salva as mudanças
        self.save_state()
                
        self.show_status(f"{len(tickets_to_delete)} ticket(s) removido(s).")

    # --- LÓGICA DE ARRASTAR E SOLTAR (DRAG AND DROP) ---
    def on_drag_start(self, event, ticket_id):
        widget = self.ticket_widgets[ticket_id]
        self.drag_data["item"] = ticket_id
        self.drag_data["y"] = event.y_root
        # Destaca o quadro que está sendo arrastado
        widget.configure(border_width=2, border_color="#3498db")

    def on_drag_motion(self, event):
        # Não movemos fisicamente aqui porque o empacotador do Tkinter (pack) gerencia o layout,
        # mas poderíamos fornecer feedback visual. 
        pass

    def on_drag_release(self, event):
        ticket_id = self.drag_data["item"]
        if not ticket_id: return
        
        widget = self.ticket_widgets[ticket_id]
        widget.configure(border_width=0)
        
        # Descobre onde o usuário soltou o item
        y_release = event.y_root
        delta_y = y_release - self.drag_data["y"]
        
        # Determina o limite de movimento baseado aproximadamente na altura do widget (ex: 40 pixels por linha)
        rows_moved = int(round(delta_y / 40.0))
        
        if rows_moved != 0:
            # Encontra o índice atual
            current_idx = next(i for i, t in enumerate(self.tickets) if t["id"] == ticket_id)
            new_idx = max(0, min(len(self.tickets) - 1, current_idx + rows_moved))
            
            if current_idx != new_idx:
                # Reordena na lista interna (backend)
                item = self.tickets.pop(current_idx)
                self.tickets.insert(new_idx, item)
                
                # Re-renderiza os widgets visualmente
                for w in self.ticket_widgets.values():
                    w.pack_forget()
                    
                for t in self.tickets:
                    self.ticket_widgets[t["id"]].pack(fill="x", pady=2, padx=2)
                    
                # Salva o novo estado da ordem
                self.save_state()

        self.drag_data["item"] = None
        self.drag_data["y"] = 0
    # ---------------------------

    def show_status(self, message, error=False):
        color = "#e74c3c" if error else "#2ecc71"
        self.label_status.configure(text=message, text_color=color)
        # Limpa o status após 3 segundos
        self.after(3000, lambda: self.label_status.configure(text=""))
        
    def clear_tickets(self):
        self.tickets = []
        for w in self.ticket_widgets.values():
            w.destroy()
        self.ticket_widgets = {}
        if hasattr(self, 'ticket_checkboxes'):
            self.ticket_checkboxes = {}
            
        self.save_state()
        self.show_status("Lista apagada.")
        
    def export_txt(self):
        if not self.tickets:
            self.show_status("Lista vazia! Nada para salvar.", error=True)
            return

        date_str = datetime.now().strftime("%d_%m_%Y")
        initial_filename = f"caoloctor_tickets_{date_str}.txt"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=initial_filename,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Salvar como TXT"
        )
        
        if not filename: # Usuário cancelou
            return
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=== CÃOLECTOR ===\n")
                f.write(f"Data de Exportação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                for t in self.tickets:
                    f.write(f"[{t['Data/Hora']}] - {t['Conteúdo']}\n")
            self.show_status(f"Salvo com sucesso!")
            notification.notify(title="Lista Exportada!", message=f"Arquivo TXT salvo.", app_name="CãoLector", timeout=3)
            os.startfile(os.path.dirname(filename)) # type: ignore
        except Exception as e:
            self.show_status(f"Erro ao salvar: {e}", error=True)
            
    def export_csv(self):
        if not self.tickets:
            self.show_status("Lista vazia! Nada para salvar.", error=True)
            return

        date_str = datetime.now().strftime("%d_%m_%Y")
        initial_filename = f"caoloctor_tickets_{date_str}.csv"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=initial_filename,
            filetypes=[("CSV (Excel)", "*.csv"), ("All Files", "*.*")],
            title="Salvar como CSV"
        )
        
        if not filename: # Usuário cancelou
            return
        
        try:
            df = pd.DataFrame(self.tickets)
            df.to_csv(filename, index=False, sep=";", encoding="utf-8-sig")
            self.show_status(f"Salvo com sucesso!")
            notification.notify(title="Lista Exportada!", message=f"Arquivo Excel salvo.", app_name="CãoLector", timeout=3)
            os.startfile(os.path.dirname(filename)) # type: ignore
        except Exception as e:
            self.show_status(f"Erro ao salvar: {e}", error=True)

    # --- LÓGICA DO ÍCONE NA BANDEJA E SEGUNDO PLANO ---
    def create_image(self):
        # Utiliza o icone.ico se existir, senao usa placeholder
        if os.path.exists("icone.ico"):
            try:
                image = Image.open("icone.ico")
                return image
            except Exception:
                pass
                
        # Fallback para placeholder
        image = Image.new('RGB', (64, 64), color=(41, 128, 185))
        d = ImageDraw.Draw(image)
        d.rectangle([16, 16, 48, 48], outline=(255, 255, 255), width=4)
        return image

    def hide_window(self):
        # Oculta a janela
        self.withdraw()
        if not self.tray_icon:
            image = self.create_image()
            menu = pystray.Menu(
                pystray.MenuItem('Restaurar Janela', self.show_window, default=True),
                pystray.MenuItem('Sair', self.quit_window)
            )
            self.tray_icon = pystray.Icon("CaoLector", image, "CãoLector 🐾", menu)
            # Roda o laço (loop) do ícone na bandeja numa thread em segundo plano
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
            # Envia notificação para o usuário saber que o app foi para a bandeja
            notification.notify(
                title="Em Segundo Plano",
                message="O aplicativo continuará rodando na bandeja do sistema. Pressione F9 para salvar.",
                app_name="CãoLector",
                timeout=4
            )

    def show_window(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        # Precisa restaurar a janela pela thread principal
        self.after(0, self.deiconify)

    def quit_window(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
        # Destrói a janela Tkinter para fechar o aplicativo completamente
        self.after(0, self.destroy)

if __name__ == "__main__":
    app = TicketTracker()
    app.mainloop()
