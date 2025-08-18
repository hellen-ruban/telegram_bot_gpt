from openai import AsyncOpenAI
from src.settings.config import OPENAI_API_KEY

_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def ask_short(prompt: str) -> str:
    """
    Коротка відповідь українською (2–4 речення).
    Відмовостійка: у разі помилки повертає дружнє повідомлення.
    """
    try:
        resp = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Відповідай українською стисло, 2–4 речення, дружнім тоном."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            # max_tokens задаємо за бажанням
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"На жаль, не вдалось отримати факт ({type(e).__name__}). Спробуйте ще раз."
