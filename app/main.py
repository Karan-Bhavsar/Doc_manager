import streamlit as st
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

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
# Initialize the database
init_db()

service = DocumentService()
analytics = AnalyticsService()

st.title("📁 Smart PDF Document Manager")

st.divider()

tabs = st.tabs(["Upload", "Search & View", "Analytics"])

with tabs[0]:
    st.header("Upload PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    tags  = st.text_input("Enter tags (comma separated)")
    description = st.text_area("Enter a brief description of the document")
    lecture_date = st.date_input("Lecture Date(optional)", value=None)

    if st.button("Upload"):
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
                    st.session_state.current_page -= 1
                    st.rerun()
            with col3:
                if st.button("Next") and current_page < total_pages - 1:
                    st.session_state.current_page += 1
                    st.rerun()

            img_path  = os.path.join(image_dir, images[st.session_state.current_page])  
            st.image(img_path, use_column_width=True)  

            analytics.record_page_visit(doc.id, st.session_state.current_page)  # Record the page visit in analytics
            st.write(f"file: {doc.name}") 

        if st.button("Exit Reader Mode"):
            st.session_state.reader_mode = False
            
            st.rerun()  # Refresh the page to exit reader mode                 



            


with tabs[2]:
    # LOGIC FOR ANALYTICS ON PDF DOCUMENTS
    pass