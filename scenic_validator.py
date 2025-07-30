import subprocess
import scenic
from scenic.core.errors import ScenicError


class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(step_name, color=Colors.BLUE):
    print(f"{color}{Colors.BOLD}[{step_name}]{Colors.END}")


def print_success(message, color=Colors.GREEN):
    print(f"{color}✓ {message}{Colors.END}")


def validate_scenic_code(scenic_code):
    if not scenic_code:
        return {"valid": False, "error": "No code provided"}

    print_step("SCENIC CODE VALIDATION", Colors.BLUE)

    version_output = subprocess.run(['scenic', '--version'], capture_output=True, text=True, timeout=5)
    version_info = version_output.stdout.strip() if version_output.returncode == 0 else "Unknown version"
    print(f"  • Using Scenic version: {version_info}")

    print("  • Compiling scenic code for validation...")

    try:
        scenario = scenic.scenarioFromString(scenic_code)
        print_success("Syntax validation passed")
        return {"valid": True, "error": None}
    except Exception as e:
        error_msg = str(e)
        print(f"{Colors.RED}✗ Validation failed: {error_msg}{Colors.END}")
        return {"valid": False, "error": error_msg}
