# LLM Scenario Generator

An intelligent system that converts natural language descriptions into executable CARLA simulation scenarios using Large Language Models and retrieval-augmented generation.

## Overview

This tool automatically generates Scenic simulation scripts for CARLA autonomous driving scenarios from simple natural language inputs. It leverages LLMs to decompose scenario requirements and retrieves relevant code snippets from a curated knowledge base to assemble complete, executable simulation code.

## Features

- **Natural Language Input**: Describe scenarios in plain English
- **Automated Decomposition**: Intelligently breaks down scenarios into behavior, geometry, and positioning components
- **Code Retrieval**: Matches components against a pre-built knowledge base of Scenic code snippets
- **Multiple LLM Support**: Compatible with OpenAI, Google Gemini, DeepSeek, and local models
- **Validation**: Built-in Scenic code validation and syntax checking
- **Extensible Database**: ChromaDB-based vector storage for efficient snippet retrieval

## Requirements

- Python 3.8+
- CARLA Simulator (for executing generated scenarios)
- Scenic 2.1.0+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AnInsomniacy/llm-scenario-generator.git
cd llm-scenario-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
   - Edit `llm_clients/api_keys.json` and add your LLM provider API keys

## Usage

### Basic Usage

```python
import sys

sys.path.append('scenic_generation')
from auto_scenario_code_generator import generate_scenario_code

# Generate a scenario from natural language
scenario_description = "Emergency braking scenario on straight road"
scenic_code = generate_scenario_code(scenario_description)
```

### Command Line

```bash
cd scenic_generation
python auto_scenario_generator.py
```

### Example Input/Output

**Input:**
```
"The ego vehicle is driving on a straight road, and the car in front brakes suddenly as the ego approaches."
```

**Output:**
Complete Scenic script with:
- Road geometry definition
- Vehicle spawn positions
- Adversarial behavior implementation
- Simulation parameters

## Project Structure

```
├── llm_clients/           # LLM provider implementations
│   ├── openai_client.py   # OpenAI GPT integration
│   ├── gemini_client.py   # Google Gemini integration
│   ├── deepseek_client.py # DeepSeek integration
│   └── local_client.py    # Local model support
├── scenic-scenario-generation/
│   ├── auto_scenario_code_generator.py  # Main generation pipeline
│   ├── scenario_code_generator.py       # Core generation logic
│   └── scenic_validator.py              # Code validation
├── chroma_database/       # Vector database for code retrieval
│   ├── scenic_retriever.py              # Snippet retrieval logic
│   └── scenic_codebase/                 # Code snippet database
├── prompts/               # LLM prompt templates
│   ├── decomposition.txt  # Scenario decomposition prompts
│   ├── behavior.txt       # Behavior generation prompts
│   ├── geometry.txt       # Road geometry prompts
│   └── spawn.txt          # Spawn position prompts
└── requirements.txt       # Python dependencies
```

## How It Works

1. **Decomposition**: Natural language input is parsed into structured components (adversarial object, behavior, geometry, spawn position)
2. **Retrieval**: Each component is matched against the vector database to find relevant code snippets
3. **Generation**: LLM generates specific code for each component using retrieved examples
4. **Integration**: Components are assembled into a complete Scenic script
5. **Validation**: Generated code is validated for syntax and semantic correctness

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project builds upon the original ChatScene system with significant architectural improvements and optimizations.