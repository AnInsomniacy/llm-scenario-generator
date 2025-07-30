# Scenic Codebase Structure

## Database Configuration

- **Database Name**: `scenic_codebase`
- **Collection Name**: `scenario_snippets`
- **Storage Path**: `scenic_codebase/`

## Record Structure

### API Layer View

```python
{
    "description": "Vehicle lane change behavior",  # Search text
    "metadata": {
        "uid": "behavior_001",  # Unique identifier
        "type": "behavior",  # Category type
        "code": "behavior LaneChange: take 2s to..."  # Code snippet
    }
}
```

### Parameter Mapping

| Field         | Type   | Description                  | Purpose              |
|---------------|--------|------------------------------|----------------------|
| `description` | String | Natural language description | Vector search target |
| `uid`         | String | Unique record identifier     | Primary key          |
| `type`        | String | Category classification      | Filter criterion     |
| `code`        | String | Executable code snippet      | Retrieved content    |

### Category Types

- `behavior` - Vehicle behavior patterns
- `geometry` - Road geometry definitions
- `spawn` - Object spawn configurations

### ID Convention

- Format: `{type}_{index:03d}`
- Examples: `behavior_001`, `geometry_015`, `spawn_007`

## Usage Examples

### Query by Description

```python
results = collection.query(
    query_texts=["lane change behavior"],
    n_results=3
)
```

### Filter by Type

```python
results = collection.get(
    where={"type": "behavior"},
    include=["documents", "metadatas"]
)
```

### Access Code Snippet

```python
code = results['metadatas'][0]['code']
```