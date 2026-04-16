import anthropic

client = anthropic.Anthropic(
    import os
api_key=os.getenv("ANTHROPIC_API_KEY")

try:
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=50,
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )

    print("✅ SUCCESS")
    print(response.content[0].text)

except Exception as e:
    print("❌ ERROR")
    print(str(e))