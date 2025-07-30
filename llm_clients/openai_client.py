from openai import OpenAI
import json

with open("api_keys.json", "r") as f:
    config = json.load(f)

client = OpenAI(api_key=config["openai_api_key"])


def get_llm_response(prompt):
    response = ""
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
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
    prompt = "Write a short story about a robot learning to paint"
    result = get_llm_response(prompt)
    print(f"\nComplete response length: {len(result)} characters")


if __name__ == "__main__":
    main()
