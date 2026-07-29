import sys
import json
import logging
from pathlib import Path
from datetime import datetime

from tqdm import tqdm

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.converter import Converter, ConversionError, SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class BatchProcessor:
    PROGRESS_FILE = ".batch_progress.json"

    def __init__(self, input_dir="input", output_dir="output", log_dir="logs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.log_dir = Path(log_dir)
        self.converter = Converter()

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
        if not self.input_dir.exists():
            logger.warning(f"Input directory does not exist: {self.input_dir}")
            return []

        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(self.input_dir.glob(f"*{ext}"))
        files = sorted(set(files))

        logger.info(f"Found {len(files)} supported file(s) in {self.input_dir}")
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

        if resume and completed:
            logger.info(f"Resuming — {len(completed)} already processed")

        results = {"succeeded": [], "failed": []}

        for f in tqdm(files, desc="Converting files", unit="file"):
            if resume and str(f) in completed:
                logger.info(f"Skipping (already done): {f.name}")
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

        self._report(results)
        return results

    @staticmethod
    def _report(results):
        succeeded = len(results["succeeded"])
        failed = len(results["failed"])
        total = succeeded + failed
        logger.info(f"Done: {succeeded}/{total} succeeded, {failed}/{total} failed")
        if failed:
            logger.warning("Failed files:")
            for entry in results["failed"]:
                logger.warning(f"  - {entry['file']}: {entry['error']}")


def prompt_for_folder():
    print("MarkItDown Batch Converter")
    print("=" * 30)
    while True:
        raw = input("Enter the path to the folder containing documents: ").strip()
        if not raw:
            print("Path cannot be empty. Try again.")
            continue
        path = Path(raw).resolve()
        if not path.exists():
            print(f"Path does not exist: {path}")
            continue
        if not path.is_dir():
            print(f"Not a directory: {path}")
            continue
        return path


def main():
    folder = prompt_for_folder()
    output_dir = folder / "Markdown"
    log_dir = folder / "Logs"

    processor = BatchProcessor(
        input_dir=folder,
        output_dir=output_dir,
        log_dir=log_dir,
    )
    processor.process_all()

    print(f"\nDone. Markdown files saved to: {output_dir}")
    print(f"Logs saved to: {log_dir}")


if __name__ == "__main__":
    main()
