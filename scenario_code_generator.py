import os
import json
from chroma_database.scenic_retriever import search_snippets
from llm_clients.gemini_client import get_llm_response

BEHAVIOR_PROMPT_PATH = "prompts/behavior.txt"
GEOMETRY_PROMPT_PATH = "prompts/geometry.txt"
SPAWN_PROMPT_PATH = "prompts/spawn.txt"
SCENARIO_DECOMPOSITION_PATH = "prompts/decomposition.txt"


class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(step_name, color=Colors.BLUE):
    print(f"{color}{Colors.BOLD}[{step_name}]{Colors.END}")


def print_success(message, color=Colors.GREEN):
    print(f"{color}✓ {message}{Colors.END}")


def print_code_section(section_name, code, color=Colors.CYAN):
    print(f"{color}{Colors.BOLD}=== {section_name} ==={Colors.END}")
    print(f"{Colors.WHITE}{code}{Colors.END}")
    print()


def load_prompt_template(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def load_decomposition_template():
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
        prompt_template = load_decomposition_template()
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


def format_snippets_content(snippets):
    content_parts = []
    for i, snippet in enumerate(snippets, 1):
        content_parts.append(f"--- Example {i} ---")
        content_parts.append(f"Description: {snippet['description']}")
        content_parts.append(f"Snippet: {snippet['code']}")
        content_parts.append("=" * 50)
        content_parts.append("")
    return "\n".join(content_parts)


def generate_code_for_category(category_description, category_type, prompt_path):
    print(f"  • Retrieving {category_type} snippets...")
    snippets = search_snippets(category_description, category_type, limit=3)

    print(f"  • Loading {category_type} prompt template...")
    prompt_template = load_prompt_template(prompt_path)
    formatted_content = format_snippets_content(snippets)

    full_prompt = prompt_template.replace("{content}", formatted_content)
    full_prompt = full_prompt.replace("{current_description}", category_description)

    print(f"{Colors.YELLOW}{Colors.BOLD}=== FULL PROMPT FOR {category_type.upper()} ==={Colors.END}")
    print(f"{Colors.WHITE}{full_prompt}{Colors.END}")
    print(f"{Colors.YELLOW}{'=' * 50}{Colors.END}")
    print()

    print(f"  • Generating {category_type} code with LLM...")
    response = get_llm_response(full_prompt)

    print(f"{Colors.CYAN}{Colors.BOLD}=== LLM RESPONSE FOR {category_type.upper()} ==={Colors.END}")
    print(f"{Colors.WHITE}{response.strip()}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
    print()

    print_success(f"{category_type.capitalize()} code generated")
    return response.strip()


def clean_code_block(code):
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        if not line.strip().startswith('```'):
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()


def extract_town_from_geometry(geometry_code):
    print("  • Extracting town information...")
    for line in geometry_code.split('\n'):
        if 'Town' in line and '=' in line:
            town_part = line.split('=')[1].strip().strip('\'"')
            print_success(f"Town extracted: {town_part}")
            return town_part
    print_success("Using default town: Town04")
    return "Town04"


def remove_town_line(geometry_code):
    print("  • Removing town definition from geometry...")
    lines = []
    for line in geometry_code.split('\n'):
        if not (line.strip().startswith('Town') and '=' in line):
            lines.append(line)
    return '\n'.join(lines).strip()


def build_scenic_header(town):
    print(f"  • Building scenic header for {town}...")
    return f'''param map = localPath('../maps/{town}.xodr')
param carla_map = '{town}'
model scenic.simulators.carla.model
EGO_MODEL = "vehicle.lincoln.mkz_2017"'''


def generate_scenario_code(scenario_description):
    try:
        print_step("STEP 1: SCENARIO DECOMPOSITION", Colors.PURPLE)
        decomposition_result = decompose_scenario(scenario_description)

        if not decomposition_result or not decomposition_result.get("success", False):
            print(f"{Colors.RED}✗ Scenario decomposition failed{Colors.END}")
            return None

        adversarial_object = decomposition_result.get("adversarial_object", "Vehicle")
        print_success("Scenario decomposed successfully")
        print(f"  Adversarial object: {adversarial_object}")
        print()

        print_step("STEP 2: CODE GENERATION", Colors.YELLOW)

        behavior_code = generate_code_for_category(
            decomposition_result["behavior"],
            "behavior",
            BEHAVIOR_PROMPT_PATH
        )
        print()

        geometry_code = generate_code_for_category(
            decomposition_result["geometry"],
            "geometry",
            GEOMETRY_PROMPT_PATH
        )
        print()

        spawn_code = generate_code_for_category(
            decomposition_result["spawn_position"],
            "spawn",
            SPAWN_PROMPT_PATH
        )
        print()

        print_step("STEP 3: CODE PROCESSING", Colors.CYAN)

        print("  • Cleaning code blocks...")
        behavior_code = clean_code_block(behavior_code)
        geometry_code = clean_code_block(geometry_code)
        spawn_code = clean_code_block(spawn_code)

        town = extract_town_from_geometry(geometry_code)
        geometry_code = remove_town_line(geometry_code)
        scenic_header = build_scenic_header(town)

        print("  • Processing adversarial object placeholder...")
        if "{AdvObject}" in spawn_code:
            spawn_code = spawn_code.replace("{AdvObject}", adversarial_object)
            print_success(f"Replaced {{AdvObject}} with {adversarial_object}")

        print()
        print_step("STEP 4: CODE ASSEMBLY", Colors.GREEN)

        print_code_section("SCENARIO DESCRIPTION", f'"""{scenario_description}"""')
        print_code_section("SCENIC HEADER", scenic_header)
        print_code_section("BEHAVIOR CODE", behavior_code)
        print_code_section("GEOMETRY CODE", geometry_code)
        print_code_section("SPAWN CODE", spawn_code)

        scenic_code = f'''"""{scenario_description}"""

{scenic_header}

{behavior_code}

{geometry_code}

{spawn_code}'''

        print_step("FINAL SCENIC CODE", Colors.BOLD + Colors.WHITE)
        print("=" * 80)
        print(f"{Colors.WHITE}{scenic_code}{Colors.END}")
        print("=" * 80)

        print_success("Scenic code generation completed successfully")
        return scenic_code

    except Exception as e:
        print(f"{Colors.RED}✗ Error generating scenario code: {e}{Colors.END}")
        return None


def main():
    test_scenario = "A car is driving through a busy city street when a cyclist suddenly swerves into the path of the car, forcing it to brake hard to avoid a collision."

    print(f"{Colors.BOLD}{Colors.PURPLE}SCENIC CODE GENERATOR{Colors.END}")
    print(f"Scenario: {test_scenario}")
    print()

    try:
        scenic_code = generate_scenario_code(test_scenario)

        if not scenic_code:
            print(f"{Colors.RED}✗ Failed to generate scenic code{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}✗ Error in main: {e}{Colors.END}")


if __name__ == "__main__":
    main()
