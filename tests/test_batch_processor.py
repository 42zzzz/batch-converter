import shutil
import tempfile
import unittest
from pathlib import Path

from src.batch_processor import BatchProcessor


class TestBatchProcessor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.input_dir = self.tmpdir / "input"
        self.output_dir = self.tmpdir / "output"
        self.log_dir = self.tmpdir / "logs"
        self.input_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_scan_files_empty(self):
        processor = BatchProcessor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            log_dir=str(self.log_dir),
        )
        files = processor.scan_files()
        self.assertEqual(files, [])

    def test_scan_files_finds_multiple_types(self):
        (self.input_dir / "doc1.pdf").write_bytes(b"%PDF-1.4")
        (self.input_dir / "doc2.txt").write_text("hello")
        (self.input_dir / "doc3.html").write_text("<html></html>")
        (self.input_dir / "notes.xyz").write_text("unsupported")

        processor = BatchProcessor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            log_dir=str(self.log_dir),
        )
        files = processor.scan_files()
        self.assertEqual(len(files), 3)

    def test_save_and_load_progress(self):
        processor = BatchProcessor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            log_dir=str(self.log_dir),
        )
        data = {"completed": ["a.pdf", "b.txt"], "failed": []}
        processor.save_progress(data)

        loaded = processor.load_progress()
        self.assertEqual(loaded, data)

    def test_process_all_no_files(self):
        processor = BatchProcessor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            log_dir=str(self.log_dir),
        )
        result = processor.process_all()
        self.assertIsNotNone(result)
        self.assertEqual(len(result["succeeded"]), 0)
        self.assertEqual(len(result["failed"]), 0)


if __name__ == "__main__":
    unittest.main()
