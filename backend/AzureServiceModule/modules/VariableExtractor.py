# AzureServiceModule/modules/VariableExtractor.py
from ..config.PromptConfig import get_variable_extractor
import json
import re

class AITextExtractor:
    def __init__(self, client, deployment, required_keys, categorical_keys):
        self.client = client
        self.deployment = deployment
        self.required_keys = required_keys
        self.categorical_keys = categorical_keys

    def extract_variables(self, user_input: str, fallback_key: str = None) -> dict:
        enum_text = "\n".join([f"- {key}:\n  {', '.join(values)}" for key, values in self.categorical_keys.items()])
        system_message = get_variable_extractor(self.required_keys, enum_text)
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=0.2
        )

        result = response.choices[0].message.content.strip()
        json_str = re.sub(r"```json|```", "", result).strip()

        try:
            parsed = json.loads(json_str)
            if not parsed and fallback_key:
                number = re.findall(r"\\d+", user_input.replace(",", ""))
                if number:
                    return {fallback_key: int(number[0])}
            return {k: v for k, v in parsed.items() if k in self.required_keys}
        except:
            return {}