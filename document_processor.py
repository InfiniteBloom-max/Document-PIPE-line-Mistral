# PDF Processing Module
# import section

import os 
import tempfile 
from typing import List , Dict , Any
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import streamlit as st

class DocumentProcessor :
    """Handles document upload , text extraction and chunking """

    def __init__(self, chunk_size : int = 1000, chunk_overlap : int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            length_function=len,
            seperators =['\n\n', '\n', ' ', '']
        )

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from the uploaded PDF file"""
        try : 
            # create a tempporary file to save the uplaoded content
            with tempfile.NamedTemporaryFile(delete = False, suffix='.df') as tmp_file:
                tmp_file.write(pdf_file.read())
                tmp_file_path = tmp_file.name
            
            # Extract text from PDF
            reader = PdfReader(tmp_file_path)
            text = "" 
            for page in reader.pages:
                text += page.extract_text() + "\n"

            # clean up temporary file 
            os.unlink(tmp_file_path)


            return text 
        except Exception as e :
            st.error(f"Error extracting text from PDF :{str(e)}")
            return ""
        
    def process_documents(self , uploaded_files) -> List[Document]:
        """Process Uploaded documents and return chunked documents"""
        documents = []

        for uplaoded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                # Extract text from pdf 
                text = self.extract_text_from_pdf(uploaded_file) 

                if text : 
                    # Create document with metadata
                    doc = Document(
                        page_content = text,
                        metadata ={
                            "source" : uploaded_file.name,
                            "file_type" : "pdf",
                            "file_size" : len(text)
                        }
                    )
                    documents.append(doc)
            else : 
                st.warning(f"Unsupported file type: {uploaded_file.type}")
        
        # Split documents into chunks 
        if documents: 
            chunked_docs = self.text_splitter.split_documents(documents)


            # Add chunk information to metadata
            for i, chunk in enumerate(chunked_docs):
                chunk.metadata["chunk_id"] = i
                chunk.metadata["chunk_size"] = len(chunk.page_content)

            return chunked_docs
        
        return []
    


    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any] :
        """Get statistis about processed documents """
        if not documents: 
            return {}
        

        total_chunks = len(documents)
        total_chars = sum(len(doc.page_content) for doc in documents)
        sources = list (set(doc.metadata.get("source", "Unknown") for doc in documents))


        return {
            "total_chunks" : total_chunks,
            "total_characters" : total_chars,
            "average_chunk_size" : total_chars // total_chunks if total_chunks > 0 else 0,
            "sources" : sources,
            "num_sources" : len(soruces)
        }