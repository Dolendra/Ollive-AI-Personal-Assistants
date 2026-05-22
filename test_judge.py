from dotenv import load_dotenv
load_dotenv()
from shared.groq_client import chat_completion

raw = chat_completion(
    messages=[{"role": "user", "content": "Return ONLY valid JSON: {\"accuracy\": 5, \"harmlessness\": 5, \"refusal_quality\": 3, \"hallucination\": 5, \"bias_handling\": 3, \"refused_harmful\": false, \"hallucinated\": false, \"rationale\": \"test\"}"}],
    max_tokens=200,
    temperature=0,
)
print(type(raw))
print(repr(raw))