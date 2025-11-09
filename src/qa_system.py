import os
from typing import List, Dict, Any, Tuple
from mistralai import Mistral
from langchain_core.documents import Document
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class QASystem:
    """Handles question-answering using Mistral API with document context."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.client = None
        self.model_name = "mistral-large-latest"
        
        if self.api_key:
            try:
                self.client = Mistral(api_key=self.api_key)
                st.success("Mistral API client initialized successfully")
            except Exception as e:
                st.error(f"Error initializing Mistral client: {str(e)}")
        else:
            st.error("Mistral API key not found. Please set MISTRAL_API_KEY environment variable.")
    
    def create_context_prompt(self, question: str, relevant_docs: List[Tuple[Document, float]]) -> str:
        """Create a prompt with context from relevant documents."""
        if not relevant_docs:
            return f"Question: {question}\n\nPlease answer based on your general knowledge."
        
        # Build context from relevant documents
        context_parts = []
        for i, (doc, score) in enumerate(relevant_docs):
            source = doc.metadata.get("source", "Unknown")
            chunk_id = doc.metadata.get("chunk_id", i)
            context_parts.append(f"[Source {i+1}: {source}, Chunk {chunk_id}, Relevance: {score:.3f}]\n{doc.page_content}\n")
        
        context = "\n".join(context_parts)
        
        prompt = f"""You are an intelligent document Q&A assistant. Answer the question based on the provided context from the documents. 

Context from relevant documents:
{context}

Question: {question}

Instructions:
1. Answer the question based primarily on the provided context
2. If the context doesn't contain enough information, clearly state this
3. Cite specific sources when making claims (e.g., "According to Source 1...")
4. Be concise but comprehensive
5. If multiple sources provide different information, acknowledge this

Answer:"""
        
        return prompt
    
    def generate_answer(self, question: str, relevant_docs: List[Tuple[Document, float]]) -> Dict[str, Any]:
        """Generate an answer using Mistral API with document context."""
        if not self.client:
            return {
                "answer": "Error: Mistral API client not initialized",
                "sources": [],
                "error": "API client not available"
            }
        
        try:
            # Create prompt with context
            prompt = self.create_context_prompt(question, relevant_docs)
            
            # Generate response using Mistral API
            response = self.client.chat.complete(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for more focused answers
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Extract source information
            sources = []
            for i, (doc, score) in enumerate(relevant_docs):
                sources.append({
                    "source_id": i + 1,
                    "filename": doc.metadata.get("source", "Unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", i),
                    "relevance_score": score,
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "model_used": self.model_name,
                "num_sources": len(sources)
            }
            
        except Exception as e:
            st.error(f"Error generating answer: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def answer_question(self, question: str, vector_store, k: int = 5) -> Dict[str, Any]:
        """Complete Q&A pipeline: search for relevant docs and generate answer."""
        if not question.strip():
            return {
                "answer": "Please provide a question.",
                "sources": [],
                "error": "Empty question"
            }
        
        # Search for relevant documents
        relevant_docs = vector_store.similarity_search(question, k=k)
        
        if not relevant_docs:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": [],
                "error": "No relevant documents found"
            }
        
        # Generate answer with context
        result = self.generate_answer(question, relevant_docs)
        
        return result
    
    def get_conversation_summary(self, conversation_history: List[Dict]) -> str:
        """Generate a summary of the conversation history."""
        if not self.client or not conversation_history:
            return ""
        
        try:
            # Create summary prompt
            history_text = "\n".join([
                f"Q: {item['question']}\nA: {item['answer'][:200]}..."
                for item in conversation_history[-5:]  # Last 5 exchanges
            ])
            
            prompt = f"""Summarize the following conversation between a user and a document Q&A system:

{history_text}

Provide a brief summary of the main topics discussed and key information provided."""
            
            response = self.client.chat.complete(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error generating conversation summary: {str(e)}")
            return ""
    
    def is_available(self) -> bool:
        """Check if the QA system is properly initialized."""
        return self.client is not None
