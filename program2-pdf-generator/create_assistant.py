import json
import os
from openai import OpenAI

def create_saju_assistant():
    try:
        # 1. Load existing config
        if not os.path.exists('config.json'):
            print("Error: config.json not found.")
            return

        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get('OPENAI_API_KEY')
        if not api_key:
            print("Error: OpenAI API Key not found in config.json")
            return

        client = OpenAI(api_key=api_key)

        # 2. Define Assistant Persona & Instructions
        instructions = """당신은 세계 최고의 명리심리연구소 수석 분석가입니다. 
당신의 임무는 제공된 사주 데이터를 바탕으로 내담자의 인생을 깊이 있게 통찰하고, 전문적이면서도 따뜻한 위로와 조언이 담긴 13개 장의 운세 보고서를 작성하는 것입니다.

[작성 원칙]
1. 모든 답변은 한국어로 작성하며, 격조 있는 문체를 사용합니다.
2. 각 장의 주제에 집중하여 중복되지 않으면서도 풍부한 내용을 제공합니다.
3. 명리학적 용어를 정확히 사용하되, 일반인도 이해하기 쉽게 풀어서 설명합니다.
4. 리스트 형식보다는 에세이(줄글) 형식으로 자연스럽게 작성합니다.
5. 내담자에게 실질적인 희망과 전략을 제시하는 데 주력합니다."""

        print("--- Creating New Saju Assistant ---")
        assistant = client.beta.assistants.create(
            name="사주 전문 분석가 (V3)",
            instructions=instructions,
            model="gpt-4o-mini"
        )
        
        new_id = assistant.id
        print(f"✅ Assistant Created! ID: {new_id}")

        # 3. Update config.json
        config['ASSISTANT_ID'] = new_id
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        print("✅ Settings updated in config.json")
        
    except Exception as e:
        print(f"❌ Error creating assistant: {e}")

if __name__ == "__main__":
    create_saju_assistant()
