# Fast Vector store 
import os 
import pickle
from typing import List, Tuple , Optional 
import faiss 
import numpy as np 
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
import streamlit as st




class VectorStore : 
    """Manage FAISS vector store for document embeddings and similarity search """

    def __init__(self, embedding_model_name : str = "all-MiniLM-L6-v2"):
        self.embedding_model_name = embedding_model_name 
        self.embeddings = None
        self.index = None
        self.documents = []
        self.vector_store_path = "vector_store"

        # initialize embedding model 
        self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Initialize the embedding model"""

        try: 
            self.embeddings = SentenceTransformer(
            self.embedding_model_name
            )
            st.sucess(f"Loaded embedding model : {self.embedding_model_name}")
        except Exception as e : 
            st.error(f"Error loading embedding model : {str(e)}")
            self.embeddings = None
    
    def create_embeddings(self , texts: List[str]) -> np.ndarray:
        """Creating embeddings for a list of texts"""
        if self.embeddings is None : 
            raise ValueError("Embedding Model is not initialized")
        
        try : 
            embeddings = self.embeddings.encode(texts, show_progress_bar=True)
            return np.array(embeddings).astype('float32') 
        except Exception as e : 
            st.error(f"Error creating embeddings : {str(e)}")
            return np.array([])
        

    
    def build_index(self, documents: List[Document]) -> bool:
        """Build FAISS index from documents"""
        if not documents:
            st.warning("No documents provided for indexing")
            return False
        
        try: 
            # Extract text content
            texts = [doc.page_content for doc in documents]

            # Create embeddings 
            with st.spinner("Creating embeddings...."):
                embeddings = self.create_embeddings(texts)

            if embeddings.size == 0:
                return False
            
            # Build FAISS Index 
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFaltIP(dimension) # Inned product for cosine similarity

            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)

            # store documents 
            self.documents = documents
            
            st.success(f"Built FAISS index with {len(documents)} documents")
            return True
        
        except Exception as e:
            st.error(f"Error building FAISS index : {str(e)}")
            return False
        


    def similarity_search(self , query: str , k: int = 5 ) -> List[Tuple[Document, float]] :
        """Perform similairty search and return top k documents with top scores"""

        if self.index is None or not self.documents:
            st.warning("Vector store not initialized, Please upload and process the documents first")
            return []
        
        try:
            # Create query embedding
            query_embedding = self.create_embeddings([query])
            if query_embedding.size == 0:
                return []
            
            # Normalize query embedding 
            faiss.normalize_L2(query_embedding)

            # search 
            scores, indices = self.index.search(query_embedding, k)

            # Return documents with scores 
            results = []
            for i , (score , idx) in enumerate(zip(score[0], indices[0])):
                if idx < len(self.documents):
                    results.append((self.documents[idx], float(score)))

            return results 
        
         except Exception as e:
             st.error(f"Error during similarity search : {str(e)}")
             return []
        
    
    def save_index (self, , path : Optional[str] =  None) -> bool:
        """Save the FAISS index and docuements to disk.."""

        if self.index is None: 
            st.warning("No index to save")
            return False 
        
        try:
            save_path = path or self.vector_store_path 
            os.makedirs(save_path , exist_ok = True)

            # Save FAISS index 
            faiss.write_index(self.index, os.path.join(save_path , "faiss_index.bin"))

            # save documents and metadata 
            with open(os.path.join(save_path m "documents.pkl"), "wb") as f:
                pickle.dump(self.documents, f)
            
            # save configaration
            config ={
                "embedding_model_name":
                self.embedding_model_name, 
                "num_documents" : len(self.documents)
            }
            with open(os.path.join(save_path , "config.pkl"), "wb") as f:
                pickle.dump(config, f)

            
            st.sucess(f"Vector store saved to {save_path}")
            return True
        
        except Exception as e:
            st.error(f"Error saving vector store : {str(e)}")
            return False
        
    
    def load_index(self , path: Optional[str] = None) -> bool:
        """Load the FAISS index and documents from disk"""
        try: 
            load_path = path or self.vector_store_path

            if not os.path.exists(load_path):
                st.info("No saved vector store found")
                return False
        
            # Load FAISS index 
            index_path = os.path.join(load_path, "faiss_index.bin")
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path) 
            else:
                st.warning("FAISS index file not found")
                return False
            
            # Load Documents 
            docs_path = os.path.join(load_path, "documents.pkl")
            if os.path.exists(docs_path):
                with open(docs_path):
                    with open(docs_path, "rb") as f:
                        self.documents = pickle.load(f)
            else :
                st.warning("Documents file not found")
                return False
            
            # Load configuaration
            config_path = os.path.join(load_path , "config.pkl")
            if os.path.exists(config_path):
                with open(config_path, "rb") as f:
                    config = pickle.load(f)
                    if config.get("embedding_model_name") !=  self.embedding_model_name:
                        st.warning("Loaded index uses different embedding Model")

            st.sucess(f"Vector store loaded from {load_path}")
            return True

        except Exception as e:
            st.error(f"Error loading vector store : {str(e)}")
            return False
        
    
    def get_stats(self) -> dict:
        """Get stat about the vector store """
    if self.index is None:
        return {"Status" : "not_initialized"}
    

    return {
        "Status" : "Initialized",
        "num_documents" : len(self.documents),
        "index_size" : self.index.ntotal,
        "embedding_model" : self.embeddding_model_name,
        "dimension" : self.index.d if hasattr(self.index, 'd')  else None
    }


        