import json
from pathlib import Path
from chroma_database.scenic_retriever import search_snippets
from llm_clients.deepseek_client import get_llm_response
from scenic_validator import validate_scenic_code

BASE_DIR = Path(__file__).parent.parent
BEHAVIOR_PROMPT_PATH = BASE_DIR / "prompts" / "behavior.txt"
GEOMETRY_PROMPT_PATH = BASE_DIR / "prompts" / "geometry.txt"
SPAWN_PROMPT_PATH = BASE_DIR / "prompts" / "spawn.txt"
SCENARIO_DECOMPOSITION_PATH = BASE_DIR / "prompts" / "decomposition.txt"
CODE_INTEGRATION_PROMPT_PATH = BASE_DIR / "prompts" / "integration.txt"


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


def load_prompt_template(prompt_path):
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to load prompt template {prompt_path}: {e}{Colors.END}")
        raise


def clean_json_response(response):
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned.strip()


def extract_code_between_backticks(text):
    first_backticks = text.find('```')
    last_backticks = text.rfind('```')
    if first_backticks == -1 or first_backticks == last_backticks:
        return text.strip()
    start_pos = first_backticks + 3
    first_newline = text.find('\n', start_pos)
    if first_newline != -1 and first_newline < last_backticks:
        start_pos = first_newline + 1
    code = text[start_pos:last_backticks]
    return code.strip()


def decompose_scenario(scenario):
    try:
        print("Loading prompt template...")
        prompt_template = load_prompt_template(SCENARIO_DECOMPOSITION_PATH)
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
            print(f"{Colors.RED}Failed - Response is not valid JSON: {e}{Colors.END}")
            return None

        if not result_json.get("success", False):
            print(f"{Colors.RED}Failed - Scenario decomposition marked as unsuccessful{Colors.END}")
            return None

        adversarial_object = result_json["adversarial_object"]
        behavior = result_json["behavior"]
        geometry = result_json["geometry"]
        spawn_position = result_json["spawn_position"]
        success = result_json["success"]

        print(f"\n{Colors.GREEN}Success{Colors.END}")
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
        print(f"{Colors.RED}Failed - Unexpected error: {e}{Colors.END}")
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
    try:
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

        cleaned_code = clean_code_block(response)

        print(f"{Colors.CYAN}{Colors.BOLD}=== CLEANED LLM RESPONSE FOR {category_type.upper()} ==={Colors.END}")
        print(f"{Colors.WHITE}{cleaned_code}{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        print()

        print_success(f"{category_type.capitalize()} code generated")
        return response.strip()
    except Exception as e:
        print(f"{Colors.RED}✗ Error generating {category_type} code: {e}{Colors.END}")
        raise


def clean_code_block(code):
    return extract_code_between_backticks(code)


def extract_town_from_geometry(geometry_code):
    try:
        print("  • Extracting town information...")
        for line in geometry_code.split('\n'):
            if 'Town' in line and '=' in line:
                town_part = line.split('=')[1].strip().strip('\'"')
                print_success(f"Town extracted: {town_part}")
                return town_part
        print_success("Using default town: Town04")
        return "Town04"
    except Exception as e:
        print(f"{Colors.RED}✗ Error extracting town: {e}{Colors.END}")
        return "Town04"


def remove_town_line(geometry_code):
    try:
        print("  • Removing town definition from geometry...")
        lines = []
        for line in geometry_code.split('\n'):
            if not (line.strip().startswith('Town') and '=' in line):
                lines.append(line)
        return '\n'.join(lines).strip()
    except Exception as e:
        print(f"{Colors.RED}✗ Error removing town line: {e}{Colors.END}")
        return geometry_code


def build_scenic_header(town):
    try:
        print(f"  • Building scenic header for {town}...")
        return f'''param map = localPath('../maps/{town}.xodr')
param carla_map = '{town}'
model scenic.simulators.carla.model
EGO_MODEL = "vehicle.lincoln.mkz_2017"'''
    except Exception as e:
        print(f"{Colors.RED}✗ Error building scenic header: {e}{Colors.END}")
        raise


def integrate_code_components(scenario_description, town, scenic_header, behavior_code, geometry_code, spawn_code):
    try:
        print("  • Loading integration prompt template...")
        prompt_template = load_prompt_template(CODE_INTEGRATION_PROMPT_PATH)

        integration_prompt = prompt_template.format(
            scenario_description=scenario_description,
            town=town,
            scenic_header=scenic_header,
            behavior_code=behavior_code,
            geometry_code=geometry_code,
            spawn_code=spawn_code
        )

        print(f"{Colors.YELLOW}{Colors.BOLD}=== FULL PROMPT FOR INTEGRATION ==={Colors.END}")
        print(f"{Colors.WHITE}{integration_prompt}{Colors.END}")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.END}")
        print()

        print("  • Sending integration request to LLM...")
        response = get_llm_response(integration_prompt)
        integrated_code = clean_code_block(response)

        print(f"{Colors.CYAN}{Colors.BOLD}=== CLEANED LLM RESPONSE FOR INTEGRATION ==={Colors.END}")
        print(f"{Colors.WHITE}{integrated_code}{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")
        print()

        print_success("Code integration completed")
        return integrated_code

    except Exception as e:
        print(f"{Colors.RED}✗ Integration error: {e}{Colors.END}")
        return None


def generate_scenario_code(scenario_description):
    try:
        print(f"{Colors.BOLD}{Colors.PURPLE}SCENIC CODE GENERATOR{Colors.END}")
        print(f"Scenario: {scenario_description}")
        print()

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
        print_step("STEP 4: LLM CODE INTEGRATION", Colors.GREEN)

        integrated_code = integrate_code_components(
            scenario_description,
            town,
            scenic_header,
            behavior_code,
            geometry_code,
            spawn_code
        )

        if not integrated_code:
            print(f"{Colors.RED}✗ Code integration failed{Colors.END}")
            return None

        print()
        print_step("FINAL INTEGRATED SCENIC CODE", Colors.BOLD + Colors.WHITE)
        print("=" * 80)
        print(f"{Colors.WHITE}{integrated_code}{Colors.END}")
        print("=" * 80)

        print_success("Scenic code generation completed successfully")
        return integrated_code

    except Exception as e:
        print(f"{Colors.RED}✗ Error generating scenario code: {e}{Colors.END}")
        return None


def main():
    test_scenario = "The ego encounters a parked car blocking its lane and must use the opposite lane to bypass the vehicle, carefully assessing the situation and yielding to oncoming traffic, when an oncoming motorcyclist swerves into the lane unexpectedly, necessitating the ego to brake or maneuver to avoid a potential accident."

    try:
        scenic_code = generate_scenario_code(test_scenario)

        if scenic_code:
            print()
            validation_result = validate_scenic_code(scenic_code)
            if validation_result["valid"]:
                print_success("All processes completed successfully")
            else:
                print(f"{Colors.RED}✗ Code validation failed: {validation_result['error']}{Colors.END}")

    except Exception as e:
        print(f"✗ Error in main: {e}")


if __name__ == "__main__":
    main()
