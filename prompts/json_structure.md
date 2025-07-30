# Scenario JSON Output Schema

## Structure

```json
{
  "success": true,
  "adversarial_object": "Car",
  "behavior": "string",
  "geometry": "string",
  "spawn_position": "string"
}
```

## Fields

| Field                | Type        | Description                                              |
|----------------------|-------------|----------------------------------------------------------|
| `success`            | boolean     | `true` if extraction successful, `false` otherwise       |
| `adversarial_object` | string/null | Must be: "Car", "Pedestrian", "Bicycle", or "Motorcycle" |
| `behavior`           | string/null | Description of adversarial agent's dangerous behavior    |
| `geometry`           | string/null | Road conditions and environment description              |
| `spawn_position`     | string/null | Initial relative position to ego vehicle                 |

## Rules

- **Success = true**: All fields populated with valid data
- **Success = false**: All other fields set to `null`
- **Output**: Raw JSON only, no additional text

## Examples

**Success:**

```json
{
  "success": true,
  "adversarial_object": "Car",
  "behavior": "The adversarial car suddenly brakes as the ego approaches.",
  "geometry": "A straight road.",
  "spawn_position": "The adversarial agent is directly in front of the ego vehicle on the same straight road, heading in the same direction."
}
```

**Failure:**

```json
{
  "success": false,
  "adversarial_object": null,
  "behavior": null,
  "geometry": null,
  "spawn_position": null
}
```