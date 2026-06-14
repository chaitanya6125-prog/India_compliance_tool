from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

# Path to your PDFs
DPDP_PATH = "dpdp_act_2023.pdf"
DSCI_PATH = "dsci_privacy_framework.pdf"
DB_PATH = "./legal_kb"

def load_and_index_documents():
    """
    Loads DPDP Act and DSCI Framework, chunks them, and stores in Vector DB.
    """
    if not os.path.exists(DB_PATH):
        print("🔄 Indexing Legal Documents...")
        documents = []
        
        # Load DPDP Act
        if os.path.exists(DPDP_PATH):
            loader_dpdp = PyPDFLoader(DPDP_PATH)
            documents.extend(loader_dpdp.load())
        
        # Load DSCI Framework
        if os.path.exists(DSCI_PATH):
            loader_dsci = PyPDFLoader(DSCI_PATH)
            documents.extend(loader_dsci.load())
        
        # Split into chunks for better retrieval
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50, 
            separators=["\n\n", "\n", " ", ""]
        )
        splits = text_splitter.split_documents(documents)
        
        # Create Embeddings (Free, local model)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Store in ChromaDB
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings, 
            persist_directory=DB_PATH
        )
        print("✅ Legal Knowledge Base Indexed.")
        return vectorstore
    else:
        print("📚 Loading existing Legal Knowledge Base...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

# Initialize once at startup
vector_store = load_and_index_documents()
