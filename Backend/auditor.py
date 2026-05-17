import os
import time
import json
import chromadb # <--- New Import
from google import genai
from dotenv import load_dotenv
from state_schema import ProcurementState 

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# --- RAG HELPER FUNCTION ---
def get_relevant_policy(query_text):
    """
    Retrieves the most relevant policy text from the ChromaDB vector store.

    Args:
        query_text (str): The search query (e.g., item name and cost).

    Returns:
        str: A combined string of the top matching policy documents.
    """
    # 1. Get the absolute path to the Backend directory
    # This works regardless of which folder you run the script from
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(backend_dir, "procurement_db")
    
    # 2. Connect using the full absolute path
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_collection(name="policy_documents")
    
    # 1. Turn the query into a vector (Use the same model as ingest_data.py)
    query_embed = client.models.embed_content(
        model="models/gemini-embedding-001", 
        contents=query_text
    ).embeddings[0].values
    
    # 2. Search for the top 2 most relevant policy chunks
    results = collection.query(
        query_embeddings=[query_embed],
        n_results=4
    )
    
    # Return the combined text of the found policies
    return "\n".join(results['documents'][0])

def auditor_node(state: ProcurementState):
    """
    Agent node that checks procurement requests against retrieved PDF policies.

    Args:
        state (ProcurementState): The current graph state containing extracted data.

    Returns:
        dict: Updated state with audit_status and audit_reason.
    """

    print("---🔍 Auditor Node (RAG-Enabled)---")
    time.sleep(2) 

    extracted = state.get('extracted_data', {})
    item = extracted.get('item_name', 'unknown item')
    origin = extracted.get('origin', 'unknown origin')
    total_cost = state.get('total_base_cost', 0) # Get the number we calculated

    # 1. THE RAG STEP: Fetch actual rules from your PDFs
    search_query = f"What are the procurement policies for {item} costing {total_cost} KWD and origin also {origin}?"
    actual_policies = get_relevant_policy(search_query)

    # 2. SYSTEM INSTRUCTION: Strict JSON enforcement
    auditor_instruction = f"""
    OBJECTIVE: You are the PDF policy checker. 
    Compare the User Request against the REFERENCE POLICIES provided.
    
    REFERENCE POLICIES:
    {actual_policies}
    
    CRITICAL RULES:
    1. If the request breaks a rule (e.g., wrong brand, exceeds KWD limit without quotes), status is "VIOLATES".
    2. Provide a detailed explanation in the 'reason' field citing the specific policy.
    3. Return ONLY valid JSON.
    """

    # 3. LLM CALL with JSON Schema
    prompt = f"User Request: {extracted}. Total Cost: {total_cost}. Does this comply?"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        config={
            "system_instruction": auditor_instruction,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["OK", "VIOLATES"]},
                    "reason": {"type": "string"}
                },
                "required": ["status", "reason"]
            }
        },
        contents=prompt
    )

    # 4. Parse the JSON and update the State
    audit_data = json.loads(response.text)
    
    return {
        "audit_status": audit_data['status'],
        "audit_reason": audit_data['reason'], # This carries the "Lenovo" and "3500 KWD" details
        "internal_reasoning": [f"Auditor: Policy check complete. Result: {audit_data['status']}"]
    }
