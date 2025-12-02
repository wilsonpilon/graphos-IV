import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import struct

# Configuração do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Paleta MSX1 (aproximação RGB)
MSX_PALETTE = [
    (0, 0, 0),  # 0: Transparent (Black)
    (0, 0, 0),  # 1: Black
    (35, 178, 53),  # 2: Medium Green
    (109, 231, 116),  # 3: Light Green
    (54, 59, 236),  # 4: Dark Blue
    (115, 119, 246),  # 5: Light Blue
    (171, 53, 49),  # 6: Dark Red
    (74, 213, 247),  # 7: Cyan
    (229, 62, 54),  # 8: Medium Red
    (241, 123, 117),  # 9: Light Red
    (201, 196, 56),  # 10: Dark Yellow
    (218, 215, 125),  # 11: Light Yellow
    (31, 138, 56),  # 12: Dark Green
    (176, 87, 182),  # 13: Magenta
    (176, 176, 176),  # 14: Gray
    (255, 255, 255)  # 15: White
]


class MSXScreenViewer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Graphos III - MSX Screen 2 Viewer")
        self.geometry("1000x850")

        # Dados da imagem carregada
        self.raw_data = None
        self.original_image = None
        self.current_zoom = 4  # Padrão 4x
        self.view_mode = "normal"  # normal, bw, color

        self.create_widgets()

    def create_widgets(self):
        # --- Painel Lateral de Controle ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        ctk.CTkLabel(self.sidebar, text="Controles", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Botão Carregar
        self.btn_load = ctk.CTkButton(self.sidebar, text="Carregar .SCR", command=self.load_file)
        self.btn_load.pack(padx=20, pady=10)

        # Modos de Visualização
        ctk.CTkLabel(self.sidebar, text="Modo de Visualização:", anchor="w").pack(padx=20, pady=(20, 5), fill="x")
        self.mode_var = ctk.StringVar(value="normal")

        self.radio_normal = ctk.CTkRadioButton(self.sidebar, text="Normal (Pixels + Cor)", variable=self.mode_var,
                                               value="normal", command=self.update_display)
        self.radio_normal.pack(padx=20, pady=5, anchor="w")

        self.radio_bw = ctk.CTkRadioButton(self.sidebar, text="Preto e Branco", variable=self.mode_var, value="bw",
                                           command=self.update_display)
        self.radio_bw.pack(padx=20, pady=5, anchor="w")

        self.radio_color = ctk.CTkRadioButton(self.sidebar, text="Apenas Cores", variable=self.mode_var, value="color",
                                              command=self.update_display)
        self.radio_color.pack(padx=20, pady=5, anchor="w")

        # Zoom
        ctk.CTkLabel(self.sidebar, text="Zoom:", anchor="w").pack(padx=20, pady=(20, 5), fill="x")
        self.zoom_combo = ctk.CTkComboBox(self.sidebar, values=["1x", "2x", "3x", "4x", "5x"],
                                          command=self.on_zoom_change)
        self.zoom_combo.set("4x")
        self.zoom_combo.pack(padx=20, pady=10)

        # Botão Salvar
        self.btn_save = ctk.CTkButton(self.sidebar, text="Salvar Imagem (PNG/BMP)", command=self.save_image,
                                      fg_color="green")
        self.btn_save.pack(padx=20, pady=(40, 10))

        # --- Área de Exibição Principal ---
        self.display_area = ctk.CTkScrollableFrame(self, label_text="Visualização")
        self.display_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.image_label = ctk.CTkLabel(self.display_area,
                                        text="Nenhuma imagem carregada.\nSelecione um arquivo .SCR (Graphos III).")
        self.image_label.pack(expand=True, pady=50)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Abrir Arquivo MSX Screen 2",
            filetypes=[("MSX Screen Files", "*.scr *.SCR"), ("Todos os arquivos", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, "rb") as f:
                # Baseado no Pascal: lê 128 bytes (cabeçalho) e descarta
                header = f.read(128)
                # Lê o restante (dump de memória VRAM)
                # O Pascal lê até $3000 bytes (12KB = 12288 bytes)
                content = f.read(12288)

                if len(content) < 12288:
                    # Se for menor, preenche com zeros (segurança)
                    content = content + b'\x00' * (12288 - len(content))

                self.raw_data = content
                self.update_display()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler arquivo: {e}")

    def process_msx_screen2(self, data, mode):
        # Screen 2 Resolution: 256x192
        width, height = 256, 192
        img = Image.new("RGB", (width, height), "black")
        pixels = img.load()

        # Endereços base conforme msxscrvw.pas
        # GRPCGP = $0000 (Padrões/Pixels)
        # GRPCOL = $1800 (Cores) -> Offset 6144 decimal
        base_pattern = 0
        base_color = 0x1800

        # A tela é dividida em 3 terços verticais
        # T = 0 (linhas 0-63), T = 1 (linhas 64-127), T = 2 (linhas 128-191)
        for t in range(3):
            # Cada terço tem 256 posições de caracteres (32 colunas * 8 linhas de char)
            # Pascal: A := 0 to $FF
            for a in range(256):
                col_char = a % 32
                row_char = a // 32

                # Offset base para este bloco de 8x8 pixels
                block_offset = (a * 8) + (t * 0x800)

                # Coordenadas base na tela
                screen_x_base = col_char * 8
                screen_y_base = (t * 64) + (row_char * 8)

                # Processar as 8 linhas do caractere
                # Pascal: D := 0 to 7
                for d in range(8):
                    # Byte de Padrão (Bitmap)
                    pattern_byte = data[base_pattern + block_offset + d]

                    # Byte de Cor
                    color_byte = data[base_color + block_offset + d]

                    # Extrair cores (MSX High Nibble = FG, Low Nibble = BG)
                    fg_idx = (color_byte >> 4) & 0x0F
                    bg_idx = color_byte & 0x0F

                    # Ajustes conforme o modo selecionado
                    if mode == "bw":
                        fg_rgb = MSX_PALETTE[15]  # Branco
                        bg_rgb = MSX_PALETTE[1]  # Preto
                        # pattern_byte permanece o mesmo
                    elif mode == "color":
                        # No modo "apenas cor", ignoramos o desenho (pattern)
                        # Para visualizar as cores do byte, vamos desenhar
                        # metade do bloco com a cor de fundo e metade com a frente
                        # ou simplesmente usar o padrão sólido.
                        # Vamos forçar um padrão visual: Metade esquerda FG, metade direita BG
                        pattern_byte = 0xF0
                        fg_rgb = MSX_PALETTE[fg_idx]
                        bg_rgb = MSX_PALETTE[bg_idx]
                    else:  # normal
                        fg_rgb = MSX_PALETTE[fg_idx]
                        bg_rgb = MSX_PALETTE[bg_idx]

                    # Desenhar os 8 pixels da linha
                    # Pascal: E := 0 to 7
                    for e in range(8):
                        # Bit mais à esquerda é o bit 7
                        bit = (pattern_byte >> (7 - e)) & 1

                        if bit == 1:
                            pixels[screen_x_base + e, screen_y_base + d] = fg_rgb
                        else:
                            pixels[screen_x_base + e, screen_y_base + d] = bg_rgb

        return img

    def update_display(self):
        if self.raw_data is None:
            return

        mode = self.mode_var.get()
        self.original_image = self.process_msx_screen2(self.raw_data, mode)

        # Aplicar Zoom
        w, h = self.original_image.size
        new_w = w * self.current_zoom
        new_h = h * self.current_zoom

        # Resize usando NEAREST para manter os pixels nítidos (estilo retro)
        zoomed_img = self.original_image.resize((new_w, new_h), Image.NEAREST)

        self.tk_image = ImageTk.PhotoImage(zoomed_img)
        self.image_label.configure(image=self.tk_image, text="")

    def on_zoom_change(self, value):
        self.current_zoom = int(value.replace("x", ""))
        self.update_display()

    def save_image(self):
        if self.original_image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem para salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("BMP Image", "*.bmp")],
            title="Salvar Imagem"
        )

        if file_path:
            # Pergunta se o usuário quer salvar com o zoom atual ou tamanho original
            save_zoomed = messagebox.askyesno("Opção de Salvamento",
                                              f"Deseja salvar com o zoom atual ({self.current_zoom}x)?\n(Não = Tamanho Original 256x192)")

            if save_zoomed:
                w, h = self.original_image.size
                final_img = self.original_image.resize((w * self.current_zoom, h * self.current_zoom), Image.NEAREST)
                final_img.save(file_path)
            else:
                self.original_image.save(file_path)

            messagebox.showinfo("Sucesso", "Imagem salva com sucesso!")


if __name__ == "__main__":
    app = MSXScreenViewer()
    app.mainloop()