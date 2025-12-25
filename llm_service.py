import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        windows_ip = os.getenv("WINDOWS_IP")
        
        self.client = AsyncOpenAI(
            base_url=f"http://{windows_ip}:11434/v1",
            api_key="ollama"
        )

    async def generate_ideas(self, topic: str, count: int) -> list[str]:
        prompt = (
            f"Сгенерируй ровно {count} коротких названий (идей) для темы: '{topic}'.\n"
            "ПРАВИЛА:\n"
            "1. Пиши ТОЛЬКО названия НА РУССКОМ ЯЗЫКЕ.\n"
            "2. НИКАКИХ описаний, пояснений, двоеточий или лишних слов.\n"
            "3. Используй обычные пробелы (не нижние подчеркивания).\n"
            "4. Верни ТОЛЬКО JSON массив строк. Пример: [\"Название 1\", \"Название 2\"]."
        )
        try:
            response = await self.client.chat.completions.create(
                model="mistral",
                messages=[
                    {"role": "system", "content": "You are a creative assistant that strictly outputs JSON. Use normal spaces in text, never underscores."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
            )
            
            content = response.choices[0].message.content.strip()

            # очистка от мусора
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            # парсинг json
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # очистка от лишних запятых/символов
                content = content.replace('\n', ' ').strip()
                result = json.loads(content)
            
            # финальная обработка текста
            if isinstance(result, list):
                clean_ideas = [str(idea).replace("_", " ") for idea in result]
                return clean_ideas[:count]
            
            return [str(result).replace("_", " ")]
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return [f"Error: {str(e)}"]

llm_brain = LLMService()