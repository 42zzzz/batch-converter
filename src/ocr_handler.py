import logging

logger = logging.getLogger(__name__)


class OcrHandler:
    def __init__(self, language="eng"):
        self.language = language
        raise NotImplementedError("OCR support is not yet implemented")

    def extract_text_from_images(self, pdf_path):
        raise NotImplementedError("OCR support is not yet implemented")
