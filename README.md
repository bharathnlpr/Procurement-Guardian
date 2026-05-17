# 🛡️ Procurement Guardian AI

A professional multi-agent system built with **LangGraph** and **Gemini** to intelligently audit procurement requests against internal PDF policies.

## 🚀 Overview
This system uses an agentic workflow to:
* **Extract** procurement details from natural language.
* **Audit** requests against local policy documents using RAG (ChromaDB).
* **Calculate** final costs including automated import duties.
* **Verify** quality through an automated inspector agent.

## 🛠️ Tech Stack
* **Language:** Python
* **Orchestration:** LangGraph
* **LLM:** Google Gemini 2.5 Flash
* **Vector DB:** ChromaDB
* **UI:** Streamlit

## ⚙️ Setup
1. Clone the repository.
2. Create a `.env` file in the root directory.
3. Add your Gemini API key: `GOOGLE_API_KEY=your_key_here`
4. Install requirements and run: `streamlit run Frontend/app.py`

## 📂 Data Setup
1. Create a folder named `Data` in the root directory.
2. Place your procurement policy PDFs inside this folder.
3. Run `python Backend/ingest_data.py` to initialize the vector database.


**The frontend is a lightweight Streamlit implementation designed solely for demonstration purposes; the core innovation of this project lies in the LangGraph-based multi-agent orchestration within the backend.**
