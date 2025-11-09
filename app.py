# Main Streamlit application code with custom css styling and the dashboard
# import section

import streamlit as st
import os 
import sys 
from datetime import datetime 
from typing import List , Dict , any


# adding a source directory path 

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from document_processor import DocumentProcessor 
from vector_store import VectorStore
from qa_system import QASystem
from citiation_system import CitationSystem


# Page config
st.stet_page_config(
    page_title ="Intelligent Document Q&A System "
    page_icon ="(To be updated)"
    layout="wide"
    intial_sidebar_state ="expanded"
)

# custom CSS style genrated from AI 
st.markdown("""
<style>
    .main-header{
            font-size: 2.5rem;
            font-weight: bold;
            color: $1f77b4;
            text-align: center;
            margin-bottom : 2rem;
            }
    .sub-header{
            font-size : 1.2rem;
            color : #666;
            text-align : center;
            margin-bottom : 2rem;
            }
    .upload-section{
            background-color : #f8f9fa;
            padding: 1.5rem;
            border-radius : 10px;
            margin-bottom : 2rem;
            }
    .qa-section{
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            }
    .answer_box{
            background-color: #f0f8ff;
            padding : 1rem;
            border-radius: 8px;
            border-left : 4px solid #1f77b4;
            margin: 1rem 0;
            }
    .stats-box {
            background-color : #f5f5f5;
            padding: 1rem;
            border-radius : 8px;
            margin : 1rem 0;
            }
    
    

</style>
""" , unsafe_allow_html = True
)

def initialize_session_state():
    """Initialize session state variable"""
    if 'document_processed' not in st.session_state:
        st.session_state.documents_processed = False
    if 'conversation_history'not in st.session_state :
        st.session_state.conversation_history = []
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore()
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = QASystem()
    if "citation_system" not in st.session_state:
        st.session_state.citation_system = CitationSystem()
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()

def display_header():
    """Display the main Header """
    st.markdown('<div class="main-header"> Inteligent Document Q&A System </div', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload Documents and ask questions to get contextual answers with source citations</div>',unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with system information and controls """
    st.sidebar.header("System Status")

    # API status 
    if st.session_state.qa_system.is_available():
        st.sidebar.success("✅ Mistral API Connected")
    else:
        st.sidebar.error("❌ Mistral API Not Available")

    # Vector Store Status 
    vector_stats = st.session_state.vector_store.get_stats()
    if vector_stats.get("status") == "initialized":
        st.sidebar.sucess(f"✅ Vector Store Ready ({vector_stats.get('num_documents', 0)} docs)")
    else :
        st.sidebar.warning("⚠️ Vector Store Not Initialized")

    st.sidebar.markdown("---")


    # settings 
    st.sidebar.header("Settings")

    # Number of sources to retrieve
    k_sources = st.sidebar.slider("Number of sources to retrieve", 1,10,5)
    st.session_state.k_sources = k_sources

    # chunk size for document processing 
    chunk_szie = st.sidebar.slider("Document chunk size ", 500, 2000, 1000, step=100)
    if chunk_size !=
    st.session_state.document_processor.chunk_size:
    st.session_state.document_processor = DocumentProcessor( chunk_size=chunk_size)

    st.sidebar.markdown("---")
    
    # clear conversation history 
    if st.sidebar.button("🗑️ Clear Conversation History"):
        st.session_state.conversation_history = []
        st.rerun()

    # Save / Load Vector store 
    st.sidebar.header("💾 Vector Store Management")

    col1, col2 = st.sidebar.columns(2)
    with col1 :
        if st.button("save index"):
            if st.session_state.vector_store.save_index():
                st.sidebar.success("Index saved !")

    with col2 :
        if st.session_state.vector_store.load_index():
            st.session_state.documents_processed = True
            st.sidebar.sucess("Index loaded")
            st.rerun()

def document_uplaod_section():
    """Handle document upload and processing """
    st.markdown('<div class="upload-section">' , unsafe_allow_html=True)
    st.header("📄 Document Upload")
    uploaded_files = st.file_uploaded(
        "Uploaded PDF documents",
        type=['pdf'],
        accept_multiple_files = True,
        help = "Upload one or more PDF documents to create a Knowledge base"
    )

    if uploaded_files:
        if st.button("🔄 Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                # Process documents
                documents = st.session_state.document_processor.process_documents(uploaded_files)

                if documents :
                    # Build vector index
                    if st.session_state.vector_store.build_index(documents):
                        st.session_state.documents_processed = True

                        # Display statistics
                        stats = st.session_state.document_processor.get_document_stats(documents)

                        col1, col2, col3 , col4 = st.columns(4)
                        with col1 :
                            st.metric("Douments", stats.get("num_sources", 0))
                        with col2 : 
                            st.metric("Chunks", stats.get("total_chunks", 0))
                        with col3 :
                            st.metric("Characters", f"{stats.get('total_characters', 0):,}")
                        with col4 :
                            st.metric("Avh Chunk Size", stats.get('average_chunk_size', 0))

                        st.success(f"Successfully processed {len(uploaded_files)} documents!")

                    else:
                        st.error("Failed to build vector index")
                else:
                    st.error("No documents were processed successfully")

    st.markdown('</div>', unsafe_allow_html = True)

def qa_section():
    """Handle question-answering interface"""
    st.markdown('<div class="qa-section">',unsafe_allow_html=True)
    st.header("❓ Ask Questions")


    if not st.session_state.documents_processed:
        st.warning("Please upload and process docuemnts first before asking questions.")
        





def main():
    """Main application function"""
    initialize_session_state()
    display_header()
    display_sidebar()

    # Main content 
    document_uplaod_section()
    qa_section()
    conversation_history_section()

    # Footer 
    st.markdown("---")
    st.markdown("<div style='text-align : center; color : #666; font-size: 0.9em>" 
                "Built with StreamLit , langchain , FAISS , and Mistral AI"
                f"Session ID : {st.sesssion_state.get('session_id', 'Unkown')}"
                "</div>"
                , unsafe_allow_html=True)


if __name__ == "__main__":
    main()


