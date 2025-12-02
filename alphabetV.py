import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw


class AlfViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphos III - Visualizador de Alfabeto MSX (.ALF)")
        self.root.geometry("640x480")
        self.root.configure(bg="#2e2e2e")

        # Variáveis de estado
        self.font_data = None
        self.char_images = []

        # Configuração do Layout
        main_frame = tk.Frame(root, bg="#2e2e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Painel Esquerdo: Tabela de Caracteres ---
        left_panel = tk.Frame(main_frame, bg="#404040", bd=2, relief=tk.SUNKEN)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        lbl_title_table = tk.Label(left_panel, text="Tabela 16x16 (Zoom 2x)", bg="#404040", fg="white")
        lbl_title_table.pack(pady=5)

        # Canvas para desenhar a tabela de caracteres
        # Tamanho original: 16 chars * 8 px = 128px.
        # Zoom 2x: 256px.
        self.canvas_table = tk.Canvas(left_panel, width=256, height=256, bg="black", highlightthickness=0)
        self.canvas_table.pack(padx=10, pady=10)
        self.canvas_table.bind("<Button-1>", self.on_table_click)

        # --- Painel Direito: Detalhes e Controles ---
        right_panel = tk.Frame(main_frame, bg="#2e2e2e")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Botão de Carregar
        btn_load = tk.Button(right_panel, text="Abrir Arquivo .ALF", command=self.load_file,
                             bg="#505050", fg="white", relief=tk.RAISED)
        btn_load.pack(fill=tk.X, pady=(0, 20))

        # Área de Detalhe (Zoom 16x)
        lbl_title_detail = tk.Label(right_panel, text="Caractere Selecionado (Zoom 16x)", bg="#2e2e2e", fg="white")
        lbl_title_detail.pack()

        self.canvas_detail = tk.Canvas(right_panel, width=128, height=128, bg="black", highlightthickness=1,
                                       highlightbackground="gray")
        self.canvas_detail.pack(pady=10)

        self.lbl_char_info = tk.Label(right_panel, text="Código: ---", bg="#2e2e2e", fg="gray")
        self.lbl_char_info.pack()

        # Imagens persistentes
        self.tk_table_img = None
        self.tk_detail_img = None

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Abrir Alfabeto Graphos III",
            filetypes=[("Graphos Alphabet", "*.ALF"), ("All Files", "*.*")],
            initialdir="./readers"
        )

        if not file_path:
            return

        try:
            with open(file_path, "rb") as f:
                # 1. Ler Cabeçalho (7 bytes)
                # O Pascal lê e sobrescreve o buffer, mas a estrutura do arquivo é: 7 bytes Header + 2048 Data
                header = f.read(7)

                # 2. Ler Dados da Fonte (2048 bytes)
                data = f.read(2048)

                if len(data) != 2048:
                    raise ValueError(f"Arquivo incompleto. Esperado 2048 bytes de dados, lido {len(data)}.")

                self.font_data = data
                self.process_data()
                self.draw_table()

                self.select_char(65)

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler arquivo:\n{e}")

    def process_data(self):
        self.char_images = []

        for i in range(256):
            char_bytes = self.font_data[i * 8: (i + 1) * 8]

            # Usar RGB para garantir visibilidade correta no Tkinter
            img = Image.new('RGB', (8, 8), color='black')
            pixels = img.load()

            for row in range(8):
                byte = char_bytes[row]
                for col in range(8):
                    # Lógica equivalente ao Pascal: if (P and($80 shr B))<>0
                    # Bit 7 é o mais à esquerda (col 0)
                    if (byte >> (7 - col)) & 1:
                        pixels[col, row] = (255, 255, 255)  # Branco

            self.char_images.append(img)

    def draw_table(self):
        if not self.char_images:
            return

        self.canvas_table.delete("all")

        base_width = 16 * 8
        base_height = 16 * 8
        full_table = Image.new('RGB', (base_width, base_height), 'black')

        for idx, img in enumerate(self.char_images):
            row = idx // 16
            col = idx % 16
            x = col * 8
            y = row * 8
            full_table.paste(img, (x, y))

        # Zoom 2x usando Nearest para manter o aspecto "pixelado"
        zoomed_table = full_table.resize((256, 256), resample=Image.NEAREST)

        self.tk_table_img = ImageTk.PhotoImage(zoomed_table)
        self.canvas_table.create_image(0, 0, anchor=tk.NW, image=self.tk_table_img)

    def on_table_click(self, event):
        if not self.font_data:
            return

        x_zoom = event.x
        y_zoom = event.y

        # Coordenadas base (sem zoom 2x)
        x_orig = x_zoom // 2
        y_orig = y_zoom // 2

        col = x_orig // 8
        row = y_orig // 8

        char_index = (row * 16) + col

        if 0 <= char_index <= 255:
            self.select_char(char_index)

    def select_char(self, index):
        if not self.char_images:
            return

        char_img = self.char_images[index]

        # Zoom 16x para o detalhe (8px * 16 = 128px)
        detail_img = char_img.resize((128, 128), resample=Image.NEAREST)

        self.tk_detail_img = ImageTk.PhotoImage(detail_img)
        self.canvas_detail.create_image(64, 64, anchor=tk.CENTER, image=self.tk_detail_img)

        self.lbl_char_info.config(
            text=f"Char: {chr(index) if 32 <= index <= 126 else '.'} | Dec: {index} | Hex: ${index:02X}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AlfViewerApp(root)
    root.mainloop()