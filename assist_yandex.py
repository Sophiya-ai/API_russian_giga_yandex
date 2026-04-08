import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

YANDEX_FOLDER_ID=os.getenv('YANDEX_FOLDER_ID')
YANDEX_API_KEY=os.getenv('YANDEX_API_KEY')

if not YANDEX_API_KEY:
    raise ValueError("Не найден YANDEX_API_KEY в .env")

if not YANDEX_FOLDER_ID:
    raise ValueError("Не найден YANDEX_FOLDER_ID в .env")

MODEL_URI = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite/latest"

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
   куда конкретно сходить - названия кафе/ресторанов, парков и других мест, которые реально существуют. Не придумывай названия.
   - **Связь с ответами пользователя** — вариант должен учитывать его интересы, а не быть шаблонным советом

3. **Варианты должны отличаться по характеру** — например, один активный, один спокойный, один неожиданный или нестандартный.

## Формат
Пиши живо как совет другу.
"""

client = OpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=YANDEX_FOLDER_ID,
)

def research(query: str) -> str:
    response = client.responses.create(
        model=MODEL_URI,
        instructions=SYSTEM_PROMPT,
        input=query,
        tools=[
            {
                "type": "web_search"
            }
        ],
        temperature=0.2,
        max_output_tokens=1800,
    )

    text_parts = []

    if hasattr(response, "output") and response.output:
        for item in response.output:
            if hasattr(item, "content") and item.content:
                for content_item in item.content:
                    text = getattr(content_item, "text", None)
                    if text:
                        text_parts.append(text)

    return "\n".join(text_parts).strip()


if __name__ == "__main__":
    user_query = "Хочу отдохнуть в Нестерове (Калининградская область), люблю прогулки и вкусную еду"
    result = research(user_query)
    print(result)

# client = openai.OpenAI(
#     api_key=YANDEX_API_KEY,
#     project=YANDEX_FOLDER_ID,
#     base_url="https://ai.api.cloud.yandex.net/v1"
# )
#
# response = client.responses.create(
#     model=f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_MODEL}",
#     input="Придумай 3 необычные идеи для стартапа в сфере путешествий.",
#     temperature=0.8,
#     max_output_tokens=1500
# )
#
# print(response.output[0].content[0].text)