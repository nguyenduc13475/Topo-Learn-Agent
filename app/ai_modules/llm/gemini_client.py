import json
import base64
from google import genai
from google.genai import types
from app.core.config import settings


class GeminiClient:
    def __init__(self):
        # Initialize the client with the API key from the .env file
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-3-flash"

    def generate_json_output(self, prompt: str, system_instruction: str = None) -> dict:
        """
        Send a prompt and force the model to return in plain JSON format.
        """
        try:
            # Configure JSON return settings and encapsulate System Instructions.
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction,
            )

            # Call API
            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt, config=config
            )

            # Parse the resulting text into a Dictionary
            return json.loads(response.text)

        except json.JSONDecodeError:
            # Handle fallback if AI returns JSON formatting errors
            return {}
        except Exception as e:
            # Catch other errors (such as exceeding quota, network disconnection, etc.)
            print(f"Error when calling Gemini API: {e}")
            return {}

    def describe_image(
        self, image_path: str, prompt: str = "Describe this academic image in detail"
    ) -> str:
        """
        Send an image to Gemini Vision API for detailed description.
        """
        try:
            print(f"Sending image {image_path} to Gemini for description...")
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=base64.b64decode(encoded_string),
                        mime_type="image/jpeg",
                    ),
                ],
            )
            return response.text
        except Exception as e:
            print(f"Vision API Error: {e}")
            return "Image description unavailable."


# Create a global instance to import and share across the entire app
gemini_client = GeminiClient()
