import httpx
from typing import Optional

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

        except httpx.ConnectError:
            raise Exception("Failed to connect to Ollama. Ensure it is running on http://127.0.0.1:11434")
        except httpx.TimeoutException:
            raise Exception(f"Ollama request timed out after {cls.TIMEOUT} seconds")
        except Exception as e:
            raise Exception(f"Ollama summarization failed: {str(e)}")
