

from db.database import get_connection
from core.models import Document

class DocumentRepository:
    def add_document(self,doc: Document):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (name, path, thumbnail_path, total_pages, tags, description, lecture_date, upload_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (doc.name, doc.path, doc.thumbnail_path, doc.total_pages, doc.tags, doc.description, doc.lecture_date, doc.upload_date))
        conn.commit()
        conn.close()

    def search_documents(self, tag=None, date=None):
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM documents"
        conditions = []
        params = []
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")
        if date:
            conditions.append("lecture_date = ?")
            params.append(date)

        if conditions:
            query += " WHERE " + " OR ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [Document(*row[1:]) for row in rows]
    
    def get_all_documents(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents")
        rows = cursor.fetchall()
        conn.close()
        return [Document(*row[1:]) for row in rows]
