from db.database import get_connection
from datetime import datetime   


class AnalyticsService:
    def record_page_visit(self, document_id, page_number):
        # Logic to record page visit in the database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO page_visits (document_id, page_number, timestamp)
            VALUES (?, ?, ?)
        ''', (document_id, page_number, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()

    def get_unique_page_viewed(self, document_id):
        # Logic to get unique pages viewed for a document
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(DISTINCT page_number) FROM page_visits
            WHERE document_id = ?
        ''', (document_id,))
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return result if result else 0

