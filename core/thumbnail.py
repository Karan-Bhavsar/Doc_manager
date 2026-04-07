import os
import pymupdf

THUMBNAIL_DIR = os.path.join("storage", 'thumbnails')

class ThumbnailGenerator:
    def generate_thumbnail(self, pdf_path):
        doc = pymupdf.open(pdf_path)
        page = doc.load_page(0)  # Load the first page
        pix = page.get_pixmap()  # Render page to an image
        base_name = os.path.basename(pdf_path).replace('.pdf', '.png')
        thumb_path = os.path.join(THUMBNAIL_DIR, base_name)

        pix.save(thumb_path)  # Save the thumbnail
        doc.close()
        return thumb_path
    
    def get_total_pages(self, pdf_path):
        doc = pymupdf.open(pdf_path)
        total = len(doc)
        doc.close()
        return total