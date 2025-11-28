import edge_tts
import asyncio
import os

async def text_to_speech_async(text, output_file="question_audio.mp3"):
    try:
        voice = "en-US-AriaNeural"
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return output_file
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None

def text_to_speech(text, output_file="question_audio.mp3"):
    return asyncio.run(text_to_speech_async(text, output_file))

def get_available_voices():
    async def get_voices():
        voices = await edge_tts.list_voices()
        return [v["Name"] for v in voices if "en-US" in v["Name"]]
    
    return asyncio.run(get_voices())
