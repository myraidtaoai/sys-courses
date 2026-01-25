# Copy the functions from your original llm_utilities.py
import wave
from google.genai import types

# Gemini Client
# Transcribe audio to text
def transcribe_audio(gemini_client, audio_path, mime_type='audio/wav', show_debug=False):
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    
    prompt = 'Generate a transcript of the speech.'
    response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        prompt,
                        types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=mime_type,
                        )
                    ],
                    config=types.GenerateContentConfig(
                        max_output_tokens=1000,
                        temperature=0,
                        system_instruction="You are a helpful AI Assitant. Your job is transform the content of audio into text.",
                    )
                    
                    )
    return response.text

def generate_tts_with_gemini(client, text):
    """
    Generate speech audio from text using Gemini TTS model.
    
    Parameters:
    - client: The Gemini client
    - text: The text to convert to speech
    
    Returns:
    - Audio response from Gemini
    """
    response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=text,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                # voice_name='Kore',
                voice_name='Aoede',
                )
            )
        ),
    )
    )
    return response.candidates[0].content.parts[0].inline_data.data

def save_audio_file(pcm, file_path, channels=1, rate=24000, sample_width=2):
    """
    Save audio data to a file.
    Parameters:
    - pcm: The audio data in PCM format
    - file_path: The path to save the audio file
    - channels: Number of audio channels
    - rate: Sample rate
    - sample_width: Sample width in bytes
    """
    if pcm:
        if not file_path.endswith(('.mp3', '.wav', '.ogg')):
            print("Invalid file extension. Please use .mp3, .wav, or .ogg.")
            return None
        try:
            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(rate)
                wf.writeframes(pcm)
            print(f"Audio saved to {file_path}")
        except Exception as e:
            print(f"Error saving audio file: {str(e)}")

# def synthesize_speech(polly_client, text, voice_id="Ruth", engine="neural", output_format="mp3", text_type="text"):
#     """
#     Synthesize speech using Amazon Polly and return the audio stream.
    
#     Parameters:
#     - text: The text to convert to speech
#     - voice_id: The voice to use (e.g., 'Joanna', 'Matthew')
#     - engine: The engine to use ('standard', 'neural', or 'long-form')
#     - output_format: The output format ('mp3', 'ogg_vorbis', or 'pcm')
#     - text_type: The type of input text ('text' or 'ssml')
    
#     Returns:
#     - Audio stream
#     """
#     try:
#         response = polly_client.synthesize_speech(
#             Text=text,
#             VoiceId=voice_id,
#             Engine=engine,
#             OutputFormat=output_format,
#             TextType=text_type
#         )
#         return response['AudioStream'].read()
#     except Exception as e:
#         print(f"Error synthesizing speech: {str(e)}")
#         return None
