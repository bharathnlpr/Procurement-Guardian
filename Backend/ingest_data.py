import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 1. SETUP CHROMADB (Local storage)
# This creates a folder named 'procurement_db' to store the vectors
chroma_client = chromadb.PersistentClient(path="./procurement_db")
collection = chroma_client.get_or_create_collection(name="policy_documents")

def ingest_pdfs(folder_path):
    """
    Processes all PDF documents in a directory and stores them in a vector database.

    The ingestion pipeline follows these steps:
    1. Parsing: Iterates through the specified folder and extracts text from each PDF page.
    2. Chunking: Uses RecursiveCharacterTextSplitter to break long texts into 2000-character 
       segments with a 200-character overlap to preserve context between chunks.
    3. Embedding: Converts each text chunk into a high-dimensional vector using 
       the 'gemini-embedding-001' model.
    4. Storage: Persists the embeddings, raw text, and source metadata into 
       a local ChromaDB collection for future retrieval.

    Args:
        folder_path (str): The relative or absolute path to the directory containing 
                           the policy PDF files.

    Returns:
        None: The results are persisted directly to the local 'procurement_db' directory.
    """
    # 2. CHUNKING LOGIC (500 words ≈ 2000 characters)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=200
    )

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            print(f"📄 Processing {file}...")
            reader = PdfReader(os.path.join(folder_path, file))
            
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()

            # Split into chunks
            chunks = text_splitter.split_text(full_text)
            
            # 3. EMBEDDING & STORAGE
            for i, chunk in enumerate(chunks):
                # Generate embedding using Gemini
                result = client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=chunk
                )
                embedding = result.embeddings[0].values
                
                # Add to ChromaDB
                collection.add(
                    ids=[f"{file}_{i}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source": file}]
                )

if __name__ == "__main__":
    ingest_pdfs("../Data")
    print("✅ Vector Database Created Successfully!")