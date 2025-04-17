# AzureServiceModule/modules/PromptGenerator.py
from ..config.VariableConfig import planning_stage_keys, sales_stage_keys
from ..config.PromptConfig import get_prompt_generator


class PromptGenerator:
    def __init__(self, client, deployment, categorical_keys):
        self.client = client
        self.deployment = deployment
        self.categorical_keys = categorical_keys

    def generate(self, collected_vars: dict,  user_input, stage: str):
        collected_keys = list(collected_vars.keys())
        collected_list = ", ".join(collected_keys) if collected_keys else "없음"

        required_in_stage = sales_stage_keys if stage == "판매" else planning_stage_keys
        missing_keys = [k for k in required_in_stage if k not in collected_vars]
        next_key = missing_keys[0] if missing_keys else None

        next_variable_prompt = (
            f"\n⏳ 다음으로 반드시 유도해야 할 항목은: {next_key}"
            if next_key else "\n✅ 모든 변수가 수집되었습니다."
        )

        system_message = get_prompt_generator(collected_list, next_variable_prompt)
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content.strip(), next_key
