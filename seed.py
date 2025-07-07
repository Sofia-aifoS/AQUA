from models import SessionLocal, Users, Chats, Messages
import uuid
from datetime import datetime
import bcrypt

def seed():
    session = SessionLocal()

    # Crea un utente di esempio con password hashata
    password_piana = "password"
    password_hashata = bcrypt.hashpw(password_piana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = Users(
        id=uuid.uuid4(),
        username="testuser",
        password=password_hashata,
        name="Mario",
        surname="Rossi",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(user)
    session.commit()

    # Crea una chat di esempio
    chat = Chats(
        id=uuid.uuid4(),
        user_id=user.id,
        name="Prima chat",
        order=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(chat)
    session.commit()

    # Crea un messaggio di esempio
    msg = Messages(
        id=uuid.uuid4(),
        user_id=user.id,
        chat_id=chat.id,
        message="Ciao, questo è un messaggio di test.",
        role="user",
        order=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(msg)
    session.commit()

    session.close()
    print("Database popolato con dati di esempio.")

if __name__ == "__main__":
    seed()
