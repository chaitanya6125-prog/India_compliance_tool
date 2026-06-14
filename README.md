# India_compliance_tool
 specialized Automated Compliance &amp; Control Monitoring tool built exclusively for DSCI Frameworks and the DPDP Act 2023.

Prerequisites
Install the necessary libraries:

bash


pip install langchain langchain-community langchain-huggingface chromadb pypdf fastapi uvicorn python-multipart textwrap3
(Note: For the demo, we use HuggingFaceEmbeddings and a local LLM. In production, swap for OpenAI/Claude for better accuracy.)

📂 File Structure
/compliance_tool
  ├── main.py               # FastAPI backend
  ├── loader.py             # Data ingestion (DPDP/DSCI docs)
  ├── analyzer.py           # RAG Logic & Gap Analysis
  ├── prompts.py            # System prompts for legal accuracy
  ├── dpdp_act.pdf          # (You must download this)
  └── dsci_framework.pdf    # (You must download this)
