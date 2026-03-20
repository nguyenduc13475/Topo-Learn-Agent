import json
import re
import time
from typing import Any, Type

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash-lite"

    # Retry with exponential backoff: Wait 2^x * 1 seconds between each retry,
    # up to 10s, max 5 attempts
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def generate_structured_output(
        self, prompt: str, response_schema: Type[Any], system_instruction: str = None
    ) -> dict:
        """
        Send a prompt and force the model to return strictly validated JSON
        using Pydantic schemas.
        """
        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,  # Force strict JSON adherence
                system_instruction=system_instruction,
                temperature=0.1,  # Low temperature for analytical extraction
            )
            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt, config=config
            )

            # Safety & Empty Response Handling
            if not response.candidates or not response.candidates[0].content.parts:
                print("[GeminiClient] Blocked by safety settings or returned empty.")
                return {}

            raw_text = response.text.strip()

            # Extract JSON inside markdown ```json ... ```
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_text, re.DOTALL)

            if match:
                raw_text = match.group(1).strip()

            try:
                return json.loads(raw_text)
            except json.JSONDecodeError as e:
                print(
                    f"[GeminiClient] JSON Decode Error: {e}\nRaw Output: {raw_text[:200]}"
                )
                return {}
        except Exception as e:
            print(f"[GeminiClient] API Error encountered: {e}. Retrying...")
            raise e

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def describe_image(
        self, image_path: str, prompt: str = "Describe this academic image in detail"
    ) -> str:
        """
        Send an image to Gemini Vision API for detailed description.
        """
        try:
            print(f"Sending image {image_path} to Gemini for description...")
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type="image/jpeg",
                    ),
                ],
            )
            return response.text
        except Exception as e:
            print(f"[GeminiClient] Vision API Error: {e}. Retrying...")
            raise e

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def process_multimodal_file(
        self, file_path: str, prompt: str, mime_type: str
    ) -> str:
        """
        Uploads a raw document or video to Gemini and generates text based on the prompt.
        """
        print(f"[GeminiClient] Uploading {file_path} to Gemini File API...")
        uploaded_file = None
        try:
            # Upload file directly to Gemini's temporary storage
            uploaded_file = self.client.files.upload(
                file=file_path, config={"mime_type": mime_type}
            )

            # Videos take a moment to process on Google's end. Apply strict timeout.
            timeout_seconds = 600  # Max 10 minutes wait
            start_time = time.time()

            while uploaded_file.state.name == "PROCESSING":
                if time.time() - start_time > timeout_seconds:
                    raise TimeoutError(
                        f"Gemini File API processing timed out after {timeout_seconds} seconds."
                    )
                print(".", end="", flush=True)
                time.sleep(
                    5
                )  # Increased sleep to prevent rate-limiting the GET request
                uploaded_file = self.client.files.get(name=uploaded_file.name)

            if uploaded_file.state.name == "FAILED":
                raise ValueError("Gemini failed to process the uploaded file.")

            print("\n[GeminiClient] File ready. Generating content...")
            response = self.client.models.generate_content(
                model=self.model_name, contents=[uploaded_file, prompt]
            )
            return response.text

        except Exception as e:
            print(f"[GeminiClient] Multimodal processing error: {e}")
            raise e
        finally:
            # Clean up the file from Google's servers to respect limits
            if uploaded_file:
                try:
                    self.client.files.delete(name=uploaded_file.name)
                    print(f"[GeminiClient] Cleaned up remote file {uploaded_file.name}")
                except Exception as cleanup_error:
                    print(
                        f"[GeminiClient] Note: Failed to delete remote file: {cleanup_error}"
                    )


# Create a global instance to import and share across the entire app
gemini_client = GeminiClient()
