# 🐾 CãoLector - Clipboard & Ticket Tracker

![CãoLector Logo](Logo_HD.png)

O **CãoLector** é um utilitário de produtividade desenvolvido em Python (com interface moderna via `customtkinter`) para otimizar a captura, rastreamento e registro rápido de tickets, protocolos e anotações. Ele elimina o atrito de alternar janelas e usar o bloco de notas durante a operação.

## 🚀 Como Funciona
Como analista, em vez de perder tempo copiando e colando informações manualmente:
1. Simplesmente selecione o texto desejado em qualquer lugar do seu computador (Browser, Email, PDF, Slack).
2. Pressione a tecla de atalho **F9**.
3. O texto será copiado e salvo automaticamente na lista do aplicativo, junto com a Data e Hora exata!

## ✨ Funcionalidades
- **Atalho Global:** Funciona de forma invisível em qualquer tela usando a tecla `F9`.
- **Modo Segundo Plano (System Tray):** Ao fechar a janela no "X", o app não encerra. Ele fica minimizado na bandeja do relógio do Windows, sem poluir sua barra de tarefas, continuando a escutar o atalho.
- **Auto-Save e Segurança:** O aplicativo salva seu progresso automaticamente em segundo plano. Se o PC desligar ou o app for fechado, você não perde seus tickets do dia!
- **Organização Ágil:** Arraste e solte (Drag & Drop) os itens na lista para reordenar sua prioridade. Exclua itens em lote através das caixas de seleção.
- **Exportação Flexível:** No final do dia, escolha onde quer salvar e exporte sua lista para **.TXT** (Texto Simples) ou **.CSV** (Excel).

---

## 🎁 Para Usuários (Como usar sem programar)
Se você quer apenas usar o programa, não precisa entender de código ou instalar o Python!
1. Vá até a aba **Releases** aqui no lado direito do GitHub.
2. Baixe o arquivo `CaoLector.zip`.
3. Extraia o arquivo `.exe`, dê dois cliques e pronto! O ícone da patinha aparecerá perto do seu relógio.

---

## 🛠️ Para Desenvolvedores (Como rodar o código-fonte)

### Dependências
Para rodar a versão em código, você precisará do Python 3.12+ e das bibliotecas listadas no `requirements.txt`.
Instale-as com o comando:
```bash
pip install -r requirements.txt
