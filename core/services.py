#uploaded doc
from datetime import datetime
from pydoc import doc
from core.models import Document
from core.file_manager import FileManager
from core.thumbnail import ThumbnailGenerator
from core.reader import PDFReader
from db.repository import DocumentRepository
import os


class DocumentService:
    def __init__(self):
        self.repo = DocumentRepository()
        self.file_manager = FileManager()
        self.thumbnail_generator = ThumbnailGenerator()
        self.reader = PDFReader()

    def upload_document(self, uploaded_file, tags, description, lecture_date):
        # Save file
        # append timestamp to filename
        
        filepath = self.file_manager.save_file(uploaded_file)
        thumbnail_path = self.thumbnail_generator.generate_thumbnail(filepath)
        total_pages = self.thumbnail_generator.get_total_pages(filepath)
        # generate thumbnail
        # get total pages
        # convert to images
        self.reader.convert_pdf_to_images(filepath)
        # create required variables : upload date

        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # save to db

        doc = Document(
            name=os.path.basename(filepath),
            path=filepath,
            thumbnail_path=thumbnail_path,
            tags=tags,
            description=description,
            upload_date=upload_date,
            lecture_date=lecture_date,
            total_pages=total_pages
        )

        self.repo.add_document(doc)

    def search_documents(self, tag=None, date=None):
        return self.repo.search_documents(tag, date)
    
    def get_all_documents(self):
        return self.repo.get_all_documents()