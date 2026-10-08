import shutil
import tempfile
import unittest
from pathlib import Path

from src.ocr_handler import OcrHandler


class TestOcrHandler(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.ocr_handler = OcrHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_auto_detect_tesseract_returns_string_or_none(self):
        cmd = OcrHandler.auto_detect_tesseract()
        if cmd is not None:
            self.assertTrue(Path(cmd).exists())

    def test_extract_text_from_nonexistent_file(self):
        ghost = self.tmpdir / "nonexistent.png"
        text = self.ocr_handler.extract_text_from_file(ghost)
        self.assertEqual(text, "")

    def test_handler_initialization(self):
        handler = OcrHandler(language="fra", tesseract_cmd="/custom/path/tesseract")
        self.assertEqual(handler.language, "fra")
        self.assertEqual(handler.tesseract_cmd, "/custom/path/tesseract")


if __name__ == "__main__":
    unittest.main()
