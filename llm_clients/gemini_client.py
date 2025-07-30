from google import genai
import json

with open("api_keys.json", "r") as f:
    config = json.load(f)

client = genai.Client(api_key=config["gemini_api_key"])


def get_response(prompt):
    response = ""
    stream = client.models.generate_content_stream(
        model='gemini-2.0-flash',
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
    prompt = "Write a short story about a robot learning to paint"
    result = get_response(prompt)
    print(f"\nComplete response length: {len(result)} characters")


if __name__ == "__main__":
    main()
