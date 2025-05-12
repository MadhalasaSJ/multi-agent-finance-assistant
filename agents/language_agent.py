import os
import openai
from dotenv import load_dotenv

class LanguageAgent:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("openai_api"))

    def synthesize_brief(self, retrieved_texts, market_data):
        prompt = f"""You are a market assistant.
Summarize today's Asia tech risk and highlight earnings.

Market data:
{market_data}

Documents:
{retrieved_texts}

Respond concisely and factually."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    
if __name__ == "__main__":
    agent = LanguageAgent()

    retrieved_docs = [
        "TSMC beat earnings by 4%.",
        "Samsung missed estimates by 2%.",
        "Alibaba reports later today."
    ]

    market_data = {
        "TSM": {"current_close": 176.5, "previous_close": 175.2, "change_percent": 0.74},
        "005930.KS": {"current_close": 57600.0, "previous_close": 54800.0, "change_percent": 5.11},
        "BABA": {"current_close": 125.3, "previous_close": 125.79, "change_percent": -0.37}
    }

    brief = agent.synthesize_brief(retrieved_docs, market_data)
    print("🧠 Market Brief:\n", brief)    
