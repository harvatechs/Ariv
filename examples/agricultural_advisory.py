#!/usr/bin/env python3
"""
Example: Agricultural Advisory System
Voice-to-voice farming advice in Hindi
"""

import sys
sys.path.insert(0, '..')

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from utils.voice import VoiceInterface, AgriculturalAdvisor
from config import get_model_paths
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("🌾 Maha-Kisan: Agricultural Advisory Demo")
    print("="*60)

    # Initialize system
    model_paths = get_model_paths()
    orchestrator = JugaadOrchestrator(model_paths)
    pipeline = TRVPipeline(orchestrator, {})

    # Initialize voice interface (Hindi)
    voice = VoiceInterface(language="hi")
    advisor = AgriculturalAdvisor(voice, pipeline)

    # Example text queries (in real use, these would be voice inputs)
    sample_queries = [
        "मेरी गेहूं की फसल में पीला रंग आ रहा है, क्या करूं?",
        "PM-KISAN योजना के लिए आवेदन कैसे करें?",
        "खरीफ सीजन में कौन सी फसल लगाएं?"
    ]

    for query in sample_queries:
        print(f"\n👨‍🌾 Farmer: {query}")

        # Process through pipeline
        result = pipeline.execute(
            query=query,
            language="hindi",
            enable_critic=True
        )

        print(f"🤖 Advisor: {result['final_answer'][:200]}...")
        print("-"*60)

if __name__ == "__main__":
    main()
