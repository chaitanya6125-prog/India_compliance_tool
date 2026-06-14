from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceEndpoint # Or use OpenAI/Anthropic
from langchain.prompts import PromptTemplate
import json
import os
from loader import vector_store
from prompts import ANALYSIS_PROMPT

# Use a free local model for demo, or swap for API key
# For production, use: os.getenv("OPENAI_API_KEY")
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct", 
    huggingfacehub_api_token=os.getenv("HF_TOKEN") # Set this env var
)

def analyze_policy_compliance(user_policy_text):
    """
    Takes user policy text, retrieves relevant laws, and generates gap analysis.
    """
    # 1. Retrieve relevant legal context
    retriever = vector_store.as_retriever(search_kwargs={"k": 10})
    
    # 2. Create the chain
    prompt_template = PromptTemplate(
        input_variables=["context", "policy"], 
        template=ANALYSIS_PROMPT
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )
    
    # 3. Execute analysis
    response = qa_chain.invoke({"context": "", "policy": user_policy_text})
    result_text = response["result"]
    
    # 4. Clean and Parse JSON (LLMs sometimes add markdown)
    try:
        # Remove markdown code blocks if present
        clean_json = result_text.replace("```json", "").replace("```", "")
        gaps = json.loads(clean_json)
        return gaps
    except json.JSONDecodeError:
        return [{"error": "Failed to parse AI response. Please try again.", "raw_output": result_text}]

def generate_fixed_policy(user_policy_text, gaps):
    """
    Generates a revised policy incorporating the fixes.
    """
    fix_prompt = f"""
    You are a legal expert. Rewrite the following policy to fix these specific gaps:
    
    GAPS:
    {json.dumps(gaps, indent=2)}
    
    ORIGINAL POLICY:
    {user_policy_text}
    
    OUTPUT: Return ONLY the revised, full policy text. Ensure it includes the new clauses.
    """
    
    # Reuse the LLM for generation
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    
    prompt = PromptTemplate(input_variables=["gaps", "policy"], template=fix_prompt)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain.run(gaps=gaps, policy=user_policy_text)
