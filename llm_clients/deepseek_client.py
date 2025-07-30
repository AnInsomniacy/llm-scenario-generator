from openai import OpenAI
import json
import os

config_path = os.path.join(os.path.dirname(__file__), "api_keys.json")

with open(config_path, "r") as f:
    config = json.load(f)

client = OpenAI(
    api_key=config["deepseek_api_key"],
    base_url="https://api.deepseek.com"
)


def get_llm_response(prompt):
    response = ""
    completion = client.chat.completions.create(
        model="deepseek-chat",
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
