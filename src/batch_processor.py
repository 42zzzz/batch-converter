import sys
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.converter import Converter, ConversionError, SUPPORTED_EXTENSIONS
from src.ocr_handler import OcrHandler

logger = logging.getLogger(__name__)


class TkinterLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")
        try:
            self.text_widget.after(0, append)
        except Exception:
            pass


class BatchProcessor:
    PROGRESS_FILE = ".batch_progress.json"

    def __init__(self, input_dir=None, output_dir=None, log_dir="logs", enable_ocr=True, ocr_lang="eng", tesseract_path=None):
        self.input_dir = Path(input_dir) if input_dir else None
        self.output_dir = Path(output_dir) if output_dir else (Path.cwd() / "Markdown")
        self.log_dir = Path(log_dir)
        self.enable_ocr = enable_ocr
        self.ocr_lang = ocr_lang
        self.tesseract_path = tesseract_path

        self.converter = Converter(
            enable_ocr=self.enable_ocr,
            ocr_language=self.ocr_lang,
            tesseract_cmd=self.tesseract_path
        )
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self):
        log_file = self.log_dir / f"conversion_{datetime.now():%Y%m%d_%H%M%S}.log"
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(fh)
        root.addHandler(ch)

        logger.info(f"Logging to {log_file}")

    def scan_files(self):
        if not self.input_dir or not self.input_dir.exists():
            return []

        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(self.input_dir.glob(f"*{ext}"))
        files = sorted(set(files))
        return files

    def _progress_path(self):
        return self.log_dir / self.PROGRESS_FILE

    def load_progress(self):
        path = self._progress_path()
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}

    def save_progress(self, data):
        path = self._progress_path()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def process_all(self, resume=False):
        files = self.scan_files()
        if not files:
            logger.info("No supported files to process.")
            return {"succeeded": [], "failed": []}

        progress = self.load_progress() if resume else {}
        completed = set(progress.get("completed", []))

        results = {"succeeded": [], "failed": []}

        for f in files:
            if resume and str(f) in completed:
                results["succeeded"].append(str(f))
                continue

            try:
                self.converter.validate_file(f)
                out = self.converter.convert(f, self.output_dir)
                results["succeeded"].append(str(f))
                logger.info(f"OK: {f.name} -> {out}")
            except (ConversionError, Exception) as e:
                results["failed"].append({"file": str(f), "error": str(e)})
                logger.error(f"FAIL: {f.name} — {e}")

            progress["completed"] = results["succeeded"]
            progress["failed"] = results["failed"]
            self.save_progress(progress)

        return results


class BatchConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MarkItDown Batch Converter & OCR Pro")
        self.root.geometry("950x750")
        self.root.minsize(800, 600)

        self.selected_files = []
        self.output_mode_var = tk.StringVar(value="same")  # "same" or "custom"
        self.output_directory = tk.StringVar(value=str(Path.cwd() / "Markdown"))
        self.ocr_enabled_var = tk.BooleanVar(value=True)
        self.ocr_lang_var = tk.StringVar(value="eng")
        
        detected_tess = OcrHandler.auto_detect_tesseract()
        self.tesseract_path_var = tk.StringVar(value=detected_tess or "")

        self._build_styles()
        self._build_ui()
        self._setup_file_logging()

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("THeading.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("TSubHeading.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="MarkItDown Batch Converter with OCR", style="THeading.TLabel").pack(side=tk.LEFT)
        
        panes = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        left_frame = ttk.LabelFrame(panes, text=" Document Queue ", padding=10)
        panes.add(left_frame, weight=3)

        btn_box = ttk.Frame(left_frame)
        btn_box.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(btn_box, text="Add Files...", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Add Folder...", command=self.add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Clear All", command=self.clear_files).pack(side=tk.RIGHT)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("name", "size", "path"), show="headings", selectmode="extended")
        self.tree.heading("name", text="File Name")
        self.tree.heading("size", text="Size (KB)")
        self.tree.heading("path", text="Full Path")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("size", width=80, anchor="e")
        self.tree.column("path", width=250, anchor="w")

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        right_frame = ttk.LabelFrame(panes, text=" Settings & OCR ", padding=10)
        panes.add(right_frame, weight=2)

        # Output Settings
        ttk.Label(right_frame, text="Output Location:", style="TSubHeading.TLabel").pack(anchor="w", pady=(0, 2))
        
        self.same_dir_radio = ttk.Radiobutton(right_frame, text="Output in the same directory as each file", variable=self.output_mode_var, value="same", command=self.toggle_output_mode)
        self.same_dir_radio.pack(anchor="w", pady=(0, 2))
        
        self.custom_dir_radio = ttk.Radiobutton(right_frame, text="Output to custom directory:", variable=self.output_mode_var, value="custom", command=self.toggle_output_mode)
        self.custom_dir_radio.pack(anchor="w", pady=(0, 2))

        self.out_box = ttk.Frame(right_frame)
        self.out_box.pack(fill=tk.X, pady=(0, 12))
        self.out_entry = ttk.Entry(self.out_box, textvariable=self.output_directory, state="disabled")
        self.out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.out_btn = ttk.Button(self.out_box, text="Browse...", command=self.browse_output, state="disabled")
        self.out_btn.pack(side=tk.RIGHT)

        ocr_frame = ttk.LabelFrame(right_frame, text=" OCR Configuration ", padding=8)
        ocr_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Checkbutton(ocr_frame, text="Enable OCR on Images / Embedded Docs", variable=self.ocr_enabled_var).pack(anchor="w", pady=(0, 5))
        
        lang_box = ttk.Frame(ocr_frame)
        lang_box.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(lang_box, text="Language Code:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(lang_box, textvariable=self.ocr_lang_var, width=10).pack(side=tk.LEFT)
        ttk.Label(lang_box, text=" (e.g. eng, fra, deu)").pack(side=tk.LEFT)

        ttk.Label(ocr_frame, text="Tesseract Executable Path:").pack(anchor="w", pady=(2, 2))
        tess_box = ttk.Frame(ocr_frame)
        tess_box.pack(fill=tk.X, pady=(0, 5))
        self.tess_entry = ttk.Entry(tess_box, textvariable=self.tesseract_path_var)
        self.tess_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(tess_box, text="Find...", command=self.browse_tesseract).pack(side=tk.RIGHT)

        tess_status_box = ttk.Frame(ocr_frame)
        tess_status_box.pack(fill=tk.X, pady=(2, 0))
        self.tess_status_lbl = ttk.Label(tess_status_box, text="", font=("Segoe UI", 9))
        self.tess_status_lbl.pack(side=tk.LEFT)
        ttk.Button(tess_status_box, text="Test OCR", command=self.test_ocr_installation).pack(side=tk.RIGHT)

        self.update_tesseract_status_display()

        self.convert_btn = ttk.Button(right_frame, text="Convert Selected Files", style="Accent.TButton", command=self.start_conversion_thread)
        self.convert_btn.pack(fill=tk.X, pady=(10, 0))

        console_frame = ttk.LabelFrame(main_frame, text=" Real-Time Console Log ", padding=10)
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        console_sub = ttk.Frame(console_frame)
        console_sub.pack(fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(console_sub, wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9), state="disabled")
        console_scroll = ttk.Scrollbar(console_sub, orient=tk.VERTICAL, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=console_scroll.set)

        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _setup_file_logging(self):
        tk_handler = TkinterLogHandler(self.console_text)
        tk_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        tk_handler.setFormatter(formatter)
        logging.getLogger().addHandler(tk_handler)

    def update_tesseract_status_display(self):
        path = self.tesseract_path_var.get().strip()
        handler = OcrHandler(tesseract_cmd=path if path else None)
        if handler.is_available():
            self.tess_status_lbl.configure(text="Tesseract Ready", foreground="green")
        else:
            self.tess_status_lbl.configure(text="Tesseract Unavailable / Invalid", foreground="red")

    def test_ocr_installation(self):
        path = self.tesseract_path_var.get().strip()
        handler = OcrHandler(tesseract_cmd=path if path else None)
        if handler.is_available():
            messagebox.showinfo("OCR Test", f"Tesseract is successfully detected and functional!\nPath: {handler.tesseract_cmd}")
        else:
            messagebox.showwarning(
                "OCR Not Found",
                "Tesseract OCR executable could not be verified.\n\n"
                "Please install Tesseract OCR:\n"
                "• Windows (winget): winget install UB-Mannheim.TesseractOCR\n"
                "• macOS: brew install tesseract\n"
                "• Linux: sudo apt install tesseract-ocr"
            )
        self.update_tesseract_status_display()

    def add_files(self):
        exts_list = [f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS)]
        filetypes = [("Supported Documents", " ".join(exts_list)), ("All Files", "*.*")]
        paths = filedialog.askopenfilenames(title="Select Files to Convert", filetypes=filetypes)
        if paths:
            for p in paths:
                path_obj = Path(p)
                if path_obj not in self.selected_files:
                    self.selected_files.append(path_obj)
                    size_kb = round(path_obj.stat().st_size / 1024, 1)
                    self.tree.insert("", tk.END, values=(path_obj.name, f"{size_kb} KB", str(path_obj)))
            logger.info(f"Added {len(paths)} file(s) to queue.")

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Documents")
        if folder:
            folder_path = Path(folder)
            added_count = 0
            for ext in SUPPORTED_EXTENSIONS:
                for p in folder_path.glob(f"*{ext}"):
                    if p not in self.selected_files:
                        self.selected_files.append(p)
                        size_kb = round(p.stat().st_size / 1024, 1)
                        self.tree.insert("", tk.END, values=(p.name, f"{size_kb} KB", str(p)))
                        added_count += 1
            logger.info(f"Scanned folder {folder_path.name}: added {added_count} supported file(s).")

    def remove_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        for item in selected_items:
            vals = self.tree.item(item, "values")
            if vals:
                path_str = vals[2]
                path_obj = Path(path_str)
                if path_obj in self.selected_files:
                    self.selected_files.remove(path_obj)
            self.tree.delete(item)
        logger.info("Removed selected items from queue.")

    def clear_files(self):
        self.selected_files.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        logger.info("Cleared file queue.")

    def toggle_output_mode(self):
        if self.output_mode_var.get() == "custom":
            self.out_entry.configure(state="normal")
            self.out_btn.configure(state="normal")
        else:
            self.out_entry.configure(state="disabled")
            self.out_btn.configure(state="disabled")

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.output_directory.set(folder)

    def browse_tesseract(self):
        path = filedialog.askopenfilename(title="Select tesseract.exe", filetypes=[("Executable", "*.exe"), ("All Files", "*.*")])
        if path:
            self.tesseract_path_var.set(path)
            self.update_tesseract_status_display()

    def start_conversion_thread(self):
        if not self.selected_files:
            messagebox.showwarning("Empty Queue", "Please add at least one file or folder to convert.")
            return

        self.convert_btn.configure(state="disabled")
        thread = threading.Thread(target=self.run_conversion_task, daemon=True)
        thread.start()

    def run_conversion_task(self):
        output_mode = self.output_mode_var.get()
        custom_output_dir = Path(self.output_directory.get())
        enable_ocr = self.ocr_enabled_var.get()
        ocr_lang = self.ocr_lang_var.get().strip() or "eng"
        tess_path = self.tesseract_path_var.get().strip() or None

        logger.info(f"Starting batch conversion of {len(self.selected_files)} file(s)...")
        if output_mode == "same":
            logger.info("Output Mode: Same directory as each selected file")
        else:
            logger.info(f"Output Directory: {custom_output_dir}")
        logger.info(f"OCR Enabled: {enable_ocr} (Lang: {ocr_lang})")

        converter = Converter(
            enable_ocr=enable_ocr,
            ocr_language=ocr_lang,
            tesseract_cmd=tess_path
        )

        succeeded = 0
        failed = 0

        for idx, file_path in enumerate(self.selected_files, start=1):
            logger.info(f"[{idx}/{len(self.selected_files)}] Processing {file_path.name}...")
            try:
                converter.validate_file(file_path)
                target_dir = file_path.parent if output_mode == "same" else custom_output_dir
                out = converter.convert(file_path, target_dir)
                logger.info(f"✔ Success: {file_path.name} -> {Path(out)}")
                succeeded += 1
            except Exception as e:
                logger.error(f"✘ Failed: {file_path.name} — {e}")
                failed += 1

        logger.info("========================================")
        logger.info(f"Batch conversion completed! Succeeded: {succeeded}, Failed: {failed}")
        if output_mode == "same":
            logger.info("Markdown files saved to their respective source directories.")
        else:
            logger.info(f"Markdown files saved to: {custom_output_dir}")
        logger.info("========================================")

        try:
            msg_target = "each file's source directory" if output_mode == "same" else str(custom_output_dir)
            self.root.after(0, lambda: messagebox.showinfo("Done", f"Batch conversion finished!\nSucceeded: {succeeded}\nFailed: {failed}\n\nSaved to: {msg_target}"))
            self.root.after(0, lambda: self.convert_btn.configure(state="normal"))
        except Exception:
            pass


def main():
    root = tk.Tk()
    app = BatchConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
