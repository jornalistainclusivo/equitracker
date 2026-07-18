import httpx
import logging
import json
from typing import Optional, List
from app.core.config import settings
from app.schemas.analysis import AnalysisResult

logger = logging.getLogger(__name__)

class DynamicLLMService:
    TIMEOUT = 180.0

    @classmethod
    async def _call_provider(cls, system_prompt: str, user_prompt: str, response_format: str = "json") -> str:
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "groq":
            return await cls._call_openai_compatible(
                "https://api.groq.com/openai/v1/chat/completions",
                settings.GROQ_API_KEY,
                "llama3-8b-8192",
                system_prompt, user_prompt, response_format
            )
        elif provider == "openrouter":
            return await cls._call_openai_compatible(
                "https://openrouter.ai/api/v1/chat/completions",
                settings.OPENROUTER_API_KEY,
                settings.OPENROUTER_MODEL,
                system_prompt, user_prompt, response_format
            )
        elif provider == "gemini":
            return await cls._call_gemini(system_prompt, user_prompt)
        else:
            # Fallback to Ollama
            return await cls._call_ollama(system_prompt, user_prompt, response_format)

    @classmethod
    async def _call_openai_compatible(cls, url: str, api_key: str, model: str, system_prompt: str, user_prompt: str, response_format: str) -> str:
        if not api_key:
            raise ValueError(f"API key missing for endpoint: {url}")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
            
        async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    @classmethod
    async def _call_gemini(cls, system_prompt: str, user_prompt: str) -> str:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY missing")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [{
                "parts": [{"text": user_prompt}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    @classmethod
    async def _call_ollama(cls, system_prompt: str, user_prompt: str, response_format: str) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        prompt = f"{system_prompt}\n\n{user_prompt}"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        if response_format == "json":
            payload["format"] = "json"
            
        async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                logger.error(f"Ollama failed: {e}")
                raise

    @classmethod
    async def summarize(cls, text: str) -> str:
        """
        Summarizes the provided text using the dynamic provider.
        """
        try:
            truncated_text = text[:6000]
            system_prompt = "Summarize this journalism source in Portuguese. Make it concise and executive."
            user_prompt = f"Text:\n\n{truncated_text}"
            return await cls._call_provider(system_prompt, user_prompt, response_format="text")
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise Exception(f"Summarization failed: {str(e)}")

    @classmethod
    async def analyze_article(cls, text: str) -> AnalysisResult:
        """
        Analyzes the article for Inclusion & Equity.
        Returns a score (0-100), reasoning, and suggested prompts.
        """
        try:
            truncated_text = text[:8000]
            
            system_prompt = """
            You are the EquiTracker Equity Engine, an expert in Media Representation, Intersectionality, and Data Voids.
            Your task is to analyze the following journalism text for Inclusivity.
            
            CRITERIA FOR SCORING (0-100):
            - 0-20: Harmful stereotypes, erasure of minorities, active bias.
            - 21-50: Neutral but exclusionary (e.g., only official sources, "manels").
            - 51-80: Good representation, diverse sources, neutral terminology.
            - 81-100: Transformative, intersectional, voices of the marginalized are central.

            OUTPUT FORMAT:
            You must output ONLY valid JSON in the following format:
            {
                "inclusion_score": <int 0-100>,
                "suggested_prompts": [
                    "<Question 1>",
                    "<Question 2>",
                    "<Question 3>"
                ],
                "reasoning": "<Paragraph justifying the score in Portuguese>"
            }

            REQUIREMENTS FOR PROMPTS:
            - Write the suggested_prompts and reasoning in Portuguese (pt-BR).
            - Must ask about "Data Voids" (who is missing?).
            - GENERATE EXACTLY 3 PROMPTS.
            - EACH PROMPT MUST BE A SHORT, PROVOCATIVE QUESTION (MAX 6 WORDS) with an EMOJI.
            """

            user_prompt = f"Analyze this text:\n\n{truncated_text}"
            
            generated_text = await cls._call_provider(system_prompt, user_prompt, "json")
            
            try:
                if "```json" in generated_text:
                    generated_text = generated_text.split("```json")[1].split("```")[0].strip()
                elif "```" in generated_text:
                    generated_text = generated_text.split("```")[0].strip()
                
                data = json.loads(generated_text)
                
                return AnalysisResult(
                    inclusion_score=data.get("inclusion_score", data.get("score", 50)),
                    suggested_prompts=data.get("suggested_prompts", data.get("prompts", [])),
                    reasoning=data.get("reasoning", data.get("summary", "Nenhuma justificativa fornecida."))
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from LLM: {generated_text}")
                return AnalysisResult(
                    inclusion_score=50,
                    suggested_prompts=["Quais vozes faltaram?", "Existe viés de classe?", "Qual o contexto?"],
                    reasoning="Erro na geração da IA. Atribuída pontuação neutra."
                )
        except Exception as e:
            logger.exception("Analysis failed with exception")
            raise Exception(f"Analysis failed: {str(e)}")
