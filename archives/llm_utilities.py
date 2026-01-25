from google.genai import types
from google import genai

# Gemini Client
# Transcribe audio to text
# Added a mime_type argument, as the original code saved to .wav but specified audio/mp3..
def transcribe_audio(gemini_client, audio_path, mime_type='audio/wav',show_debug=False):
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    
    prompt = 'Generate a transcript of the speech.'
    response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
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

# AI Assistant
def respond_to_text(gemini_client, user_query):
    if not user_query:
        return "I didn't receive a query. How can I help you today?"
    
    prompt = f'You are a helpful assistant. Answer the user\'s question as **Briefly** as you can: {user_query}'
    response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[
                        prompt
                    ]
                    )
    return response.text

# Groq Client
# Respond to user query with audio output
async def output_audio(groq_client, text, output_audio_path):
    model = "playai-tts"
    voice = "Arista-PlayAI"
    response_format = "wav"

    response = groq_client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )

    response.write_to_file(output_audio_path)
    return response

def synthesize_speech(polly_client,text, voice_id="Ruth", engine="neural", output_format="mp3", text_type="text"):
    """
    Synthesize speech using Amazon Polly and return the audio stream.
    
    Parameters:
    - text: The text to convert to speech
    - voice_id: The voice to use (e.g., 'Joanna', 'Matthew')
    - engine: The engine to use ('standard', 'neural', or 'long-form')
    - output_format: The output format ('mp3', 'ogg_vorbis', or 'pcm')
    - text_type: The type of input text ('text' or 'ssml')
    
    Returns:
    - Audio stream
    """
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            Engine=engine,
            OutputFormat=output_format,
            TextType=text_type
        )
        return response['AudioStream'].read()
    except Exception as e:
        print(f"Error synthesizing speech: {str(e)}")
        return None

def save_audio_file(audio_data, file_path):
    """
    Save audio data to a file.
    
    Parameters:
    - audio_data: The audio data to save
    - filename: The name of the file to save to
    """
    if audio_data:
        if not file_path.endswith(('.mp3', '.wav', '.ogg')):
            print("Invalid file extension. Please use .mp3, .wav, or .ogg.")
            return None
        try:
            with open(file_path, 'wb') as file:
                file.write(audio_data)
            print(f"Audio saved to {file_path}")
        except Exception as e:
            print(f"Error saving audio file: {str(e)}")