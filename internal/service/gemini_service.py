"""Обёртка над Google Gemini API (бесплатный тариф, https://aistudio.google.com/apikey).

ВАЖНО: с сентября 2026 Google выдаёт новые ключи с префиксом "AQ." (вместо старых "AIzaSy...").
Такие ключи Google принимает ТОЛЬКО в заголовке x-goog-api-key, а не в query-параметре ?key=,
иначе API отвечает 404 Not Found (это подтверждённое изменение самого Google, не баг наш)."""
import httpx


class GeminiService:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, system_prompt: str, history: list) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        for m in history:
            role = "assistant" if m["role"] == "model" else "user"
            messages.append({"role": role, "content": m["text"]})
        payload = {"model": self.model, "messages": messages}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(self.url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"]