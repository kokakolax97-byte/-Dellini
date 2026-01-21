import streamlit as st
import json
import os
from dotenv import load_dotenv
from google import genai

# 1. Налаштування сторінки
st.set_page_config(page_title="Dellini 2.0 | Night Wolves", page_icon="🐺")

# 2. Завантаження ключа API
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Ініціалізація клієнта Gemini
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("Помилка: GOOGLE_API_KEY не знайдено у файлі .env")

# 3. Функція для роботи з базою знань
def load_kb():
    try:
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def get_custom_answer(query, kb):
    query = query.lower().strip()
    for key in kb:
        if key in query:
            return kb[key]
    return None

kb = load_kb()

# 4. Інтерфейс чату
st.title("🐺 Dellini: Night Wolves AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Відображення історії повідомлень
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле вводу
if prompt := st.chat_input("Напиши повідомлення..."):
    # Додаємо повідомлення користувача в історію
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Спочатку перевіряємо локальну базу знань
        custom_response = get_custom_answer(prompt, kb)
        
        if custom_response:
            response_text = custom_response
        else:
            # Якщо в базі немає — запитуємо у Gemini
            try:
                sys_instr = "Ти Dellini, створений Night Wolves. Творець — Fyn8zrox2. Допомагай команді чітко і стильно."
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=f"{sys_instr}\nКористувач: {prompt}"
                )
                response_text = response.text
            except Exception as e:
                response_text = "Вибачте, сталася помилка з'єднання з ШІ. Перевірте API ключ."
        
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})