import re
from typing import List, Dict, Any, Tuple
import streamlit as st
from langchain_core.documents import Document


class CitationSystem:
    """Handles source citation and text highlighting for Q&A responses."""
    
    def __init__(self):
        self.highlight_color = "#ffeb3b"  # Yellow highlight
        self.citation_color = "#2196f3"  # Blue for citations
    
    def extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from the question for highlighting."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'was', 'were',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'can', 'could',
            'should', 'would', 'will', 'shall', 'may', 'might', 'must', 'do', 'does',
            'did', 'have', 'has', 'had', 'be', 'been', 'being'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', question.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def highlight_text(self, text: str, keywords: List[str]) -> str:
        """Highlight keywords in text using HTML."""
        if not keywords:
            return text
        
        highlighted_text = text
        
        # Sort keywords by length (longest first) to avoid partial matches
        sorted_keywords = sorted(keywords, key=len, reverse=True)
        
        for keyword in sorted_keywords:
            # Case-insensitive highlighting
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_text = pattern.sub(
                f'<mark style="background-color: {self.highlight_color}; padding: 2px 4px; border-radius: 3px;">{keyword}</mark>',
                highlighted_text
            )
        
        return highlighted_text
    
    def format_sources(self, sources: List[Dict[str, Any]], question: str = "") -> str:
        """Format sources with citations and highlighting."""
        if not sources:
            return "No sources found."
        
        keywords = self.extract_keywords(question) if question else []
        formatted_sources = []
        
        for source in sources:
            source_id = source.get("source_id", "Unknown")
            filename = source.get("filename", "Unknown")
            chunk_id = source.get("chunk_id", "Unknown")
            relevance_score = source.get("relevance_score", 0.0)
            content = source.get("content", "")
            
            # Highlight keywords in content
            highlighted_content = self.highlight_text(content, keywords)
            
            # Format source citation
            citation_header = f"""
            <div style="border-left: 4px solid {self.citation_color}; padding-left: 12px; margin: 10px 0;">
                <h4 style="color: {self.citation_color}; margin: 0;">
                    📄 Source {source_id}: {filename}
                </h4>
                <p style="margin: 5px 0; font-size: 0.9em; color: #666;">
                    Chunk {chunk_id} | Relevance: {relevance_score:.3f}
                </p>
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 8px;">
                    {highlighted_content}
                </div>
            </div>
            """
            
            formatted_sources.append(citation_header)
        
        return "\n".join(formatted_sources)
    
    def create_citation_links(self, answer: str, sources: List[Dict[str, Any]]) -> str:
        """Add clickable citation links to the answer."""
        if not sources:
            return answer
        
        # Look for source references in the answer (e.g., "Source 1", "according to source 2")
        citation_pattern = r'\b[Ss]ource\s+(\d+)\b'
        
        def replace_citation(match):
            source_num = int(match.group(1))
            return f'<a href="#source-{source_num}" style="color: {self.citation_color}; text-decoration: none; font-weight: bold;">[Source {source_num}]</a>'
        
        cited_answer = re.sub(citation_pattern, replace_citation, answer)
        
        return cited_answer
    
    def display_sources_sidebar(self, sources: List[Dict[str, Any]], question: str = ""):
        """Display sources in Streamlit sidebar."""
        if not sources:
            st.sidebar.info("No sources available")
            return
        
        st.sidebar.header("📚 Sources")
        
        keywords = self.extract_keywords(question) if question else []
        
        for source in sources:
            source_id = source.get("source_id", "Unknown")
            filename = source.get("filename", "Unknown")
            chunk_id = source.get("chunk_id", "Unknown")
            relevance_score = source.get("relevance_score", 0.0)
            content = source.get("content", "")
            
            with st.sidebar.expander(f"Source {source_id}: {filename}", expanded=False):
                st.write(f"**Chunk:** {chunk_id}")
                st.write(f"**Relevance:** {relevance_score:.3f}")
                
                # Display content with highlighting (Streamlit doesn't support HTML in sidebar)
                if keywords:
                    st.write("**Content:**")
                    # Simple text highlighting for sidebar
                    display_content = content
                    for keyword in keywords:
                        display_content = re.sub(
                            f'({re.escape(keyword)})',
                            r'**\1**',
                            display_content,
                            flags=re.IGNORECASE
                        )
                    st.write(display_content)
                else:
                    st.write(f"**Content:** {content}")
    
    def create_downloadable_report(self, question: str, answer: str, sources: List[Dict[str, Any]]) -> str:
        """Create a downloadable report with question, answer, and sources."""
        report_lines = [
            "# Document Q&A Report",
            f"**Generated on:** {st.session_state.get('timestamp', 'Unknown')}",
            "",
            "## Question",
            question,
            "",
            "## Answer",
            answer,
            "",
            "## Sources"
        ]
        
        if sources:
            for source in sources:
                source_id = source.get("source_id", "Unknown")
                filename = source.get("filename", "Unknown")
                chunk_id = source.get("chunk_id", "Unknown")
                relevance_score = source.get("relevance_score", 0.0)
                content = source.get("content", "")
                
                report_lines.extend([
                    f"### Source {source_id}: {filename}",
                    f"- **Chunk:** {chunk_id}",
                    f"- **Relevance Score:** {relevance_score:.3f}",
                    f"- **Content:** {content}",
                    ""
                ])
        else:
            report_lines.append("No sources available.")
        
        return "\n".join(report_lines)
    
    def get_source_statistics(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the sources used."""
        if not sources:
            return {}
        
        filenames = [source.get("filename", "Unknown") for source in sources]
        unique_files = list(set(filenames))
        
        avg_relevance = sum(source.get("relevance_score", 0.0) for source in sources) / len(sources)
        max_relevance = max(source.get("relevance_score", 0.0) for source in sources)
        min_relevance = min(source.get("relevance_score", 0.0) for source in sources)
        
        return {
            "total_sources": len(sources),
            "unique_files": len(unique_files),
            "files_used": unique_files,
            "average_relevance": avg_relevance,
            "max_relevance": max_relevance,
            "min_relevance": min_relevance
        }
