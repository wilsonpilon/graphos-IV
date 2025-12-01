import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import struct
import os

# --- Constantes e Paleta MSX ---
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


class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Exportar Imagem")
        self.geometry("300x200")
        self.resizable(False, False)

        # Modal
        self.transient(parent)
        self.grab_set()

        # Centralizar
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")

        ctk.CTkLabel(self, text="Opções de Exportação", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        # Opção de Zoom
        ctk.CTkLabel(self, text="Ampliação (Zoom):").pack(pady=(10, 0))
        self.combo_zoom = ctk.CTkComboBox(self, values=["1x (Original)", "2x", "3x", "4x", "8x", "16x"])
        self.combo_zoom.set("4x")
        self.combo_zoom.pack(pady=5)

        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x")

        ctk.CTkButton(btn_frame, text="Salvar Como...", command=self.on_confirm, fg_color="#008000").pack(side="left",
                                                                                                          padx=10,
                                                                                                          expand=True)
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="red").pack(side="right", padx=10,
                                                                                             expand=True)

    def on_confirm(self):
        zoom_str = self.combo_zoom.get().split("x")[0]  # Pega só o numero
        zoom = int(zoom_str)
        self.callback(zoom)
        self.destroy()


class ShapeViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Graphos IV - Shape Viewer (Python Edition)")
        self.geometry("900x650")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#008080", height=40, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.header_frame, text="MSX SHAPE VIEWER",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(pady=5)

        # --- Área Principal ---
        self.main_frame = ctk.CTkFrame(self, fg_color="gray20")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.canvas = Canvas(self.main_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Rodapé ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="#004040", height=60, corner_radius=0)
        self.footer_frame.grid(row=2, column=0, sticky="ew")

        # Botão Load
        self.btn_load = ctk.CTkButton(self.footer_frame, text="Abrir Arquivo .SHP",
                                      command=self.load_shape_file, fg_color="#FFD700", text_color="black")
        self.btn_load.pack(side="left", padx=20, pady=10)

        # Navegação (Frame Centralizado)
        nav_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        nav_frame.pack(side="left", expand=True)

        self.btn_prev = ctk.CTkButton(nav_frame, text="< Anterior", width=80,
                                      command=self.prev_shape, state="disabled", fg_color="gray50")
        self.btn_prev.pack(side="left", padx=5)

        self.lbl_counter = ctk.CTkLabel(nav_frame, text="0 / 0", text_color="white", font=("Arial", 14, "bold"))
        self.lbl_counter.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(nav_frame, text="Próximo >", width=80,
                                      command=self.next_shape, state="disabled", fg_color="gray50")
        self.btn_next.pack(side="left", padx=5)

        # Exportação
        self.btn_export = ctk.CTkButton(self.footer_frame, text="Exportar Imagem",
                                        command=self.open_export_dialog, state="disabled", fg_color="#2060A0")
        self.btn_export.pack(side="right", padx=20, pady=10)

        # Variáveis de Controle
        self.file_path = None
        self.shape_offsets = []  # Lista de posições (offsets) de cada shape no arquivo
        self.current_index = -1
        self.current_pil_image = None  # Armazena a imagem original (1x) para exportação

    def load_shape_file(self):
        path = filedialog.askopenfilename(filetypes=[("Shape Files", "*.shp"), ("All Files", "*.*")])
        if not path:
            return

        self.file_path = path
        if self.scan_file_offsets(path):
            self.current_index = 0
            self.update_controls()
            self.load_shape_at_index(0)
        else:
            messagebox.showinfo("Info", "Nenhum shape válido encontrado ou arquivo vazio.")

    def scan_file_offsets(self, path):
        """Lê o arquivo inteiro rapidamente para mapear onde começa cada shape."""
        self.shape_offsets = []
        try:
            with open(path, "rb") as f:
                while True:
                    offset = f.tell()
                    k_byte = f.read(1)

                    if not k_byte: break  # EOF real

                    k = struct.unpack('B', k_byte)[0]
                    if k == 0xFF: break  # Marcador de Fim lógico do Graphos

                    # Header: T(1), S(1), H(1)
                    header = f.read(3)
                    if len(header) < 3: break
                    t, s, h = struct.unpack('BBB', header)

                    # Adiciona este offset à lista
                    self.shape_offsets.append(offset)

                    # Calcula tamanho dos dados para pular
                    # S = largura (em pixels/unidades internas), H = altura
                    # Tamanho base de um plane = S * H bytes
                    plane_size = s * h

                    skip_bytes = 0
                    if t == 1:
                        skip_bytes = plane_size  # Ptn
                    elif t == 2:
                        skip_bytes = plane_size * 2  # Ptn + Col
                    elif t == 3:
                        skip_bytes = plane_size * 2  # Msk + Ptn
                    elif t == 4:
                        skip_bytes = plane_size * 3  # Msk + Ptn + Col

                    f.seek(skip_bytes, 1)  # Pula relativo a posição atual

            return len(self.shape_offsets) > 0

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao indexar arquivo: {e}")
            return False

    def update_controls(self):
        total = len(self.shape_offsets)
        if total == 0:
            self.lbl_counter.configure(text="0 / 0")
            self.btn_prev.configure(state="disabled", fg_color="gray50")
            self.btn_next.configure(state="disabled", fg_color="gray50")
            self.btn_export.configure(state="disabled", fg_color="gray50")
            return

        display_idx = self.current_index + 1
        self.lbl_counter.configure(text=f"{display_idx} / {total}")

        # Botão Anterior
        if self.current_index > 0:
            self.btn_prev.configure(state="normal", fg_color="#FFD700")
        else:
            self.btn_prev.configure(state="disabled", fg_color="gray50")

        # Botão Próximo
        if self.current_index < total - 1:
            self.btn_next.configure(state="normal", fg_color="#FFD700")
        else:
            self.btn_next.configure(state="disabled", fg_color="gray50")

        # Exportar sempre ativo se houver imagem
        self.btn_export.configure(state="normal", fg_color="#2060A0")

    def prev_shape(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_shape_at_index(self.current_index)
            self.update_controls()

    def next_shape(self):
        if self.current_index < len(self.shape_offsets) - 1:
            self.current_index += 1
            self.load_shape_at_index(self.current_index)
            self.update_controls()

    def load_shape_at_index(self, index):
        if not self.file_path or index < 0 or index >= len(self.shape_offsets):
            return

        offset = self.shape_offsets[index]

        try:
            with open(self.file_path, "rb") as f:
                f.seek(offset)

                # Re-lê cabeçalho
                k = struct.unpack('B', f.read(1))[0]
                t, s, h = struct.unpack('BBB', f.read(3))

                w_blocks = s // 8
                buffer_size = s * h

                # Buffers temporários
                buffer_cgp = bytearray(buffer_size)
                buffer_col = bytearray(buffer_size)
                buffer_msk = bytearray(buffer_size)

                if t == 1:
                    buffer_cgp = f.read(buffer_size)
                    buffer_col = b'\xF0' * buffer_size
                elif t == 2:
                    buffer_cgp = f.read(buffer_size)
                    buffer_col = f.read(buffer_size)
                elif t == 3:
                    buffer_msk = f.read(buffer_size)
                    buffer_cgp = f.read(buffer_size)
                    buffer_col = b'\xF0' * buffer_size
                elif t == 4:
                    buffer_msk = f.read(buffer_size)
                    buffer_cgp = f.read(buffer_size)
                    buffer_col = f.read(buffer_size)

                self.draw_shape(w_blocks, h, buffer_cgp, buffer_col, buffer_msk)

        except Exception as e:
            print(f"Erro ao ler shape no index {index}: {e}")

    def draw_shape(self, w_tiles, h_tiles, buf_pattern, buf_color, buf_mask):
        self.canvas.delete("all")

        px_width = w_tiles * 8
        px_height = h_tiles * 8

        # Cria imagem PIL Original (1x)
        img = Image.new("RGB", (px_width, px_height), "black")
        pixels = img.load()

        for ty in range(h_tiles):
            for tx in range(w_tiles):
                tile_index = (tx + ty * w_tiles) * 8

                for line in range(8):
                    byte_pos = tile_index + line
                    if byte_pos >= len(buf_pattern): break

                    pattern_byte = buf_pattern[byte_pos]
                    color_byte = buf_color[byte_pos]

                    fg_rgb = MSX_PALETTE[color_byte // 16]
                    bg_rgb = MSX_PALETTE[color_byte % 16]

                    for bit in range(8):
                        is_set = (pattern_byte & (0x80 >> bit)) != 0
                        pixel_x = (tx * 8) + bit
                        pixel_y = (ty * 8) + line

                        if is_set:
                            pixels[pixel_x, pixel_y] = fg_rgb
                        else:
                            pixels[pixel_x, pixel_y] = bg_rgb

        # Guarda imagem original para exportação
        self.current_pil_image = img

        # Exibição (Zoom Fixo Visual 4x)
        VIEWER_ZOOM = 4
        w_z = px_width * VIEWER_ZOOM
        h_z = px_height * VIEWER_ZOOM

        img_zoomed = img.resize((w_z, h_z), Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(img_zoomed)

        canvas_w = int(self.canvas.winfo_width())
        canvas_h = int(self.canvas.winfo_height())
        cx, cy = canvas_w // 2, canvas_h // 2

        self.canvas.create_image(cx, cy, image=self.tk_img, anchor="center")
        self.canvas.create_rectangle(cx - w_z // 2, cy - h_z // 2, cx + w_z // 2, cy + h_z // 2, outline="white",
                                     width=2)

    def open_export_dialog(self):
        if not self.current_pil_image:
            return
        ExportDialog(self, self.perform_export)

    def perform_export(self, scale):
        if not self.current_pil_image:
            return

        # Pede ao usuário onde salvar
        file_types = [("PNG Image", "*.png"), ("BMP Image", "*.bmp")]
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=file_types)

        if not filename:
            return

        try:
            # Processa o redimensionamento
            original_w, original_h = self.current_pil_image.size
            new_w = original_w * scale
            new_h = original_h * scale

            # Usa NEAREST para manter o visual pixel art sem borrões
            export_img = self.current_pil_image.resize((new_w, new_h), Image.Resampling.NEAREST)

            export_img.save(filename)
            messagebox.showinfo("Sucesso", f"Imagem salva com sucesso!\nEscala: {scale}x\nArquivo: {filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar imagem: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ShapeViewerApp()
    app.mainloop()