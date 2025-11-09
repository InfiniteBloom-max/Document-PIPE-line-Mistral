# Intelligent Document Pipleine System

A powerful document question-answering system build with Streamlit , Langchain , FAISS ,and Mistral API that allows users to upload PDF documents and ask contextual questions with source citations 


# Features 
### Core Features 
- **Pdf Document Upload** -- Source for multiple PDF document Uplaods 
- **Intelligent Pipeline** -- Ask questions and get contextual answers for your documents 
- **Source Citations** -- Automatic citation with highlighted relevant text
- **Vector search** -- FAISS used here for similairty search for relevant document chunks 
- **Conversation History** -- The history is been saved to track the sessions accordingly 

## Optional Features (included)
- **Text Hightlighting** -- Keywords from questions are highlighted in source text
- **Relevance Scoring** -- See how relevant each source is to your  questions
- **Downloadable reports** -- Export Q&A sessions as markdown reports
- **Vector Store Persistence** -- Save and load document indexes 
- **Conversation summaries** -- AI-generated summaries of converastion history 



# Tech Stack 

- Frontend : Streamlit
- LLM : Mistral AI API
- Vecotr Database : False
- Document processing : Langchain , PyPDF2
- Embeddings : sentence transformers (all-MiniLM-L6-v2)
- Language : Python 3.8+

# Installation 

1. Clone the repository : 

use 
```
git clone <repository-url>
cd intelligent-document-qa
```

2. Install dependencies :

```
pip install -r requirements.txt
```

3. Set up environment variables :

```
cp .env.example .env
# Edit .env to add a Mistral API key
```

4. Run the application :
```
streamlit run app.py --server.port 12000 --server.address 0.0.0.0
```

# Usage 

1. Upload Documents
- Click on the "Document Upload" section 
- Upload one or more PDF files
- click "process Documents" to create the vector index

2. Ask Questions
- Enter your a question in the text input 
- click "Ask  Question" to get an AI generated answer
- view sources with highlighted relevant text

3. Managing the session 
- use the sidebar to adjust settings 
-save/load the vector indexes for persistence
- clear conversation history when needed



# Configuration 

-- Environment Variables
- `MISTRAL_API_KEY` : you Mistral AI API key (needed)

### Adjustable settings 

- Number of sources : How many relevant documents to retrieve (1 to 10)

- Chunk size : Size of document chunks for processing ( 500 to 2000 characters)

# API Integration

The system uses Mistral's freely avaliable api key and Mistral-large-latest model for generating answers 
