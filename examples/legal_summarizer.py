#!/usr/bin/env python3
"""
Example: Legal Document Processing
Summarizes court documents in vernacular languages
"""

import sys
sys.path.insert(0, '..')

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths

def summarize_legal_document(document_text: str, language: str = "hindi"):
    """
    Summarize a legal document with key points in simple language

    Args:
        document_text: Raw legal text
        language: Target language for summary
    """

    # Specialized prompt for legal domain
    legal_prompt = f"""You are a legal assistant helping common people understand court documents.
    Summarize the following legal text in simple {language}.

    Requirements:
    1. Identify: Case type, parties involved, key dates
    2. Explain: Main legal issue in plain language
    3. Action items: What does the reader need to do?
    4. Rights: What are the person's rights in this matter?

    Legal Text:
    {document_text[:2000]}  # Truncate for demo

    Provide structured summary:"""

    model_paths = get_model_paths()
    orchestrator = JugaadOrchestrator(model_paths)
    pipeline = TRVPipeline(orchestrator, {
        'reasoning': legal_prompt
    })

    result = pipeline.execute(
        query=document_text[:500],  # First 500 chars as query
        language=language,
        enable_critic=True
    )

    return result['final_answer']

# Demo with sample legal text
sample_legal_text = """
IN THE COURT OF DISTRICT JUDGE, DELHI
Case No. 123/2024

Between:
Ram Prasad (Plaintiff)
AND  
State of Delhi (Defendant)

ORDER

This case pertains to land acquisition under the Land Acquisition Act, 1894. 
The plaintiff challenges the compensation amount awarded for his agricultural 
land measuring 2.5 acres situated in Village Badarpur, Delhi.

The Collector had awarded Rs. 50 lakhs per acre. The plaintiff contends that 
the market value is Rs. 1.5 crore per acre based on recent sales deeds.

Court hereby orders:
1. Matter referred to District Valuation Officer for fresh assessment
2. Status quo maintained regarding possession
3. Next hearing on 15th March 2024
"""

if __name__ == "__main__":
    print("⚖️ Legal Document Summarizer")
    print("="*60)

    summary = summarize_legal_document(sample_legal_text, "hindi")
    print(f"\n📄 Summary:\n{summary}")
