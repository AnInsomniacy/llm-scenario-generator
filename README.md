# llm-scenario-generator

> **Complete reimplementation of the original ChatScene system** - Referenced and utilized parts of the original code
> database, but most architecture and functionality have been rewritten and optimized

## 🎯 Functionality

**Input:** Natural language scenario requirement descriptions

```
"Generate a safety-critical scenario"
"Emergency braking scenario on straight road"
```

**Output:** Executable CARLA simulation code

- Complete Scenic script files
- Simulation scenarios containing vehicle behaviors, road geometry, and relative positions

## 🔄 Workflow

1. **Scenario Description Generation** - LLM generates detailed scenario text descriptions based on input
2. **Component Decomposition** - Automatically parses into behavior, geometry, and position components
3. **Code Retrieval** - Matches corresponding Scenic code snippets from pre-built knowledge base
4. **Script Assembly** - Synthesizes code snippets into complete executable simulation scripts