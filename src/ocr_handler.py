import os
import sys
import logging
import zipfile
import io
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class OcrHandler:
    def __init__(self, language="eng", tesseract_cmd=None):
        self.language = language
        self.tesseract_cmd = tesseract_cmd or self.auto_detect_tesseract()
        if self.tesseract_cmd and OCR_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    @staticmethod
    def auto_detect_tesseract():
        # Common installation paths on Windows and Unix
        candidates = []
        if os.name == "nt":
            candidates = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
                os.path.expandvars(r"%ProgramFiles%\Tesseract-OCR\tesseract.exe"),
            ]
        else:
            candidates = [
                "/usr/bin/tesseract",
                "/usr/local/bin/tesseract",
                "/opt/homebrew/bin/tesseract",
            ]

        for path in candidates:
            if path and os.path.exists(path):
                return path

        # Check if tesseract is in PATH
        import shutil
        found = shutil.which("tesseract")
        if found:
            return found

        return None

    def is_available(self):
        if not OCR_AVAILABLE:
            return False
        cmd = self.tesseract_cmd or self.auto_detect_tesseract()
        if not cmd or not os.path.exists(cmd):
            return False
        try:
            pytesseract.pytesseract.tesseract_cmd = cmd
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_text_from_image_bytes(self, image_bytes):
        if not self.is_available():
            return ""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image, lang=self.language)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed on image bytes: {e}")
            return ""

    def extract_text_from_file(self, file_path):
        file_path = Path(file_path)
        if not file_path.exists():
            return ""

        suffix = file_path.suffix.lower()
        extracted_sections = []

        if not self.is_available():
            logger.warning("Tesseract OCR is not available or not configured. Skipping OCR.")
            return ""

        try:
            # 1. Standalone Images (.png, .jpg, .jpeg, etc.)
            if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
                with open(file_path, "rb") as f:
                    text = self.extract_text_from_image_bytes(f.read())
                    if text:
                        extracted_sections.append(f"### OCR Text from {file_path.name}\n\n{text}")

            # 2. PDFs (extract embedded images via PyPDF2)
            elif suffix == ".pdf":
                from PyPDF2 import PdfReader
                reader = PdfReader(str(file_path))
                for page_idx, page in enumerate(reader.pages):
                    try:
                        images = page.images
                        for img_idx, img_file_object in enumerate(images):
                            img_bytes = img_file_object.data
                            text = self.extract_text_from_image_bytes(img_bytes)
                            if text:
                                extracted_sections.append(
                                    f"### OCR Text from PDF Page {page_idx + 1}, Image {img_idx + 1} ({img_file_object.name})\n\n{text}"
                                )
                    except Exception as pe:
                        logger.debug(f"Failed to extract images from PDF page {page_idx + 1}: {pe}")

            # 3. Office Docs (.docx, .pptx, .xlsx, .epub) which are ZIP archives containing media
            elif suffix in {".docx", ".pptx", ".xlsx", ".epub"}:
                with zipfile.ZipFile(file_path, "r") as zf:
                    for filename in zf.namelist():
                        if any(filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]):
                            try:
                                img_bytes = zf.read(filename)
                                text = self.extract_text_from_image_bytes(img_bytes)
                                if text:
                                    extracted_sections.append(
                                        f"### OCR Text from Embedded Image ({filename})\n\n{text}"
                                    )
                            except Exception as ze:
                                logger.debug(f"Failed to OCR embedded zip image {filename}: {ze}")

        except Exception as e:
            logger.error(f"Error during OCR extraction for {file_path.name}: {e}")

        if extracted_sections:
            return "\n\n---\n## Extracted Text from Embedded Images (OCR)\n\n" + "\n\n".join(extracted_sections)

        return ""
