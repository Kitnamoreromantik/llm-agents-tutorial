# LangGraph Tutorial – Summer School 2025

This repository contains a hands-on tutorial for building stateful and cyclic LLM agents using [LangGraph](https://github.com/langchain-ai/langgraph).

## Goals

- Understand state graphs and agent workflows
- Implement conditional and multi-step reasoning with LLMs
- Combine tools and memory in LangGraph agents

## Requirements

- `Python 3.12.7`
- `uv`

## Dependecies

Some installations:

```bash
brew install python@3.12  # on Mac os
winget install Python.Python.3.12  # Win

python3.12 --version  # to check
brew install pipx

pipx --version
# -> 1.7.1

pipx install uv
uv --version
# -> uv 0.7.17 (41c218a89 2025-06-29)
```

Create virtual environment:

``` bash
uv venv .venv-llm-agents-tutorial
source .venv-llm-agents-tutorial/bin/activate
```

Libraries installations:

```bash
uv pip install langgraph
uv pip freeze > requirements.txt
```

