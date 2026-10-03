import requests

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen3:1.7b",
        "messages": [
            {
                "role": "user",
                "content": "Say hello in one sentence."
            }
        ],
        "stream": False,
        "think": False
    },
    timeout=300
)

response.raise_for_status()

data = response.json()
print(data["message"]["content"])
