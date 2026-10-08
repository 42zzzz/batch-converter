import logging
from pathlib import Path

from markitdown import MarkItDown
from src.ocr_handler import OcrHandler

logger = logging.getLogger(__name__)


SUPPORTED_EXTENSIONS = frozenset({
    ".txt", ".text", ".md", ".markdown", ".json", ".jsonl",
    ".html", ".htm",
    ".rss", ".atom", ".xml",
    ".docx",
    ".pptx",
    ".xlsx", ".xls",
    ".pdf",
    ".jpg", ".jpeg", ".png",
    ".wav", ".mp3", ".m4a", ".mp4",
    ".msg",
    ".ipynb",
    ".epub",
    ".csv",
    ".zip",
})


class ConversionError(Exception):
    pass


class Converter:
    def __init__(self, enable_ocr=True, ocr_language="eng", tesseract_cmd=None):
        self._engine = MarkItDown()
        self.enable_ocr = enable_ocr
        self.ocr_handler = OcrHandler(language=ocr_language, tesseract_cmd=tesseract_cmd)

    def validate_file(self, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix} — expected one of: "
                f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        return True

    def convert(self, file_path, output_dir, retries=2):
        file_path = Path(file_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{file_path.stem}.md"

        if output_path.exists():
            logger.info(f"Output already exists, skipping: {output_path}")
            return str(output_path)

        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Converting [{attempt}/{retries}]: {file_path.name}")
                result = self._engine.convert(str(file_path))
                text_content = result.text_content

                if self.enable_ocr:
                    logger.info(f"Running OCR on embedded/source images for {file_path.name}...")
                    ocr_text = self.ocr_handler.extract_text_from_file(file_path)
                    if ocr_text:
                        text_content += "\n\n" + ocr_text
                        logger.info(f"Successfully extracted OCR text for {file_path.name}")

                output_path.write_text(text_content, encoding="utf-8")
                logger.info(f"Wrote: {output_path}")
                return str(output_path)
            except Exception as e:
                logger.error(f"Attempt {attempt} failed for {file_path.name}: {e}")
                if attempt == retries:
                    raise ConversionError(
                        f"Failed to convert {file_path.name} after {retries} attempts"
                    ) from e
