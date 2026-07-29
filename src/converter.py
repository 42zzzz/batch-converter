import logging
from pathlib import Path

from markitdown import MarkItDown

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
    def __init__(self):
        self._engine = MarkItDown()

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
                output_path.write_text(result.text_content, encoding="utf-8")
                logger.info(f"Wrote: {output_path}")
                return str(output_path)
            except Exception as e:
                logger.error(f"Attempt {attempt} failed for {file_path.name}: {e}")
                if attempt == retries:
                    raise ConversionError(
                        f"Failed to convert {file_path.name} after {retries} attempts"
                    ) from e
