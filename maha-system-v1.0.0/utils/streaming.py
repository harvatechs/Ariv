#!/usr/bin/env python3
"""
Streaming Response Handler for Maha-System
Provides real-time token-by-token output for better UX
"""

import logging
from typing import Iterator, Optional
from core.orchestrator import JugaadOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Streaming")

class StreamingPipeline:
    """
    Wraps the TRV pipeline to provide streaming responses
    Yields intermediate results as they're generated
    """

    def __init__(self, orchestrator: JugaadOrchestrator):
        self.orchestrator = orchestrator

    def stream_translate(self, query: str, language: str) -> Iterator[str]:
        """
        Stream translation tokens as they're generated
        Yields partial translations for real-time display
        """
        model = self.orchestrator.load_model("translator")

        prompt = f"Translate from {language} to English: {query}\nEnglish:"

        # Stream tokens
        stream = model(
            prompt,
            max_tokens=512,
            temperature=0.3,
            stream=True
        )

        translation = ""
        for output in stream:
            token = output['choices'][0]['text']
            translation += token
            yield token

        logger.info(f"Translation complete: {translation}")

    def stream_reasoning(self, english_prompt: str) -> Iterator[str]:
        """
        Stream reasoning tokens (Chain-of-Thought)
        Shows the model's thinking process in real-time
        """
        model = self.orchestrator.load_model("reasoner")

        system_prompt = "Solve step-by-step, showing your reasoning:\n\n"
        full_prompt = system_prompt + english_prompt + "\n\nSolution:"

        stream = model(
            full_prompt,
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )

        for output in stream:
            token = output['choices'][0]['text']
            yield token

    def stream_full_pipeline(self, query: str, language: str) -> Iterator[Dict]:
        """
        Stream the entire pipeline with phase updates
        Yields dicts with 'phase', 'status', 'content'

        Usage:
            for update in streamer.stream_full_pipeline("...", "hindi"):
                print(f"{update['phase']}: {update['content']}")
        """
        # Phase 1: Translation
        yield {"phase": "translation", "status": "started", "content": ""}

        translation = ""
        for token in self.stream_translate(query, language):
            translation += token
            yield {"phase": "translation", "status": "streaming", "content": token}

        yield {"phase": "translation", "status": "complete", "content": translation}

        # Phase 2: Reasoning
        yield {"phase": "reasoning", "status": "started", "content": ""}

        reasoning = ""
        for token in self.stream_reasoning(translation):
            reasoning += token
            yield {"phase": "reasoning", "status": "streaming", "content": token}

        yield {"phase": "reasoning", "status": "complete", "content": reasoning}

        # Phase 3: Synthesis (non-streaming for final polish)
        yield {"phase": "synthesis", "status": "started", "content": ""}

        # Load translator again for synthesis
        model = self.orchestrator.load_model("translator")
        synth_prompt = f"Transcreate to {language}: {reasoning}"
        result = model(synth_prompt, max_tokens=512, temperature=0.4)
        final = result['choices'][0]['text']

        yield {"phase": "synthesis", "status": "complete", "content": final}

# FastAPI Streaming Endpoint
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

def create_streaming_app(orchestrator):
    """Create FastAPI app with streaming endpoints"""
    streamer = StreamingPipeline(orchestrator)

    @app.get("/stream")
    async def stream_query(query: str, language: str = "hindi"):
        """
        SSE (Server-Sent Events) endpoint for real-time updates

        Client receives:
            event: translation
            data: {"status": "streaming", "content": "Hello"}

            event: reasoning
            data: {"status": "streaming", "content": "Let me think..."}
        """
        async def event_generator():
            for update in streamer.stream_full_pipeline(query, language):
                yield f"event: {update['phase']}\ndata: {json.dumps(update)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )

    return app

if __name__ == "__main__":
    print("Streaming demo - import and use with FastAPI")
    print("Example client JavaScript:")
    print("""
    const eventSource = new EventSource('/stream?query=...&language=hindi');
    eventSource.addEventListener('translation', (e) => {
        console.log('Translation:', JSON.parse(e.data));
    });
    eventSource.addEventListener('reasoning', (e) => {
        console.log('Reasoning:', JSON.parse(e.data));
    });
    """)
