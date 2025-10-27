import customtkinter as ctk
from PIL import Image
import os
from tkinter import messagebox

# --- Configurações Iniciais ---
LOGO_FILENAME = "newgraphos.jpg"
SPLASH_DURATION_MS = 1500

# --- Cores Customizadas ---
COLOR_HEADER_BG = "#008080"  # Teal/Ciano Moderno
COLOR_HEADER_TEXT = "white"
COLOR_MENU_BG = "black"
COLOR_MENU_BUTTON = "#FFD700"  # Dourado/Amarelo Forte
COLOR_MENU_TEXT = "black"
COLOR_SUBMENU_BG = "gray20"
COLOR_STATUS_BG = "#008000"  # Verde Moderno
COLOR_STATUS_TEXT = "white"
# --- NOVAS CORES NÍVEL 3 ---
COLOR_ACTION_BG = "gray80"  # Fundo Cinza Claro
COLOR_ACTION_BUTTON_FG = "black"  # Botão Preto
COLOR_ACTION_BUTTON_TEXT = "white"  # Texto Branco

# --- Estrutura do Menu (Adicionado o Nível 3) ---
MENU_OPTIONS = {
    "Tela": {
        "Display": {
            "Rotina A": {}, "Rotina B": {}, "Rotina C": {}, "Rotina D": {}  # NOVO NÍVEL
        },
        "Edita": {}, "Arquiva": {}, "Recupera": {}
    },
    "Alfabeto": {
        "Edita": {}, "Arquiva": {}, "Recupera": {}
    },
    "Shapes": {
        "Cria": {}, "Arquiva": {}, "Recupera": {}
    },
    "Arquivos": {
        "Diretorio": {}, "Abrir": {}, "Gravar": {}, "Exportar": {}, "Importar": {}
    },
    "Versao do Sistema": {},
    "Encerrar": {}
}


class App(ctk.CTk):
    """
    Classe principal da aplicação (O Editor Gráfico GraphosPy).
    Contém a área de trabalho e o sistema de menus laterais.
    """

    def __init__(self):
        super().__init__()

        self.title("Graphos IV - Editor Gráfico MSX SCREEN 2")
        self.geometry("1000x700")

        self.withdraw()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 1. Header (Topo) ---
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_HEADER_BG, height=40, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.header_frame, text="GRAPHOS IV",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=COLOR_HEADER_TEXT).grid(row=0, column=0, padx=20, pady=5, sticky="w")

        # --- 2. Container Principal (Menu + Conteúdo) ---
        self.content_container = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.content_container.grid(row=1, column=0, columnspan=4, sticky="nswe")

        self.content_container.grid_columnconfigure(3, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        self.current_menu = None
        self.current_submenu = None  # Adicionado para rastrear o submenu ativo

        # --- Frames do Menu (Dentro do Content Container) ---
        self.menu_frame = ctk.CTkFrame(self.content_container, width=150, corner_radius=0, fg_color=COLOR_MENU_BG)
        self.menu_frame.grid(row=0, column=0, sticky="nswe")
        self.menu_frame.grid_rowconfigure(len(MENU_OPTIONS) + 1, weight=1)

        self.submenu_frame = ctk.CTkFrame(self.content_container, width=150, corner_radius=0, fg_color=COLOR_SUBMENU_BG)

        # O action_frame (Col. 2) será o frame de Nível 3 (Rotinas A, B, C, D)
        self.action_frame = ctk.CTkFrame(self.content_container, width=150, corner_radius=0, fg_color=COLOR_ACTION_BG)

        # --- Área de Edição (Canvas) ---
        self.main_content_frame = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="white")
        self.main_content_frame.grid(row=0, column=3, sticky="nswe", padx=10, pady=10)
        ctk.CTkLabel(self.main_content_frame, text="ÁREA DE EDIÇÃO (256x192 MSX SCREEN 2)",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(padx=20, pady=200)

        # --- 3. Status Bar/Command Line (Rodapé) ---
        self.status_frame = ctk.CTkFrame(self, fg_color=COLOR_STATUS_BG, height=30, corner_radius=0)
        self.status_frame.grid(row=2, column=0, columnspan=4, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: Aguardando comando...",
                                         text_color=COLOR_STATUS_TEXT)
        self.status_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")

        self.command_entry = ctk.CTkEntry(self.status_frame, placeholder_text="Linha de Comando >", width=250,
                                          fg_color="#006400", border_color="#006400", text_color=COLOR_STATUS_TEXT)
        self.command_entry.grid(row=0, column=1, padx=10, pady=2, sticky="e")
        self.command_entry.bind("<Return>", self.handle_command_input)

        self.create_main_menu_buttons()

    def create_main_menu_buttons(self):
        """Cria os botões do menu principal (Fundo Preto, Botões Amarelos)."""
        row_count = 0
        for name in MENU_OPTIONS.keys():
            button = ctk.CTkButton(self.menu_frame, text=name,
                                   command=lambda n=name: self.handle_menu_click(n),
                                   fg_color=COLOR_MENU_BUTTON,
                                   hover_color="#FFB300",
                                   text_color=COLOR_MENU_TEXT)
            button.grid(row=row_count, column=0, padx=10, pady=(10, 5), sticky="ew")
            row_count += 1

        ctk.CTkLabel(self.menu_frame, text="", fg_color="transparent").grid(row=row_count, column=0, sticky="nswe")

    def create_submenu_buttons(self, sub_options):
        """Cria os botões do submenu (Fundo Cinza Escuro, Botões Amarelos)."""
        row_count = 0

        back_button = ctk.CTkButton(self.submenu_frame, text="< Voltar",
                                    fg_color="red", hover_color="#8B0000",
                                    command=self.clear_submenus)
        back_button.grid(row=row_count, column=0, padx=10, pady=(10, 5), sticky="ew")
        row_count += 1

        for name in sub_options.keys():
            button = ctk.CTkButton(self.submenu_frame, text=name,
                                   command=lambda n=name: self.handle_submenu_click(n),
                                   fg_color=COLOR_MENU_BUTTON,
                                   hover_color="#FFB300",
                                   text_color=COLOR_MENU_TEXT)
            button.grid(row=row_count, column=0, padx=10, pady=5, sticky="ew")
            row_count += 1

        self.submenu_frame.grid_rowconfigure(row_count, weight=1)
        ctk.CTkLabel(self.submenu_frame, text="", fg_color="transparent").grid(row=row_count, column=0, sticky="nswe")

    def handle_menu_click(self, menu_name):
        """Manipula o clique no Nível 1."""
        self.clear_submenus()

        if menu_name in ["Encerrar", "Versao do Sistema"]:
            # Ações diretas de Nível 1
            if menu_name == "Encerrar": self.quit_app()
            if menu_name == "Versao do Sistema": self.show_version_info()
            return

        sub_options = MENU_OPTIONS.get(menu_name, {})
        if sub_options:
            self.submenu_frame.grid(row=0, column=1, sticky="nswe")
            self.current_menu = menu_name
            self.create_submenu_buttons(sub_options)

    def handle_submenu_click(self, submenu_name):
        """Manipula o clique no Nível 2."""

        # Limpa Coluna 3 antes de qualquer coisa
        self.clear_frame(self.action_frame)
        self.action_frame.grid_forget()
        self.current_submenu = submenu_name

        # Lógica para Menus de Nível 3 (Rotinas de Display)
        if self.current_menu == "Tela" and submenu_name == "Display":
            self.action_frame.grid(row=0, column=2, sticky="nswe")
            self.show_display_options()
            return

        # Lógica para Menus de Nível 3 (Arquivos, etc.)
        if self.current_menu == "Arquivos" and submenu_name in ["Diretorio", "Abrir", "Gravar", "Exportar", "Importar"]:
            self.action_frame.grid(row=0, column=2, sticky="nswe")
            self.show_file_action_options(submenu_name)
            return

        # Ação simples de Nível 2
        self.display_message(f"Ação: {self.current_menu} -> {submenu_name} (Implementar!)")
        self.status_label.configure(text=f"Ação executada: {submenu_name}")

    def show_display_options(self):
        """Mostra opções detalhadas do Display (Rotinas A, B, C, D) - Nível 3."""
        self.clear_frame(self.action_frame)

        # Título
        ctk.CTkLabel(self.action_frame,
                     text=f"ROTINAS DE DISPLAY",
                     font=ctk.CTkFont(weight="bold"),
                     text_color="black",  # Texto preto para fundo claro
                     fg_color=COLOR_ACTION_BG).pack(padx=10, pady=10)

        # Opções de Rotina
        rotinas = MENU_OPTIONS["Tela"]["Display"].keys()
        for opt in rotinas:
            button = ctk.CTkButton(self.action_frame, text=opt,
                                   command=lambda o=opt: self.display_message(f"Executando: Display -> {o}"),
                                   fg_color=COLOR_ACTION_BUTTON_FG,
                                   text_color=COLOR_ACTION_BUTTON_TEXT,
                                   hover_color="gray50")
            button.pack(padx=10, pady=5, fill="x")

        # Botão Voltar (que volta para o Nível 2)
        back_button = ctk.CTkButton(self.action_frame, text="< Voltar", fg_color="red",
                                    command=lambda: self.action_frame.grid_forget())
        back_button.pack(padx=10, pady=(20, 10), fill="x", side="bottom")

    def show_file_action_options(self, action_type):
        """Mostra opções detalhadas do Arquivos (Mantido do passo anterior) - Nível 3."""
        self.clear_frame(self.action_frame)

        # Lógica de cores e botões de arquivo (mantido do passo anterior)
        ctk.CTkLabel(self.action_frame,
                     text=f"OPÇÕES DE {action_type.upper()}",
                     font=ctk.CTkFont(weight="bold"),
                     text_color="white",  # Mantido branco para contraste
                     fg_color="transparent").pack(padx=10, pady=10)

        if action_type == "Exportar":
            options = ["RAW (.SCR)", "PNG", "JPEG"]
        elif action_type == "Abrir":
            options = ["Abrir Arquivo", "Opções de Filtro"]
        else:
            options = [f"Detalhe 1 de {action_type}", f"Detalhe 2 de {action_type}"]

        for opt in options:
            button = ctk.CTkButton(self.action_frame, text=opt,
                                   command=lambda o=opt: self.display_message(f"Executando: {action_type} -> {o}"))
            button.pack(padx=10, pady=5, fill="x")

        back_button = ctk.CTkButton(self.action_frame, text="< Voltar Nível 2", fg_color="orange",
                                    command=lambda: self.action_frame.grid_forget())
        back_button.pack(padx=10, pady=(20, 10), fill="x", side="bottom")

    # --- Funções Utilitárias e de Ação (Mantidas) ---

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def clear_submenus(self):
        """Limpa e esconde as colunas de submenu e ação."""
        self.clear_frame(self.submenu_frame)
        self.clear_frame(self.action_frame)
        self.submenu_frame.grid_forget()
        self.action_frame.grid_forget()
        self.current_menu = None
        self.current_submenu = None
        self.display_message("Menu Principal Ativo. Selecione uma opção.")
        self.status_label.configure(text="Pronto.")

    def handle_command_input(self, event):
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, 'end')

        if command.lower() in ["exit", "quit", "encerra"]:
            self.quit_app()
        elif command:
            self.display_message(f"Comando recebido: {command} (Implementar parser de comandos!)")
            self.status_label.configure(text=f"Executando comando: {command}")
        else:
            self.status_label.configure(text="Status: Aguardando comando...")

    def show_version_info(self):
        version_text = (
            "**Graphos IV - Editor Gráfico MSX SCREEN 2**\n\n"
            "Versão: 0.1 (Alpha)\n"
            "Inspirado em: Graphos III (Renato Degiovani - 1987)\n"
            "Desenvolvido com: Python, CustomTkinter, SQLite\n"
            "Suporte IA: Google Gemini"
        )
        self.display_message(version_text)
        self.status_label.configure(text="Exibindo informações da versão.")

    def quit_app(self):
        if messagebox.askyesno("Confirmar Encerramento", "Tem certeza que deseja fechar o Graphos IV?"):
            self.destroy()

    def display_message(self, text):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_content_frame, text=text, font=ctk.CTkFont(size=18)).pack(padx=20, pady=200)


# --- Código da Splash Screen (Inalterado) ---
class SplashScreen(ctk.CTkToplevel):
    # ... (código da SplashScreen omitido para brevidade, é o mesmo da V4.0)
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Carregando...")
        self.overrideredirect(True)
        self.pil_image = None
        self.load_image()
        if self.pil_image:
            self.center_window()
        master.after(SPLASH_DURATION_MS, self.destroy_splash_and_open_main)

    def load_image(self):
        if not os.path.exists(LOGO_FILENAME):
            self.image_label = ctk.CTkLabel(self, text="Logotipo não encontrado!", width=400, height=300)
            self.image_label.pack(padx=20, pady=20)
            return
        try:
            self.pil_image = Image.open(LOGO_FILENAME)
            img_width, img_height = self.pil_image.size
            self.tk_image = ctk.CTkImage(light_image=self.pil_image, size=(img_width, img_height))
            self.image_label = ctk.CTkLabel(self, image=self.tk_image, text="")
            self.image_label.pack(padx=0, pady=0)
        except Exception as e:
            self.pil_image = None
            self.image_label = ctk.CTkLabel(self, text=f"Erro de carregamento:\n{e}", width=400, height=300)
            self.image_label.pack(padx=20, pady=20)

    def center_window(self):
        if self.pil_image:
            width, height = self.pil_image.size
        else:
            width, height = 400, 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def destroy_splash_and_open_main(self):
        self.destroy()
        self.master.deiconify()


# --- Execução Principal ---
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    app = App()
    splash = SplashScreen(app)
    app.mainloop()