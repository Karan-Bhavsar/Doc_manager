import streamlit as st
import os
import sys
from dotenv import load_dotenv



BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

from core.services import DocumentService

from core.analytics import AnalyticsService

st.set_page_config(page_title="DocManager", layout="centered")

from db.database import init_db
if "current_page" not in st.session_state:
    st.session_state.current_page = 0

if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "reader_mode" not in st.session_state:
    st.session_state.reader_mode = False
if "show_reset" not in st.session_state:
    st.session_state.show_reset = False

# Initialize the database
init_db()

service = DocumentService()
analytics = AnalyticsService()

st.title("📁 Smart PDF Document Manager")

st.divider()

st.subheader("Admin Controls")
if st.button("Clean Data"):
    st.session_state.show_reset = True

if st.session_state.show_reset:
    password_input = st.text_input("Enter admin password to confirm data reset", type="password")  

    if st.button("Confirm Reset"):
        if password_input == ADMIN_PASSWORD:
            import shutil
            # Clear the database
            if os.path.exists("db/documents.db"):
                os.remove("db/documents.db")
            # Clear the storage directory
            pdf_dir = os.path.join("storage", "pdfs")
            thumbnail_dir = os.path.join("storage", "thumbnails")
            if os.path.exists(pdf_dir):
                shutil.rmtree(pdf_dir, ignore_errors=True)
            if os.path.exists(thumbnail_dir):
                shutil.rmtree(thumbnail_dir, ignore_errors=True)

            os.makedirs(pdf_dir, exist_ok=True)
            os.makedirs(thumbnail_dir, exist_ok=True)

            st.success("All data has been reset successfully.")
            st.rerun()
        else:
            st.error("Incorrect password. Data reset aborted.")        



tabs = st.tabs(["Upload", "Search & View", "Analytics"])

with tabs[0]:
    st.header("Upload PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    tags  = st.text_input("Enter tags (comma separated)")
    description = st.text_area("Enter a brief description of the document")
    lecture_date = st.date_input("Lecture Date(optional)", value=None)

    if st.button("Upload"):
        analytics.record_app_visit("upload clicked")
        if uploaded_file:
            service.upload_document(uploaded_file, tags, description, lecture_date)
        else:
            st.error("Please select a PDF file to upload.")
with tabs[1]:
    st.header("Search & View Documents")
    col1, col2 = st.columns(2)
    with col1:
        search_tag = st.text_input("Search by Tag")
    with col2:
        search_date = st.date_input("Search by Lecture Date", value=None)
    
    if st.button("Search"):
        analytics.record_app_visit("search clicked")
        st.session_state.search_results = service.search_documents(tag=search_tag if search_tag else None, date=(search_date) if search_date else None)

    # Now display the search results
    results = st.session_state.search_results
    if results and not st.session_state.reader_mode:
        st.subheader(f"Results ({len(results)} found")
        container = st.container(height=500)

        with container:
            for doc in results:
                col1, col2 = st.columns([1, 3])
                with col1:
                    if doc.thumbnail_path:
                        st.image(doc.thumbnail_path, width=100)
                with col2: 
                    st.write(f"**{doc.name}**")
                    st.write(f"**Tags:** {doc.tags}")   
                    st.write(f"**Description:** {doc.description}")
                    st.write(f"**Lecture Date:** {doc.lecture_date}")  

                    if st.button("Open", key=f"open_{doc.name}"):
                        analytics.record_app_visit("open clicked")
                        # Logic to open the PDF document
                        st.session_state.selected_doc = doc
                      # This works on Windows. For cross-platform, consider using subprocess.
                        st.session_state.current_page = 0
                        st.session_state.reader_mode = True
                        st.rerun()  # Refresh the page to switch to reader mode
    if st.session_state.reader_mode and st.session_state.selected_doc:
        st.write("### PDF Reader Mode")

        doc  = st.session_state.selected_doc
        st.subheader(f" Reading: {doc.name}")

        folder_name = os.path.basename(doc.path).replace(".pdf", "")
        image_dir = f"storage/pdfs/{folder_name}"

        st.write("Image dir:", image_dir)
        st.write("Files:", os.listdir(image_dir) if os.path.exists(image_dir) else "Directory not found")

        if not os.path.exists(image_dir):
            st.error("PDF images not found. Please ensure the PDF was processed correctly.")
        else:
            images = sorted([f for f in os.listdir(image_dir) if f.endswith(".png")])
            total_pages = len(images)
            current_page = st.session_state.current_page

            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("Previous") and current_page > 0:
                    analytics.record_app_visit("previous page")
                    st.session_state.current_page -= 1
                    st.rerun()
            with col3:
                if st.button("Next") and current_page < total_pages - 1:
                    analytics.record_app_visit("next page")
                    st.session_state.current_page += 1
                    st.rerun()

            img_path  = os.path.join(image_dir, images[st.session_state.current_page])  
            st.image(img_path, use_column_width=True)  

            analytics.record_page_visit(doc.name, st.session_state.current_page)  # Record the page visit in analytics
            unique_pages = analytics.get_unique_page_viewed(doc.name)
            progress = (unique_pages / doc.total_pages) * 100 if doc.total_pages > 0 else 0
            
            st.progress(progress/100)
            st.write(f"Progress: {unique_pages}/{doc.total_pages} unique pages viewed ({progress:.2f}%)")
             

        if st.button("Exit Reader Mode"):
            analytics.record_app_visit("exit reader mode")
            st.session_state.reader_mode = False
            
            st.rerun()  # Refresh the page to exit reader mode                 



            


with tabs[2]:
    # LOGIC FOR ANALYTICS ON PDF DOCUMENTS
    st.header("Analytics Dashboard")
    
    if st.button("Reset Analytics Data"):
        analytics.reset_analytics()
        st.success("Analytics data has been reset.")
    
    st.subheader("App Usage")

    app_data = analytics.get_app_visits()

    import pandas as pd
    df = pd.DataFrame(app_data, columns=["Event Type", "Count"])

    if df.empty:
        st.write("No app usage data available.")
    else:
        st.bar_chart(df.set_index("Event Type"))

    st.subheader("Document Progress")  

    docs = service.get_all_documents()

    data = []  
    for doc in docs:
        unique_pages = analytics.get_unique_page_viewed(doc.name)
        progress = (unique_pages / doc.total_pages) * 100 if doc.total_pages else 0
        
        data.append({
            "Document": doc.name,
            "Unique Pages Viewed": unique_pages,
            "Total Pages": doc.total_pages,
            "Progress (%)": progress
        })

    df_docs = pd.DataFrame(data)  
    st.dataframe(df_docs)      
