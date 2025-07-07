import gradio as gr
import os
from dotenv import load_dotenv
import openai
import tempfile
from pathlib import Path
from models import SessionLocal, Messages, Users
from datetime import datetime
import bcrypt

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def check_login(username, password):
    session = SessionLocal()
    user = session.query(Users).filter_by(username=username).first()
    session.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return True
    return False

def login_fn(username, password):
    if check_login(username, password):
        return gr.update(visible=False), gr.update(visible=True), ""
    else:
        return gr.update(visible=True), gr.update(visible=False), "Credenziali errate."

def trascrivi(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcription = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )
    print('User: ', transcription.text)
    return transcription.text

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
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_path = temp_file.name
    with openai.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="shimmer",
            input=testo,
            instructions="Adotta un tono vivace e interrogativo, come chi vuole davvero capire, ma non accetta risposte vaghe. Incalza con curiosità, mantenendo sempre un rispetto profondo."
    ) as response:
        response.stream_to_file(temp_path)
    return temp_path

conversazione_history = []

def conversazione(audio):
    testo_utente = trascrivi(audio)
    conversazione_history.append({"role": "user", "content": testo_utente})
    risposta = genera_risposta(conversazione_history)
    conversazione_history.append({"role": "assistant", "content": risposta})
    audio_risposta = sintetizza_tts(risposta)
    session = SessionLocal()
    user_id = 1
    chat_id = 1
    for idx, msg in enumerate(conversazione_history):
        exists = session.query(Messages).filter_by(user_id=user_id, chat_id=chat_id, order=idx).first()
        if not exists:
            session.add(Messages(
                user_id=user_id,
                chat_id=chat_id,
                message=msg["content"],
                role=msg["role"],
                order=idx,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ))
    session.commit()
    session.close()
    return testo_utente, risposta, audio_risposta

with gr.Blocks() as demo:
    login_box = gr.Column(visible=True)
    chat_box = gr.Column(visible=False)
    with login_box:
        gr.Markdown("## Login AQUA")
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login")
        login_error = gr.Textbox(label="Errore login", visible=True)
        login_btn.click(login_fn, inputs=[username, password], outputs=[login_box, chat_box, login_error])
    with chat_box:
        gr.Markdown("## Parla con AQUA")
        with gr.Row():
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Parla qui")
            audio_output = gr.Audio(label="Risposta Audio", autoplay=True)
        with gr.Row():
            testo_input_utente = gr.Textbox(label="Hai detto:")
            testo_output_AQUA = gr.Textbox(label="AQUA: ")
        audio_input.stop_recording(conversazione, inputs=audio_input, outputs=[testo_input_utente, testo_output_AQUA, audio_output])

demo.launch()
