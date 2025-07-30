from google import genai
import json
import os

config_path = os.path.join(os.path.dirname(__file__), "api_keys.json")

with open(config_path, "r") as f:
    config = json.load(f)

client = genai.Client(api_key=config["gemini_api_key"])


def get_llm_response(prompt):
    response = ""
    stream = client.models.generate_content_stream(
        model='gemini-2.5-pro',
        contents=prompt
    )

    for chunk in stream:
        if chunk.text:
            content = chunk.text
            print(content, end="", flush=True)
            response += content

    print()
    return response


def main():
    prompt = "你谁啊"
    result = get_llm_response(prompt)
    print(f"\nComplete response length: {len(result)} characters")


if __name__ == "__main__":
    main()
