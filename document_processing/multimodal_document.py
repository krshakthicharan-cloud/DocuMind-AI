class MultimodalDocument:

    def __init__(self):

        self.pages = []
        self.tables = []
        self.images = []
        self.ocr_pages = []
        self.chunks = []

    def add_pages(self, pages):

        self.pages = pages

    def add_tables(self, tables):

        self.tables = tables

    def add_images(self, images):

        self.images = images

    def add_ocr(self, ocr_pages):

        self.ocr_pages = ocr_pages

    def add_chunks(self, chunks):

        self.chunks = chunks

    def summary(self):

        return {
            "pages": len(self.pages),
            "tables": len(self.tables),
            "images": len(self.images),
            "ocr_pages": len(self.ocr_pages),
            "chunks": len(self.chunks)
        }