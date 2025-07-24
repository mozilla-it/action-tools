<!-- This document is automatically generated. Do not edit by hand! -->
# Hello World

Minimal GitHub Action


## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `greeting` | The greeting to use | True | |
| `target` | Who to give the greeting to | False | `World`|



## Example Usage
### Minimal Configuration
```yaml
- uses: org/repo/tests/gendocs/__fixtures__
  with:
    greeting: Hello
```

### Minimal Configuration with Defaults
```yaml
- uses: org/repo/tests/gendocs/__fixtures__
  with:
    greeting: Hello
    target: World
```

