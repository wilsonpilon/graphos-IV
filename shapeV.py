import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk, ImageDraw
import struct
import os

# --- Constantes e Paleta MSX ---
# Paleta aproximada do MSX1
MSX_PALETTE = [
    (0, 0, 0),  # 0: Transparent (Black)
    (0, 0, 0),  # 1: Black
    (32, 192, 32),  # 2: Medium Green
    (96, 224, 96),  # 3: Light Green
    (32, 32, 224),  # 4: Dark Blue
    (64, 96, 224),  # 5: Light Blue
    (160, 32, 32),  # 6: Dark Red
    (64, 192, 224),  # 7: Cyan
    (224, 32, 32),  # 8: Medium Red
    (224, 96, 96),  # 9: Light Red
    (192, 192, 32),  # 10: Dark Yellow
    (192, 192, 128),  # 11: Light Yellow
    (32, 128, 32),  # 12: Dark Green
    (192, 64, 160),  # 13: Magenta
    (160, 160, 160),  # 14: Gray
    (224, 224, 224)  # 15: White
]


class ShapeViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Graphos IV - Shape Viewer (Python Edition)")
        self.geometry("800x600")

        # Configuração do Grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#008080", height=40, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.header_frame, text="MSX SHAPE VIEWER",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(pady=5)

        # --- Área Principal (Canvas de visualização) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="gray20")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Canvas onde desenharemos os Shapes (Zoomed)
        self.canvas_bg = "black"
        self.canvas = Canvas(self.main_frame, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Rodapé / Controles ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="#008000", height=50, corner_radius=0)
        self.footer_frame.grid(row=2, column=0, sticky="ew")

        self.btn_load = ctk.CTkButton(self.footer_frame, text="Carregar .SHP",
                                      command=self.load_shape_file, fg_color="#FFD700", text_color="black")
        self.btn_load.pack(side="left", padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(self.footer_frame, text="Aguardando arquivo...", text_color="white")
        self.lbl_status.pack(side="left", padx=20)

        self.btn_next = ctk.CTkButton(self.footer_frame, text="Próximo Shape >",
                                      command=self.next_shape, state="disabled", fg_color="gray50")
        self.btn_next.pack(side="right", padx=20, pady=10)

        # Variáveis de Controle do Arquivo
        self.file_handle = None
        self.current_shape_data = None
        self.file_size = 0

        # Buffer simulado (como no Pascal: array [0..$47FF] of Byte)
        # No Python, usamos listas ou bytearrays dinâmicos, mas a estrutura lógica se mantém
        self.GRPCGP_OFFSET = 0x0000
        self.GRPCOL_OFFSET = 0x1800
        self.GRPMsk_OFFSET = 0x3000

    def load_shape_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Shape Files", "*.shp"), ("All Files", "*.*")])
        if not file_path:
            return

        try:
            if self.file_handle:
                self.file_handle.close()

            self.file_handle = open(file_path, "rb")
            self.file_size = os.path.getsize(file_path)

            self.lbl_status.configure(text=f"Arquivo carregado: {os.path.basename(file_path)}")
            self.next_shape()  # Tenta ler o primeiro shape

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir arquivo: {e}")

    def next_shape(self):
        if not self.file_handle:
            return

        try:
            # Pascal: Read(F1, K); -> Lê 1 byte (Número do Shape)
            k_byte = self.file_handle.read(1)

            # Verifica fim do arquivo ou marcador FF
            if not k_byte:
                self.lbl_status.configure(text="Fim do arquivo.")
                self.btn_next.configure(state="disabled")
                self.file_handle.close()
                self.file_handle = None
                return

            k = struct.unpack('B', k_byte)[0]

            if k == 0xFF:  # Marcador de fim lógico no Graphos
                self.lbl_status.configure(text="Fim dos Shapes (Marcador FF encontrado).")
                self.btn_next.configure(state="disabled")
                return

            # Lê T (Type), S (Size/Largura em bytes?), H (Height/Altura em linhas)
            # Pascal: Read(F1,T); Read(F1,S); Read(F1,H);
            header = self.file_handle.read(3)
            if len(header) < 3:
                return  # Arquivo corrompido/incompleto

            t, s, h = struct.unpack('BBB', header)

            w_blocks = s // 8  # Largura em caracteres (tiles)

            # Atualiza Status
            info_text = f"Shape: {k} | Tipo: {t} | Tamanho: ({w_blocks}x{h} tiles) / Raw S={s}"
            self.lbl_status.configure(text=info_text)
            self.btn_next.configure(state="normal", fg_color="#FFD700", text_color="black")

            # Limpa e prepara buffers
            # O buffer total é grande, mas vamos alocar apenas o necessário para o shape atual
            buffer_size = s * h
            buffer_cgp = bytearray(buffer_size)  # Pattern
            buffer_col = bytearray(buffer_size)  # Color
            buffer_msk = bytearray(buffer_size)  # Mask

            # Lógica de leitura baseada no TIPO (Case T of...)
            # Tipos mapeados do Pascal original:

            if t == 1:
                # Lê apenas Pattern, Cor fixa F0 (Branco sobre Transparente/Preto)
                buffer_cgp = self.file_handle.read(buffer_size)
                buffer_col = b'\xF0' * buffer_size

            elif t == 2:
                # Lê Pattern e depois Color
                buffer_cgp = self.file_handle.read(buffer_size)
                buffer_col = self.file_handle.read(buffer_size)

            elif t == 3:
                # Lê Mask, depois Pattern. (Cor fixa F0)
                buffer_msk = self.file_handle.read(buffer_size)
                buffer_cgp = self.file_handle.read(buffer_size)
                buffer_col = b'\xF0' * buffer_size
                # Nota: O original mostra shape normal, espera tecla, mostra mascara.
                # Vamos mostrar o Shape normal composto.

            elif t == 4:
                # Lê Mask, Pattern, Color
                buffer_msk = self.file_handle.read(buffer_size)
                buffer_cgp = self.file_handle.read(buffer_size)
                buffer_col = self.file_handle.read(buffer_size)

            # Renderiza
            self.draw_shape(w_blocks, h, buffer_cgp, buffer_col, buffer_msk)

        except Exception as e:
            self.lbl_status.configure(text=f"Erro na leitura: {e}")
            print(e)

    def draw_shape(self, w_tiles, h_tiles, buf_pattern, buf_color, buf_mask):
        """
        Reimplementação da procedure ShowShape do Pascal.
        w_tiles: Largura em blocos de 8 pixels
        h_tiles: Altura em blocos de 8 pixels
        """

        self.canvas.delete("all")

        # Escala visual (Zoom)
        ZOOM = 4

        # Dimensões em pixels reais
        px_width = w_tiles * 8
        px_height = h_tiles * 8

        # Cria imagem PIL
        img = Image.new("RGB", (px_width, px_height), "black")
        pixels = img.load()

        # Lógica de Loop do Pascal convertida:
        # for Y:=0 to H-1 do (Note que H no pascal original parecia ser altura em LINHAS DE PIXEL ou TILES?)
        # Analisando o Pascal: A:=X+Y*W; ... A:=X+Y*32; ... (A div 32)*8 + T*64...
        # O loop do Pascal original iterava sobre TILES (caracteres 8x8).

        # Vamos iterar sobre Tiles (Blocos 8x8)
        # W e H no pascal eram passados como Tiles.

        for ty in range(h_tiles):
            for tx in range(w_tiles):

                # Cálculo do offset linear base (similar a A:=X+Y*W no Pascal)
                # O "S" lido do arquivo era Largura * 8. Logo o loop do Pascal iterava linearmente no buffer.

                # Offset linear no buffer de bytes lido
                tile_index = (tx + ty * w_tiles) * 8

                # Dentro de cada Tile, iteramos as 8 linhas (D:=0 to 7)
                for line in range(8):
                    byte_pos = tile_index + line

                    if byte_pos >= len(buf_pattern): break

                    pattern_byte = buf_pattern[byte_pos]
                    color_byte = buf_color[byte_pos]

                    # Extrai cores MSX (Foreground / Background)
                    fg_color_idx = color_byte // 16
                    bg_color_idx = color_byte % 16

                    fg_rgb = MSX_PALETTE[fg_color_idx]
                    bg_rgb = MSX_PALETTE[bg_color_idx]

                    # Itera sobre os 8 bits do byte (pixels)
                    for bit in range(8):
                        # Pascal: if (P and($80 shr E))<>0 then
                        is_set = (pattern_byte & (0x80 >> bit)) != 0

                        pixel_x = (tx * 8) + bit
                        pixel_y = (ty * 8) + line

                        if is_set:
                            pixels[pixel_x, pixel_y] = fg_rgb
                        else:
                            pixels[pixel_x, pixel_y] = bg_rgb

        # --- Exibir no Canvas com Zoom ---
        # Redimensiona para visualização (Nearest Neighbor para manter pixel art crocante)
        img_zoomed = img.resize((px_width * ZOOM, px_height * ZOOM), Image.Resampling.NEAREST)

        self.tk_img = ImageTk.PhotoImage(img_zoomed)

        # Centralizar no Canvas
        canvas_w = int(self.canvas.winfo_width())
        canvas_h = int(self.canvas.winfo_height())
        center_x = canvas_w // 2
        center_y = canvas_h // 2

        self.canvas.create_image(center_x, center_y, image=self.tk_img, anchor="center")

        # Desenha borda ao redor
        w_z = px_width * ZOOM
        h_z = px_height * ZOOM
        x1 = center_x - (w_z // 2)
        y1 = center_y - (h_z // 2)
        self.canvas.create_rectangle(x1, y1, x1 + w_z, y1 + h_z, outline="white", width=2)


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ShapeViewerApp()
    app.mainloop()