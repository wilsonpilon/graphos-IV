import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import struct
import os

# --- Configurações de Cores do Tema (Baseado no Graphos IV) ---
COLOR_HEADER_BG = "#008080"
COLOR_BG = "gray20"
COLOR_PIXEL_ON = (255, 255, 255)  # Branco (conforme msxlayvm.pas usa cor 15)
COLOR_PIXEL_OFF = (0, 0, 0)  # Preto


class ExportDialog(ctk.CTkToplevel):
    """
    Diálogo para exportar a imagem (Reutilizado do padrão do projeto).
    """

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Exportar Layout")
        self.geometry("300x200")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")

        ctk.CTkLabel(self, text="Opções de Exportação", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        ctk.CTkLabel(self, text="Ampliação (Zoom):").pack(pady=(10, 0))
        self.combo_zoom = ctk.CTkComboBox(self, values=["1x", "2x", "3x", "4x"])
        self.combo_zoom.set("2x")
        self.combo_zoom.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x")

        ctk.CTkButton(btn_frame, text="Salvar", command=self.on_confirm, fg_color="#008000").pack(side="left", padx=10,
                                                                                                  expand=True)
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="red").pack(side="right", padx=10,
                                                                                             expand=True)

    def on_confirm(self):
        zoom_str = self.combo_zoom.get().split("x")[0]
        self.callback(int(zoom_str))
        self.destroy()


class LayViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Graphos IV - Layout Viewer (.LAY)")
        self.geometry("800x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_HEADER_BG, height=40, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.header_frame, text="MSX GRAPHOS III LAYOUT VIEWER",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(pady=5)

        # --- Área Principal ---
        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Canvas para desenhar
        self.canvas = Canvas(self.main_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Mensagem inicial no canvas
        self.canvas.create_text(400, 250, text="Carregue um arquivo .LAY", fill="gray", font=("Arial", 16))

        # --- Rodapé ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="#004040", height=60, corner_radius=0)
        self.footer_frame.grid(row=2, column=0, sticky="ew")

        self.btn_load = ctk.CTkButton(self.footer_frame, text="Abrir Arquivo .LAY",
                                      command=self.load_lay_file, fg_color="#FFD700", text_color="black")
        self.btn_load.pack(side="left", padx=20, pady=10)

        self.lbl_info = ctk.CTkLabel(self.footer_frame, text="", text_color="silver")
        self.lbl_info.pack(side="left", padx=20)

        self.btn_export = ctk.CTkButton(self.footer_frame, text="Exportar Imagem",
                                        command=self.open_export_dialog, state="disabled", fg_color="#2060A0")
        self.btn_export.pack(side="right", padx=20, pady=10)

        # Dados
        self.current_pil_image = None
        self.current_filename = None

    def load_lay_file(self):
        path = filedialog.askopenfilename(filetypes=[("Graphos Layout", "*.lay"), ("All Files", "*.*")])
        if not path:
            return

        try:
            buffer = self.decode_graphos_lay(path)
            self.current_filename = os.path.basename(path)
            self.render_buffer_to_screen(buffer)

            self.lbl_info.configure(
                text=f"Arquivo: {self.current_filename} | Tamanho Decodificado: {len(buffer)} bytes")
            self.btn_export.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Falha ao ler o arquivo .LAY:\n{str(e)}")

    def decode_graphos_lay(self, filepath):
        """
        Implementa a lógica de descompressão do msxlayvm.pas
        """
        decoded_buffer = bytearray()

        with open(filepath, "rb") as f:
            # Ignora 3 bytes iniciais
            f.read(3)

            # Lê cabeçalho de tamanho/controle
            # Pascal: Read(F1,E); Read(F1,F); A:=F*256+E+1-$9200;
            byte_e = f.read(1)
            byte_f = f.read(1)

            if not byte_e or not byte_f:
                raise ValueError("Arquivo muito curto ou cabeçalho inválido.")

            e_val = ord(byte_e)
            f_val = ord(byte_f)

            # 'counter' equivale à variável A no Pascal
            counter = (f_val * 256) + e_val + 1 - 0x9200

            # Ignora mais 2 bytes
            f.read(2)

            # Loop de descompressão (while A > 0)
            # O buffer no Pascal tem limite de $1800 (6144 bytes) que é o tamanho do PGT (Pattern Generator Table)
            MAX_SIZE = 0x1800

            while counter > 0 and len(decoded_buffer) < MAX_SIZE:
                char = f.read(1)
                if not char:
                    break

                raw_val = ord(char)
                counter -= 1  # A:=A-1

                # Transformação
                # if E>=$99 then E:=E-$99 else E:=E+$67;
                if raw_val >= 0x99:
                    val = raw_val - 0x99
                else:
                    val = raw_val + 0x67

                # Verifica se é marcador de repetição (RLE)
                # if (E=0)or(E=$FF) then ...
                if val == 0x00 or val == 0xFF:
                    # Lê quantidade
                    count_char = f.read(1)
                    if count_char:
                        count = ord(count_char)
                        # Pascal loop: for C:=0 to F-1 do Buffer[B+C]:=E;
                        for _ in range(count):
                            if len(decoded_buffer) < MAX_SIZE:
                                decoded_buffer.append(val)
                else:
                    # Valor literal
                    decoded_buffer.append(val)

        # Preenche o restante com 0 se for menor que 6144 (segurança)
        if len(decoded_buffer) < 6144:
            decoded_buffer.extend(b'\x00' * (6144 - len(decoded_buffer)))

        return decoded_buffer

    def render_buffer_to_screen(self, buffer):
        """
        Converte o buffer (Pattern Table) em uma imagem PIL monocromática.
        Lógica baseada no loop de desenho do Pascal.
        """
        width, height = 256, 192
        img = Image.new("RGB", (width, height), COLOR_PIXEL_OFF)
        pixels = img.load()

        # MSX Screen 2 Layout:
        # A tela é dividida em 3 terços (Top, Mid, Bot).
        # Cada terço tem 256 tiles (32 colunas * 8 linhas de tiles).
        # Cada tile tem 8 bytes (1 byte por linha de pixel).

        for t in range(3):  # 3 terços (Banks)
            for a in range(256):  # 256 caracteres/tiles por terço
                # Calcula offset base no buffer
                # B:=A*8+T*$800;
                base_offset = (a * 8) + (t * 0x800)

                # Posição do Tile na tela
                tile_x = (a % 32) * 8
                tile_y = (a // 32) * 8 + (t * 64)

                for d in range(8):  # 8 linhas por tile
                    if base_offset + d >= len(buffer):
                        break

                    p = buffer[base_offset + d]

                    # Desenha os 8 pixels desta linha
                    # Pascal: if (P and($80 shr E))<>0 then PutPixel(...)
                    for bit in range(8):
                        if (p & (0x80 >> bit)) != 0:
                            px = tile_x + bit
                            py = tile_y + d
                            pixels[px, py] = COLOR_PIXEL_ON

        self.current_pil_image = img

        # Exibe na GUI (com zoom padrão de 2x para melhor visibilidade)
        self.update_canvas_image(2)

    def update_canvas_image(self, zoom_factor):
        if not self.current_pil_image:
            return

        w, h = self.current_pil_image.size
        new_w = w * zoom_factor
        new_h = h * zoom_factor

        # Nearest Neighbor para manter o aspecto "pixelado" retrô
        img_zoomed = self.current_pil_image.resize((new_w, new_h), Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(img_zoomed)

        self.canvas.delete("all")

        # Centralizar
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        cx = c_width // 2
        cy = c_height // 2

        self.canvas.create_image(cx, cy, image=self.tk_img, anchor="center")

        # Borda
        self.canvas.create_rectangle(cx - new_w // 2, cy - new_h // 2,
                                     cx + new_w // 2, cy + new_h // 2,
                                     outline="white")

    def open_export_dialog(self):
        if self.current_pil_image:
            ExportDialog(self, self.perform_export)

    def perform_export(self, scale):
        if not self.current_pil_image:
            return

        file_types = [("PNG Image", "*.png"), ("BMP Image", "*.bmp")]
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=file_types,
                                                initialfile=f"{self.current_filename}.png")
        if filename:
            try:
                w, h = self.current_pil_image.size
                export_img = self.current_pil_image.resize((w * scale, h * scale), Image.Resampling.NEAREST)
                export_img.save(filename)
                messagebox.showinfo("Sucesso", f"Layout exportado com sucesso!\nEscala: {scale}x")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar imagem: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = LayViewerApp()
    app.mainloop()