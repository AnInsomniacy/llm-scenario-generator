import json
from llm_clients.gemini_client import get_llm_response

SCENARIO_DECOMPOSITION_PATH = "prompts/decomposition.txt"


def load_prompt_template():
    with open(SCENARIO_DECOMPOSITION_PATH, "r", encoding="utf-8") as f:
        return f.read()


def clean_json_response(response):
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned.strip()


def decompose_scenario(scenario):
    try:
        print("Loading prompt template...")
        prompt_template = load_prompt_template()
        full_prompt = prompt_template.replace("{scenario}", scenario)

        print("\nSending request to LLM...")
        response = get_llm_response(full_prompt)
        print(f"Model response:\n{response}")

        print("\nCleaning and parsing JSON...")
        cleaned_response = clean_json_response(response)
        try:
            result_json = json.loads(cleaned_response)
            print(f"Raw JSON data:\n{json.dumps(result_json, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"\033[91mFailed\033[0m - Response is not valid JSON: {e}")
            return None

        if not result_json.get("success", False):
            print(f"\033[91mFailed\033[0m - Scenario decomposition marked as unsuccessful")
            return None

        adversarial_object = result_json["adversarial_object"]
        behavior = result_json["behavior"]
        geometry = result_json["geometry"]
        spawn_position = result_json["spawn_position"]
        success = result_json["success"]

        print(f"\n\033[92mSuccess\033[0m")
        print(f"Adversarial Object: {adversarial_object}")
        print(f"Behavior: {behavior}")
        print(f"Geometry: {geometry}")
        print(f"Spawn Position: {spawn_position}")

        return {
            "success": success,
            "adversarial_object": adversarial_object,
            "behavior": behavior,
            "geometry": geometry,
            "spawn_position": spawn_position
        }

    except Exception as e:
        print(f"\033[91mFailed\033[0m - Unexpected error: {e}")
        return None


def main():
    test_scenario = "A car is driving through a busy city street with pedestrians and cyclists. Suddenly, a cyclist swerves into the path of the car, forcing it to brake hard to avoid a collision. The cyclist appears to be distracted by their phone and does not notice the car until it is very close."
    try:
        result = decompose_scenario(test_scenario)
        return result
    except Exception:
        return None


if __name__ == "__main__":
    main()
