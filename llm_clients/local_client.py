from openai import OpenAI

SERVER_URL = "http://127.0.0.1:1234"

client = OpenAI(base_url=f"{SERVER_URL}/v1", api_key="not-needed")


def get_llm_response(prompt):
    response = ""
    completion = client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in completion:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            response += content

    print()
    return response


def main():
    prompt = "Explain quantum computing in simple terms"
    result = get_llm_response(prompt)
    print(f"\nComplete response length: {len(result)} characters")


if __name__ == "__main__":
    main()
