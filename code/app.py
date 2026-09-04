"""Image Layouter — batch crop photos to a fixed print size (e.g. 10x15 cm).

Workflow:
  1. Startup dialog asks for the print layout size (cm) and DPI.
  2. Every image in ./images/ is loaded (natural, numeric-aware order).
  3. For each photo you position/zoom a crop box matching the layout's
     aspect ratio with WASD / arrow keys, mouse drag, "1"/"2" or the
     mouse wheel to zoom.
  4. Enter, Space or Escape confirms the crop, saves it and moves on.
  5. After the last photo, all crops have been written to
     ./finished-images/ as 1.png, 2.png, ... N.png at the exact pixel
     size for the chosen layout + DPI.
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from PIL import Image, ImageTk, ImageOps

from . import config as cfg
from . import utils


class CropState:
    """Position/size of the crop box for one image, in original image pixel coordinates."""

    def __init__(self, img_w, img_h, aspect_ratio):
        self.img_w, self.img_h = img_w, img_h
        self.aspect_ratio = aspect_ratio

        self.max_box_h = min(img_h, img_w / aspect_ratio)
        self.max_box_w = self.max_box_h * aspect_ratio
        self.min_box_h = max(10.0, self.max_box_h * cfg.MIN_ZOOM_FRACTION)

        self.box_h = self.max_box_h
        self.box_w = self.max_box_w
        self.cx = img_w / 2.0
        self.cy = img_h / 2.0

    def clamp_center(self):
        half_w, half_h = self.box_w / 2.0, self.box_h / 2.0
        if self.img_w <= self.box_w:
            self.cx = self.img_w / 2.0
        else:
            self.cx = min(max(self.cx, half_w), self.img_w - half_w)
        if self.img_h <= self.box_h:
            self.cy = self.img_h / 2.0
        else:
            self.cy = min(max(self.cy, half_h), self.img_h - half_h)

    def pan(self, dx_img, dy_img):
        self.cx += dx_img
        self.cy += dy_img
        self.clamp_center()

    def zoom(self, factor):
        new_h = self.box_h * factor
        new_h = min(max(new_h, self.min_box_h), self.max_box_h)
        self.box_h = new_h
        self.box_w = new_h * self.aspect_ratio
        self.clamp_center()

    def box_px(self):
        x0 = self.cx - self.box_w / 2.0
        y0 = self.cy - self.box_h / 2.0
        x1 = self.cx + self.box_w / 2.0
        y1 = self.cy + self.box_h / 2.0
        return x0, y0, x1, y1


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Layouter")
        self.root.geometry("1100x800")
        self.root.minsize(700, 500)
        self.root.update_idletasks()

        self.images_dir = Path("images")
        self.output_dir = Path("finished-images")

        self.dpi = cfg.DEFAULT_DPI
        self.layout_w_cm = cfg.DEFAULT_LAYOUT_W_CM
        self.layout_h_cm = cfg.DEFAULT_LAYOUT_H_CM

        if not self.ask_layout_size():
            self.root.destroy()
            return

        self.aspect_ratio = self.layout_w_cm / self.layout_h_cm
        self.target_px = (
            utils.cm_to_px(self.layout_w_cm, self.dpi),
            utils.cm_to_px(self.layout_h_cm, self.dpi),
        )

        self.image_paths = utils.list_images(self.images_dir)
        if not self.image_paths:
            messagebox.showerror(
                "Rasm topilmadi",
                f"'{self.images_dir}/' papkasida hech qanday rasm topilmadi.\n"
                f"Rasmlarni shu papkaga solib, dasturni qayta ishga tushiring.",
            )
            self.root.destroy()
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.index = 0
        self.total = len(self.image_paths)
        self.current_pil = None
        self.display_source = None
        self.state = None
        self.tk_preview = None
        self.preview_scale = 1.0
        self._drag_start = None

        self.build_ui()
        self.load_current_image()
        self.root.mainloop()

    # ---------------------------------------------------------- layout dialog
    def ask_layout_size(self):
        result = {"ok": False}
        dlg = tk.Toplevel(self.root)
        dlg.title("Chop etish o'lchami")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Qog'oz o'lchamini kiriting:", font=("", 11, "bold")).grid(
            row=0, column=0, columnspan=2, padx=14, pady=(14, 8), sticky="w"
        )

        tk.Label(dlg, text="Kenglik (sm):").grid(row=1, column=0, padx=14, pady=4, sticky="e")
        w_var = tk.StringVar(value=str(cfg.DEFAULT_LAYOUT_W_CM))
        w_entry = tk.Entry(dlg, textvariable=w_var, width=10)
        w_entry.grid(row=1, column=1, padx=14, pady=4, sticky="w")

        tk.Label(dlg, text="Balandlik (sm):").grid(row=2, column=0, padx=14, pady=4, sticky="e")
        h_var = tk.StringVar(value=str(cfg.DEFAULT_LAYOUT_H_CM))
        h_entry = tk.Entry(dlg, textvariable=h_var, width=10)
        h_entry.grid(row=2, column=1, padx=14, pady=4, sticky="w")

        tk.Label(dlg, text="DPI (chop sifati):").grid(row=3, column=0, padx=14, pady=4, sticky="e")
        dpi_var = tk.StringVar(value=str(cfg.DEFAULT_DPI))
        dpi_entry = tk.Entry(dlg, textvariable=dpi_var, width=10)
        dpi_entry.grid(row=3, column=1, padx=14, pady=4, sticky="w")

        err_label = tk.Label(dlg, text="", fg="red")
        err_label.grid(row=4, column=0, columnspan=2)

        def confirm(event=None):
            try:
                w = float(w_var.get().replace(",", "."))
                h = float(h_var.get().replace(",", "."))
                d = int(float(dpi_var.get().replace(",", ".")))
                if w <= 0 or h <= 0 or d <= 0:
                    raise ValueError
            except ValueError:
                err_label.config(text="Iltimos, to'g'ri musbat son kiriting.")
                return
            self.layout_w_cm, self.layout_h_cm, self.dpi = w, h, d
            result["ok"] = True
            dlg.destroy()

        def cancel(event=None):
            dlg.destroy()

        btn_frame = tk.Frame(dlg)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=14)
        tk.Button(btn_frame, text="OK", width=10, command=confirm).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Bekor qilish", width=10, command=cancel).pack(side="left", padx=6)

        dlg.bind("<Return>", confirm)
        dlg.bind("<Escape>", cancel)
        dlg.protocol("WM_DELETE_WINDOW", cancel)
        w_entry.focus_set()
        w_entry.selection_range(0, "end")

        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2 - dlg.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2 - dlg.winfo_height() // 2)
        dlg.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        self.root.wait_window(dlg)
        return result["ok"]

    # ------------------------------------------------------------------- UI
    def build_ui(self):
        self.status_var = tk.StringVar()
        self.help_var = tk.StringVar(
            value=(
                "WASD / strelkalar: joylashtirish   |   1: yaqinlashtirish   2: uzoqlashtirish   |   "
                "Sichqoncha: bosib surish, g'ildirak: zoom   |   Enter / Space / Esc: saqlash va keyingisi"
            )
        )

        top = tk.Frame(self.root, bg="#111111")
        top.pack(side="top", fill="x")
        tk.Label(
            top, textvariable=self.status_var, fg="white", bg="#111111",
            font=("", 11, "bold"), anchor="w", padx=10, pady=6,
        ).pack(side="left")

        self.canvas = tk.Canvas(self.root, bg=cfg.CANVAS_BG, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)

        bottom = tk.Frame(self.root, bg="#111111")
        bottom.pack(side="bottom", fill="x")
        tk.Label(
            bottom, textvariable=self.help_var, fg="#cccccc", bg="#111111",
            anchor="w", padx=10, pady=6,
        ).pack(side="left")

        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows / macOS
        self.canvas.bind("<Button-4>", lambda e: self.on_zoom(1 / cfg.ZOOM_FACTOR))  # Linux scroll up
        self.canvas.bind("<Button-5>", lambda e: self.on_zoom(cfg.ZOOM_FACTOR))  # Linux scroll down

        self.root.bind("<KeyPress>", self.on_keypress)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------- key/mouse
    def on_keypress(self, event):
        if self.state is None:
            return
        key = event.keysym.lower()
        if key in ("w", "up"):
            self._pan(0, -1)
        elif key in ("s", "down"):
            self._pan(0, 1)
        elif key in ("a", "left"):
            self._pan(-1, 0)
        elif key in ("d", "right"):
            self._pan(1, 0)
        elif key == "1":
            self.on_zoom(1 / cfg.ZOOM_FACTOR)
        elif key == "2":
            self.on_zoom(cfg.ZOOM_FACTOR)
        elif key in ("return", "space", "escape"):
            self.confirm_and_next()

    def _pan(self, dx, dy):
        step = self.state.box_h * cfg.PAN_STEP_FRACTION
        self.state.pan(dx * step, dy * step)
        self.redraw()

    def on_zoom(self, factor):
        if self.state is None:
            return
        self.state.zoom(factor)
        self.redraw()

    def on_mousewheel(self, event):
        if self.state is None:
            return
        if event.delta > 0:
            self.on_zoom(1 / cfg.ZOOM_FACTOR)
        else:
            self.on_zoom(cfg.ZOOM_FACTOR)

    def on_drag_start(self, event):
        if self.state is None:
            return
        self._drag_start = (event.x, event.y, self.state.cx, self.state.cy)

    def on_drag_move(self, event):
        if self.state is None or self._drag_start is None or self.preview_scale <= 0:
            return
        sx, sy, start_cx, start_cy = self._drag_start
        dx_img = (event.x - sx) / self.preview_scale
        dy_img = (event.y - sy) / self.preview_scale
        self.state.cx = start_cx + dx_img
        self.state.cy = start_cy + dy_img
        self.state.clamp_center()
        self.redraw()

    # ------------------------------------------------------------ image i/o
    def load_current_image(self):
        path = self.image_paths[self.index]
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
        except Exception as e:
            messagebox.showerror("Xatolik", f"'{path.name}' rasmini ochib bo'lmadi:\n{e}\n\nO'tkazib yuborilmoqda.")
            del self.image_paths[self.index]
            self.total = len(self.image_paths)
            if not self.image_paths:
                messagebox.showinfo("Tugadi", "Ishlov beriladigan rasm qolmadi.")
                self.root.destroy()
                return
            if self.index >= len(self.image_paths):
                self.index = len(self.image_paths) - 1
            self.load_current_image()
            return

        self.current_pil = img
        scale0 = min(1.0, cfg.MAX_PREVIEW_SIDE / max(img.width, img.height))
        if scale0 < 1.0:
            self.display_source = img.resize(
                (max(1, int(img.width * scale0)), max(1, int(img.height * scale0))), Image.LANCZOS
            )
        else:
            self.display_source = img

        self.state = CropState(img.width, img.height, self.aspect_ratio)
        self.status_var.set(f"{self.index + 1}/{self.total} — {path.name}  ({img.width}x{img.height}px)")
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        if self.current_pil is None:
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            return

        img_w, img_h = self.current_pil.width, self.current_pil.height
        scale = min(cw / img_w, ch / img_h)
        disp_w, disp_h = max(1, int(img_w * scale)), max(1, int(img_h * scale))
        offset_x = (cw - disp_w) // 2
        offset_y = (ch - disp_h) // 2
        self.preview_scale = scale

        preview = self.display_source.resize((disp_w, disp_h), Image.BILINEAR)
        self.tk_preview = ImageTk.PhotoImage(preview)
        self.canvas.create_image(offset_x, offset_y, anchor="nw", image=self.tk_preview)

        x0, y0, x1, y1 = self.state.box_px()
        bx0 = offset_x + x0 * scale
        by0 = offset_y + y0 * scale
        bx1 = offset_x + x1 * scale
        by1 = offset_y + y1 * scale

        # Dim everything outside the crop box.
        self.canvas.create_rectangle(offset_x, offset_y, offset_x + disp_w, by0,
                                      fill="black", stipple=cfg.DIM_STIPPLE, outline="")
        self.canvas.create_rectangle(offset_x, by1, offset_x + disp_w, offset_y + disp_h,
                                      fill="black", stipple=cfg.DIM_STIPPLE, outline="")
        self.canvas.create_rectangle(offset_x, by0, bx0, by1,
                                      fill="black", stipple=cfg.DIM_STIPPLE, outline="")
        self.canvas.create_rectangle(bx1, by0, offset_x + disp_w, by1,
                                      fill="black", stipple=cfg.DIM_STIPPLE, outline="")

        self.canvas.create_rectangle(bx0, by0, bx1, by1, outline=cfg.BOX_OUTLINE_COLOR, width=2)

    # ------------------------------------------------------------ export
    def confirm_and_next(self):
        if self.current_pil is None or self.state is None:
            return
        if not self.export_current():
            return
        self.current_pil.close()
        self.index += 1
        if self.index >= len(self.image_paths):
            self.finish()
        else:
            self.load_current_image()

    def export_current(self):
        try:
            x0, y0, x1, y1 = self.state.box_px()
            x0, y0 = max(0, int(round(x0))), max(0, int(round(y0)))
            x1 = min(self.current_pil.width, int(round(x1)))
            y1 = min(self.current_pil.height, int(round(y1)))
            cropped = self.current_pil.crop((x0, y0, x1, y1))
            resized = cropped.resize(self.target_px, Image.LANCZOS)
            out_path = self.output_dir / f"{self.index + 1}.png"
            resized.save(out_path, dpi=(self.dpi, self.dpi))
            return True
        except Exception as e:
            messagebox.showerror("Xatolik", f"Rasmni saqlashda xatolik yuz berdi:\n{e}")
            return False

    def finish(self):
        self.canvas.delete("all")
        self.current_pil = None
        self.state = None
        msg = (
            f"Hammasi tayyor!\n{self.total} ta rasm '{self.output_dir}/' papkasiga "
            f"{self.target_px[0]}x{self.target_px[1]}px ({self.layout_w_cm:g}x{self.layout_h_cm:g} sm, "
            f"{self.dpi} DPI) o'lchamda saqlandi."
        )
        self.status_var.set("Tayyor!")
        messagebox.showinfo("Tayyor", msg)
        self.root.destroy()

    def on_close(self):
        if self.state is None or messagebox.askyesno(
            "Chiqish", "Dasturdan chiqishni xohlaysizmi? Saqlanmagan progress yo'qoladi."
        ):
            self.root.destroy()


def main():
    App()


if __name__ == "__main__":
    main()
