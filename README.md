# Model UN Simulation with LLMs

A simulation platform for testing how different Large Language Models (LLMs) perform in Model UN-style diplomatic negotiations.

## Overview

This project creates a simulated environment where LLM agents representing different countries debate, propose solutions, and vote on resolutions related to international issues. The goal is to evaluate how models perform in diplomatic contexts, focusing on their persuasiveness, reasoning, consistency, and adherence to diplomatic norms.

## Features

- Multi-agent simulation with different LLMs via API calls (OpenAI, Hugging Face, Replicate)
- Model UN-inspired debate format with speeches, proposals, and voting
- Performance metrics tracking (messages sent, proposals passed, reputation)
- Export functionality for conversation history and metrics
- Voting mechanism for proposals with results tracking
- Mock mode for testing without API keys

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/model-un-simulation.git
cd model-un-simulation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
```

4. Run the simulation:
```bash
python main.py
```

## Configuration

- Modify `main.py` to change the debate topic, characters, or prompts
- Edit `models.json` to add new models or change priority settings
- Adjust `CHARACTERS` dictionary in `main.py` to change which countries participate
- Set `mock_mode=True` in `main.py` to run without API calls (for testing)

## Output

The simulation generates two types of output files in the `exports` directory:
- JSON history files with all messages, notes, and interactions
- Performance metrics tracking each agent's effectiveness

## Adding New Models

To add support for a new LLM provider:
1. Create a new class that inherits from the `Model` abstract base class
2. Implement the required methods (`_load_model()`, `query()`, etc.)
3. Update the `_load_model_options()` method in `ModelManager` to include your new class
4. Add models to the `models.json` configuration file

## Project Structure

- `programs/` - Core modules and classes
  - `models.py` - Model implementations for different LLM providers
  - `history.py` - Conversation and committee history tracking
  - `models.json` - Configuration for available models
- `templates/` - Templates for export formats
- `exports/` - Output directory for simulation results
- `main.py` - Main simulation script

## Requirements

- Python 3.9+
- Dependencies listed in requirements.txt
- API keys for the LLM providers you want to use
