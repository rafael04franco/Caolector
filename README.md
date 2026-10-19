# 🐾 CãoLector - Clipboard & Ticket Tracker

![CãoLector Logo](Logo_HD.png)

O **CãoLector** é um utilitário de produtividade desenvolvido em Python (com arquitetura modular MVC e interface moderna via `customtkinter`) para otimizar a captura, rastreamento e registro rápido de tickets, protocolos e anotações. Ele elimina o atrito de alternar janelas e usar o bloco de notas durante a operação.

## 🚀 Como Funciona
Como analista, em vez de perder tempo copiando e colando informações manualmente:
1. Simplesmente selecione o texto desejado em qualquer lugar do seu computador (Browser, Email, PDF, Slack).
2. Pressione a tecla de atalho configurada (por padrão: **F9**).
3. O texto será copiado e salvo automaticamente na lista do aplicativo, junto com a Data e Hora exata!

## ✨ Funcionalidades
- **Atalho Customizável:** Atalho global inteligente. Podes definir e alterar a tecla de captura facilmente através da interface gráfica usando um capturador físico de teclas.
- **Modo Segundo Plano (System Tray):** Ao fechar a janela no "X", o app não encerra. Ele fica minimizado na bandeja do relógio do Windows, sem poluir a tua barra de tarefas, continuando a escutar o atalho.
- **Auto-Save e Segurança:** O aplicativo salva o teu progresso automaticamente em segundo plano (`%APPDATA%`). Se o PC desligar, não perdes os teus tickets do dia!
- **Organização Ágil:** Arraste e solte (Drag & Drop) os itens na lista para reordenar a prioridade. Exclua itens em lote através das caixas de seleção.
- **Exportação Flexível:** No final do dia, escolhe onde queres salvar e exporta a lista para **.TXT** (Texto Simples) ou **.CSV** (Excel).

---

## 🎁 Para Usuários (Como usar sem programar)
Se queres apenas usar o programa, não precisas de entender de código ou instalar o Python!
1. Vá até a aba **Releases** aqui no lado direito do GitHub.
2. Baixe o arquivo executável portátil (`CaoLector.exe`).
3. Dê dois cliques e pronto! O ícone da patinha aparecerá perto do teu relógio.

---

## 🛠️ Para Desenvolvedores (Como rodar o código-fonte)

### Arquitetura
O projeto segue o padrão **MVC (Model-View-Controller)** estruturado em módulos limpos:
- `config.py`: Gestão de caminhos e definições do sistema.
- `backend.py`: Lógica de dados, exportação e escuta de eventos em background (multithreading).
- `main.py`: Interface gráfica (UI) baseada em CustomTkinter.

### Dependências e Execução
Para rodar a versão em código, precisas do Python e das bibliotecas listadas no `requirements.txt`.
Instale-as com o comando:
```bash
pip install -r requirements.txt