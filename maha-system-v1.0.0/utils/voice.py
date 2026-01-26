#!/usr/bin/env python3
"""
Voice Interface for Maha-System
Enables voice-to-voice interaction for low-literacy users
Perfect for agricultural advisory and rural outreach
"""

import logging
from typing import Optional, Tuple
import tempfile
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VoiceInterface")

class VoiceInterface:
    """
    End-to-end voice pipeline:
    Speech -> Text (ASR) -> Maha-System -> Text -> Speech (TTS)

    Uses lightweight open-source models suitable for edge deployment
    """

    def __init__(self, 
                 asr_model: Optional[str] = None,
                 tts_model: Optional[str] = None,
                 language: str = "hi"):
        """
        Args:
            asr_model: Path to Whisper or similar ASR model
            tts_model: Path to Coqui TTS or similar model
            language: Language code (hi, ta, te, etc.)
        """
        self.language = language
        self.asr = None
        self.tts = None

        # Lazy loading - only initialize when needed
        self.asr_model_path = asr_model
        self.tts_model_path = tts_model

    def _load_asr(self):
        """Load Automatic Speech Recognition model"""
        if self.asr is None:
            try:
                import whisper
                logger.info("🎤 Loading ASR model...")
                self.asr = whisper.load_model("base")  # small for edge
            except ImportError:
                logger.error("Whisper not installed. Run: pip install openai-whisper")
                raise
        return self.asr

    def _load_tts(self):
        """Load Text-to-Speech model"""
        if self.tts is None:
            try:
                from TTS.api import TTS
                logger.info("🔊 Loading TTS model...")
                # Use Indic-specific TTS if available
                model_name = "tts_models/hi/clean/vits" if self.language == "hi" else "tts_models/en/ljspeech/vits"
                self.tts = TTS(model_name)
            except ImportError:
                logger.error("TTS not installed. Run: pip install TTS")
                raise
        return self.tts

    def speech_to_text(self, audio_path: str) -> str:
        """
        Convert speech to text

        Args:
            audio_path: Path to audio file (wav, mp3, etc.)

        Returns:
            Transcribed text in vernacular language
        """
        model = self._load_asr()

        logger.info(f"🎤 Transcribing: {audio_path}")
        result = model.transcribe(audio_path, language=self.language)

        text = result['text']
        logger.info(f"📝 Transcribed: {text}")
        return text

    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Convert text to speech

        Args:
            text: Text to speak (in vernacular language)
            output_path: Optional output path, else creates temp file

        Returns:
            Path to generated audio file
        """
        model = self._load_tts()

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")

        logger.info(f"🔊 Synthesizing speech: {text[:50]}...")
        model.tts_to_file(text=text, file_path=output_path)

        logger.info(f"🔊 Audio saved: {output_path}")
        return output_path

    def voice_query(self, 
                    audio_input_path: str, 
                    pipeline,  # TRVPipeline instance
                    audio_output_path: Optional[str] = None) -> Tuple[str, str]:
        """
        Complete voice-to-voice pipeline

        Args:
            audio_input_path: User's voice query
            pipeline: Initialized TRVPipeline
            audio_output_path: Optional output path

        Returns:
            (transcribed_text, answer_text, audio_output_path)
        """
        # 1. Speech to Text
        query_text = self.speech_to_text(audio_input_path)

        # 2. Process through Maha-System
        result = pipeline.execute(
            query=query_text,
            language=self.language,
            enable_critic=True
        )
        answer_text = result['final_answer']

        # 3. Text to Speech
        output_path = self.text_to_speech(answer_text, audio_output_path)

        return query_text, answer_text, output_path

class AgriculturalAdvisor:
    """
    Specialized wrapper for agricultural use case
    Pre-configured with farming-specific prompts
    """

    def __init__(self, voice_interface: VoiceInterface, pipeline):
        self.voice = voice_interface
        self.pipeline = pipeline

        # Farming-specific context
        self.system_context = """You are an agricultural expert advisor for Indian farmers. 
        Provide practical advice in simple language. Consider:
        - Local climate and soil conditions
        - Traditional farming practices (जैविक खेती)
        - Government schemes (PM-KISAN, Soil Health Card)
        - Pest management and crop diseases
        Answer concisely and actionably."""

    def advise(self, audio_query: str) -> dict:
        """
        Get farming advice from voice query

        Returns dict with:
        - transcription
        - advice_text
        - advice_audio_path
        - relevant_schemes (extracted by pipeline)
        """
        # Modify pipeline prompts temporarily for agricultural context
        original_prompts = self.pipeline.prompts.copy()
        self.pipeline.prompts['reasoning'] = self.system_context + "\n\n" + self.pipeline.prompts.get('reasoning', '')

        try:
            query_text, answer_text, audio_path = self.voice.voice_query(
                audio_query, 
                self.pipeline
            )

            return {
                "transcription": query_text,
                "advice_text": answer_text,
                "advice_audio": audio_path,
                "language": self.voice.language
            }
        finally:
            self.pipeline.prompts = original_prompts

# Gradio Demo Interface
def create_gradio_demo(pipeline):
    """Create web demo with voice interface"""
    try:
        import gradio as gr
    except ImportError:
        logger.error("Gradio not installed. Run: pip install gradio")
        return None

    voice = VoiceInterface(language="hi")
    advisor = AgriculturalAdvisor(voice, pipeline)

    def process_audio(audio_file):
        if audio_file is None:
            return "No audio provided", None

        result = advisor.advise(audio_file)
        return result['advice_text'], result['advice_audio']

    demo = gr.Interface(
        fn=process_audio,
        inputs=gr.Audio(source="microphone", type="filepath"),
        outputs=[
            gr.Textbox(label="Advice (Text)"),
            gr.Audio(label="Advice (Voice)")
        ],
        title="🌾 Maha-Kisan: AI Agricultural Advisor",
        description="Speak in Hindi to get farming advice"
    )

    return demo

if __name__ == "__main__":
    print("Voice Interface Module")
    print("Usage:")
    print("  from utils.voice import VoiceInterface")
    print("  voice = VoiceInterface(language='hi')")
    print("  text = voice.speech_to_text('query.wav')")
    print("  audio = voice.text_to_speech('answer')")
