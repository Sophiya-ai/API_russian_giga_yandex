import os #подключаем работу с .env
import uuid #добавляем генерацию уникального ID запроса (rq_uid)
import requests #подключаем библиотеку requests;
import httpx
import urllib3 # В коде отключается проверка SSL. Это сделано для упрощения работы. В реальных проектах лучше использовать официальные сертификаты.
from dotenv import load_dotenv #Загрузка переменных
from openai import OpenAI

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

if not GIGACHAT_AUTH_KEY:
    raise ValueError("Не найден GIGACHAT_AUTH_KEY в .env")

SYSTEM_PROMPT = """
## Роль
Ты — опытный организатор досуга с чутьём на то, что действительно понравится конкретному человеку.

## Контекст
Твоя задача — предложить 3 варианта вечера, каждый из которых будет привлекательным и реалистичным для конкретного человека.

## Задача
1. Учти интересы и используй web_search.

2. Предложи ровно **3 варианта вечера**. Каждый вариант должен иметь:
   - **Короткое цепляющее название**
   - **Конкретное описание** того, чем заняться (не абстрактное «посмотри фильм», а что именно и почему это подойдёт), 
   куда конкретно сходить - названия кафе/ресторанов, парков и других мест, которые реально существуют. 
   Не придумывай названия. Добавь url сайта рекомендуемого места. Используй реальные url.
   - **Связь с ответами пользователя** — вариант должен учитывать его интересы, а не быть шаблонным советом

3. **Варианты должны отличаться по характеру** — например, один активный, один спокойный, один неожиданный или нестандартный.

## Формат
Пиши живо как совет другу.
"""

"""
В коде есть отдельный блок, который:
- Отправляет запрос на сервер авторизации.
- Передаёт: ключ, уникальный ID запроса (rq_uid).
- Получает access token.
В коде есть отдельный блок, который:

Этот блок — ключевой, потому что именно он обновляет токен; без него запросы к модели не работают.
"""

# Отправка запроса к модели
def get_access_token() -> str:
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
    }
    data = {"scope": GIGACHAT_SCOPE}

    response = requests.post(
        url,
        headers=headers,
        data=data,
        timeout=30,
        verify=False,  # только для локальной разработки
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_recommendations(user_description: str) -> str:
    access_token = get_access_token()

# Создаётся клиент для работы с GigaChat
    client = OpenAI(
        api_key=access_token,
        base_url="https://gigachat.devices.sberbank.ru/api/v1",
        http_client=httpx.Client(verify=False),  # только для локальной разработки
    )

# Формируется запрос: role: system → правила; role: user → описание человека.
# Устанавливаются параметры: температура = 0.8 (более креативные ответы)
    completion = client.chat.completions.create(
        model="GigaChat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Рекомендации согласно интересам: {user_description}"
            },
        ],
        temperature=0.2,
    )

    return completion.choices[0].message.content

if __name__ == "__main__":
    person_description = "Хочу отдохнуть в Нестерове (Калининградская область), люблю прогулки и вкусную еду"
    print(get_recommendations(person_description))