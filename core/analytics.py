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
        conn.close()
        return result if result else 0

    def record_app_visit(self, event_type):
        # Logic to record app visit in the database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO app_visits (event_type, timestamp)
            VALUES (?, ?)
        ''', (event_type, datetime.now()))
        conn.commit()
        conn.close()

    def get_app_visits(self):
        # Logic to get app visits from the database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT event_type, COUNT(*) FROM app_visits
            GROUP BY event_type
        ''')
        data = cursor.fetchall()
        conn.close()
        return data
    
    def reset_analytics(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM page_visits")
        cursor.execute("DELETE FROM app_visits")
        conn.commit()
        conn.close()    