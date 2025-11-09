import streamlit as st
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from document_processor import DocumentProcessor
from vector_store import VectorStore
from qa_system import QASystem
from citation_system import CitationSystem

# Page configuration
st.set_page_config(
    page_title="Intelligent Document Q&A System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .qa-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .answer-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .stats-box {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'documents_processed' not in st.session_state:
        st.session_state.documents_processed = False
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore()
    if 'citation_system' not in st.session_state:
        st.session_state.citation_system = CitationSystem()
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()
    if 'mistral_api_key' not in st.session_state:
        st.session_state.mistral_api_key = "GtJJSeLN4KB2ZSHRiFW4mPwjeIIOUfG2"
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = QASystem(api_key=st.session_state.mistral_api_key)

def display_header():
    """Display the main header."""
    st.markdown('<div class="main-header">📚 Intelligent Document Q&A System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload documents and ask questions to get contextual answers with source citations</div>', unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with system information and controls."""
    # API Key Configuration
    st.sidebar.header("🔑 API Configuration")
    
    new_api_key = st.sidebar.text_input(
        "Mistral API Key",
        value=st.session_state.mistral_api_key,
        type="password",
        help="Enter your Mistral API key. Default key is provided for testing."
    )
    
    if new_api_key != st.session_state.mistral_api_key:
        st.session_state.mistral_api_key = new_api_key
        st.session_state.qa_system = QASystem(api_key=new_api_key)
        st.rerun()
    
    st.sidebar.markdown("---")
    
    st.sidebar.header("🔧 System Status")
    
    # API Status
    if st.session_state.qa_system.is_available():
        st.sidebar.success("✅ Mistral API Connected")
    else:
        st.sidebar.error("❌ Mistral API Not Available")
    
    # Vector Store Status
    vector_stats = st.session_state.vector_store.get_stats()
    if vector_stats.get("status") == "initialized":
        st.sidebar.success(f"✅ Vector Store Ready ({vector_stats.get('num_documents', 0)} docs)")
    else:
        st.sidebar.warning("⚠️ Vector Store Not Initialized")
    
    st.sidebar.markdown("---")
    
    # Settings
    st.sidebar.header("⚙️ Settings")
    
    # Number of sources to retrieve
    k_sources = st.sidebar.slider("Number of sources to retrieve", 1, 10, 5)
    st.session_state.k_sources = k_sources
    
    # Chunk size for document processing
    chunk_size = st.sidebar.slider("Document chunk size", 500, 2000, 1000, step=100)
    if chunk_size != st.session_state.document_processor.chunk_size:
        st.session_state.document_processor = DocumentProcessor(chunk_size=chunk_size)
    
    st.sidebar.markdown("---")
    
    # Clear conversation history
    if st.sidebar.button("🗑️ Clear Conversation History"):
        st.session_state.conversation_history = []
        st.rerun()
    
    # Save/Load Vector Store
    st.sidebar.header("💾 Vector Store Management")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Save Index"):
            if st.session_state.vector_store.save_index():
                st.sidebar.success("Index saved!")
    
    with col2:
        if st.button("Load Index"):
            if st.session_state.vector_store.load_index():
                st.session_state.documents_processed = True
                st.sidebar.success("Index loaded!")
                st.rerun()

def document_upload_section():
    """Handle document upload and processing."""
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.header("📄 Document Upload")
    
    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF documents to create a knowledge base"
    )
    
    if uploaded_files:
        if st.button("🔄 Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                # Process documents
                documents = st.session_state.document_processor.process_documents(uploaded_files)
                
                if documents:
                    # Build vector index
                    if st.session_state.vector_store.build_index(documents):
                        st.session_state.documents_processed = True
                        
                        # Display statistics
                        stats = st.session_state.document_processor.get_document_stats(documents)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Documents", stats.get('num_sources', 0))
                        with col2:
                            st.metric("Chunks", stats.get('total_chunks', 0))
                        with col3:
                            st.metric("Characters", f"{stats.get('total_characters', 0):,}")
                        with col4:
                            st.metric("Avg Chunk Size", stats.get('average_chunk_size', 0))
                        
                        st.success(f"Successfully processed {len(uploaded_files)} documents!")
                    else:
                        st.error("Failed to build vector index")
                else:
                    st.error("No documents were processed successfully")
    
    st.markdown('</div>', unsafe_allow_html=True)

def qa_section():
    """Handle question-answering interface."""
    st.markdown('<div class="qa-section">', unsafe_allow_html=True)
    st.header("❓ Ask Questions")
    
    if not st.session_state.documents_processed:
        st.warning("Please upload and process documents first before asking questions.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        placeholder="What would you like to know about the uploaded documents?",
        help="Ask any question about the content in your uploaded documents"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_button = st.button("🔍 Ask Question", type="primary", disabled=not question.strip())
    with col2:
        if st.session_state.conversation_history:
            if st.button("📊 Show Summary"):
                summary = st.session_state.qa_system.get_conversation_summary(st.session_state.conversation_history)
                if summary:
                    st.info(f"**Conversation Summary:** {summary}")
    
    if ask_button and question.strip():
        with st.spinner("Searching documents and generating answer..."):
            # Get answer
            result = st.session_state.qa_system.answer_question(
                question, 
                st.session_state.vector_store, 
                k=st.session_state.get('k_sources', 5)
            )
            
            if 'error' not in result:
                # Display answer
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown("### 💡 Answer")
                
                # Format answer with citations
                formatted_answer = st.session_state.citation_system.create_citation_links(
                    result['answer'], 
                    result['sources']
                )
                st.markdown(formatted_answer, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display sources
                if result['sources']:
                    st.markdown("### 📚 Sources")
                    sources_html = st.session_state.citation_system.format_sources(
                        result['sources'], 
                        question
                    )
                    st.markdown(sources_html, unsafe_allow_html=True)
                    
                    # Display source statistics
                    source_stats = st.session_state.citation_system.get_source_statistics(result['sources'])
                    if source_stats:
                        st.markdown('<div class="stats-box">', unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Sources Used", source_stats.get('total_sources', 0))
                        with col2:
                            st.metric("Unique Files", source_stats.get('unique_files', 0))
                        with col3:
                            st.metric("Avg Relevance", f"{source_stats.get('average_relevance', 0):.3f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'question': question,
                    'answer': result['answer'],
                    'sources': result['sources']
                })
                
                # Download report option
                report = st.session_state.citation_system.create_downloadable_report(
                    question, result['answer'], result['sources']
                )
                st.download_button(
                    label="📥 Download Report",
                    data=report,
                    file_name=f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
            else:
                st.error(f"Error: {result.get('error', 'Unknown error occurred')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def conversation_history_section():
    """Display conversation history."""
    if st.session_state.conversation_history:
        st.header("💬 Conversation History")
        
        for i, item in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
            with st.expander(f"Q{len(st.session_state.conversation_history)-i}: {item['question'][:50]}..."):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")
                st.markdown(f"**Sources:** {len(item.get('sources', []))} documents")
                st.markdown(f"**Time:** {item['timestamp']}")

def main():
    """Main application function."""
    initialize_session_state()
    display_header()
    display_sidebar()
    
    # Main content
    document_upload_section()
    qa_section()
    conversation_history_section()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        "Built with Streamlit, LangChain, FAISS, and Mistral AI | "
        f"Session ID: {st.session_state.get('session_id', 'Unknown')}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
