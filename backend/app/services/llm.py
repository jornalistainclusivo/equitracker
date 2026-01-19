import httpx
import logging
from typing import Optional, List
import json
from app.schemas.analysis import AnalysisResult

# Configure logger
logger = logging.getLogger(__name__)

class OllamaService:
    OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
    MODEL = "gemma:2b"
    TIMEOUT = 180.0

    @classmethod
    async def summarize(cls, text: str) -> str:
        """
        Summarizes the provided text using the local Ollama instance.
        Truncates input to 6000 characters.
        """
        try:
            truncated_text = text[:6000]
            prompt = (
                f"Summarize this journalism source in Portuguese (based on the first 6000 chars): \n\n{truncated_text}"
            )
            
            payload = {
                "model": cls.MODEL,
                "prompt": prompt,
                "stream": False
            }

            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.post(cls.OLLAMA_URL, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")

        except httpx.ConnectError as e:
            logger.error(f"Ollama connection failed: {e}")
            raise Exception("Failed to connect to Ollama. Ensure it is running on http://127.0.0.1:11434")
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out: {e}")
            raise Exception(f"Ollama request timed out after {cls.TIMEOUT} seconds")
        except Exception as e:
            logger.error(f"Ollama summarization failed with unexpected error: {e}")
            raise Exception(f"Ollama summarization failed: {str(e)}")

    @classmethod
    async def analyze_article(cls, text: str) -> AnalysisResult:
        """
        Analyzes the article for Inclusion & Equity using the local Ollama instance.
        Returns a score (0-100) and suggested prompts.
        """
        try:
            truncated_text = text[:10000] # Increased context window for analysis
            
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
                "score": <int 0-100>,
                "prompts": [
                    "<Question 1>",
                    "<Question 2>",
                    "<Question 3>"
                ],
                "summary": "<Short justification>"
            }

            REQUIREMENTS FOR PROMPTS:
            - Must be specific to the article content.
            - Must ask about "Data Voids" (who is missing?).
            - Must challenge euphemisms or framing.
            - GENERATE EXACTLY 3 PROMPTS.
            - EACH PROMPT MUST BE A SHORT, PROVOCATIVE QUESTION (MAX 6 WORDS).
            - INSERT AN EMOJI AT THE START OF EACH PROMPT (e.g., 🔍, 🗣️, 📉).
            - EXAMPLES: "🔍 Quem financia o estudo?", "🗣️ Onde estão as fontes negras?", "📉 Dados sobre mulheres?"
            """

            user_prompt = f"Analyze this text:\n\n{truncated_text}"
            
            payload = {
                "model": cls.MODEL,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "format": "json" # Force JSON mode if model supports it, otherwise prompt instructions handle it
            }

            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.post(cls.OLLAMA_URL, json=payload)
                response.raise_for_status()
                
                result = response.json()
                generated_text = result.get("response", "")
                
                # Parse JSON from response
                try:
                    # Clean up markdown code blocks if present
                    if "```json" in generated_text:
                        generated_text = generated_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in generated_text:
                         generated_text = generated_text.split("```")[0].strip()
                    
                    data = json.loads(generated_text)
                    
                    return AnalysisResult(
                        inclusion_score=data.get("score", 0),
                        suggested_prompts=data.get("prompts", []),
                        summary=data.get("summary", "No summary provided.")
                    )
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from LLM: {generated_text}")
                    # Fallback
                    return AnalysisResult(
                        inclusion_score=50,
                        suggested_prompts=[
                            "Quais vozes foram marginalizadas neste texto?",
                            "Existe viés de classe na cobertura?",
                            "Como a terminologia afeta a percepção do leitor?"
                        ],
                        summary="Erro na análise automática. Pontuação neutra atribuída."
                    )

        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            raise Exception(f"Analysis failed: {str(e)}")
