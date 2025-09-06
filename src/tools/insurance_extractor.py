import os
import json
import google.generativeai as genai

class InsuranceExtractor:
    def __init__(self, api_key=None):
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

    def extract_from_pdf(self, pdf_path):
        prompt = """
        Extract the following fields from the intake form:
        - insurance_carrier
        - insurance_member_id
        - insurance_group
        Return as JSON only.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        with open(pdf_path, "rb") as f:
            response = model.generate_content(
                [prompt, {"mime_type": "application/pdf", "data": f.read()}]
            )

        try:
            data = json.loads(response.text)
            return {"status": "ok", "insurance": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}
