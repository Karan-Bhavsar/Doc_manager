import pymupdf
import os
class PDFReader:
    def convert_pdf_to_images(self, pdf_path):
         # PyMuPDF
        doc = pymupdf.open(pdf_path)
        folder_name = os.path.basename(pdf_path).replace('.pdf', '')
        output_dir = os.path.join("storage", "pdfs", folder_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        image_paths = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            matrix = pymupdf.Matrix(2, 2)  # Scale factor for better resolution
            pix = page.get_pixmap(matrix=matrix)
            image_path = os.path.join(output_dir, f"page_{i+1}.png")
            pix.save(image_path)
            image_paths.append(image_path)

        doc.close()    
        return image_paths
