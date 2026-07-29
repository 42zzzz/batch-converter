import shutil
import tempfile
import unittest
from pathlib import Path

from src.converter import Converter, ConversionError, SUPPORTED_EXTENSIONS


class TestConverter(unittest.TestCase):
    def setUp(self):
        self.converter = Converter()
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_validate_file_missing(self):
        with self.assertRaises(FileNotFoundError):
            self.converter.validate_file("nonexistent.pdf")

    def test_validate_file_unsupported_extension(self):
        f = self.tmpdir / "readme.txt"
        f.write_text("plain text", encoding="utf-8")
        txt_ext = f.suffix.lower()
        other = self.tmpdir / "readme.xyz"
        other.write_text("some content", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.converter.validate_file(str(other))

    def test_validate_file_supported(self):
        for ext in list(SUPPORTED_EXTENSIONS)[:5]:
            f = self.tmpdir / f"sample{ext}"
            f.write_text("content", encoding="utf-8")
            result = self.converter.validate_file(str(f))
            self.assertTrue(result)

    def test_convert_creates_markdown_file(self):
        f = self.tmpdir / "test.txt"
        f.write_text("Hello world", encoding="utf-8")

        out_dir = self.tmpdir / "output"
        result = self.converter.convert(str(f), str(out_dir))
        self.assertIsNotNone(result)
        self.assertTrue(Path(result).exists())
        content = Path(result).read_text(encoding="utf-8")
        self.assertIn("Hello world", content)

    def test_convert_retry_exhaustion(self):
        missing = self.tmpdir / "ghost.txt"
        with self.assertRaises(ConversionError):
            self.converter.convert(str(missing), str(self.tmpdir / "out"), retries=1)

    def test_supported_extensions_are_lowercase(self):
        for ext in SUPPORTED_EXTENSIONS:
            self.assertEqual(ext, ext.lower())


if __name__ == "__main__":
    unittest.main()
