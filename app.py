import gradio as gr
import os
from dotenv import load_dotenv
import openai
import tempfile
from pathlib import Path

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def trascrivi(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcription = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

    print('User: ', transcription.text)
    return transcription.text
'''
def genera_risposta(messaggi):
    response = openai.chat.completions.create( # da cambiare in completions.create
        model=os.getenv("MODEL_ID"),
        messages=messaggi,
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    print("Assistente: ", response.choices[0].message.content)
    return response.choices[0].message.content
    '''
def genera_risposta(conversazione_history):
    response = openai.responses.create(
        model=os.getenv("MODEL_ID"),
        prompt={
            "id": "pmpt_685ad2253a5881949ede64fb6e3e831a0f2bc6aa6e47beb1",
            "version": "6"
        },
        input=conversazione_history,
        reasoning={},
        max_output_tokens=2048,
        store=True
    )

    print("Assistente: ", response.output[0].content[0].text)
    return response.output[0].content[0].text


def sintetizza_tts(testo):
    # Create a temporary file for the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_path = temp_file.name

    # Use the streaming response to generate the audio file
    with openai.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="shimmer",
            input=testo,
            instructions="Adotta un tono vivace e interrogativo, come chi vuole davvero capire, ma non accetta risposte vaghe. Incalza con curiosità, mantenendo sempre un rispetto profondo."
    ) as response:
        response.stream_to_file(temp_path)

    return temp_path
'''
# Stato iniziale con il messaggio di sistema
messaggi = [
    {
        "role": "system",
        "content": "Sei un tutor socratico esperto della laguna di Venezia. Guida l'utente attraverso domande per esplorare e comprendere i dati della laguna."
    }
]


def conversazione(audio):
    testo_utente = trascrivi(audio)
    messaggi.append({"role": "user", "content": testo_utente})
    risposta = genera_risposta(messaggi)
    messaggi.append({"role": "assistant", "content": risposta})
    audio_risposta = sintetizza_tts(risposta)
    return testo_utente, risposta, audio_risposta
'''

# Conversation history for the playground prompt
conversazione_history = []


def conversazione(audio):
    testo_utente = trascrivi(audio)

    # Add user message to conversation history
    conversazione_history.append({"role": "user", "content": testo_utente})

    # Generate response using playground prompt
    risposta = genera_risposta(conversazione_history)

    # Add assistant response to conversation history
    conversazione_history.append({"role": "assistant", "content": risposta})

    audio_risposta = sintetizza_tts(risposta)
    return testo_utente, risposta, audio_risposta


with gr.Blocks() as demo:
    gr.Markdown("## Parla con AQUA")
    with gr.Row():
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Parla qui")
        audio_output = gr.Audio(label="Risposta Audio", autoplay=True)
    with gr.Row():
        testo_input_utente = gr.Textbox(label="Hai detto:")
        testo_output_AQUA = gr.Textbox(label="AQUA: ")
    audio_input.stop_recording(conversazione, inputs=audio_input, outputs=[testo_input_utente, testo_output_AQUA, audio_output])

demo.launch()



# lavorare su intefaccia < simile a chatgpt vocale
