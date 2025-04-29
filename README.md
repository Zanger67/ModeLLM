# Model UN Simulation with LLMs

A simulation platform for testing how different Large Language Models (LLMs) perform in Model UN-style diplomatic negotiations.

## Overview

This project creates a simulated environment where LLM agents representing different countries debate, propose solutions, and vote on resolutions related to international issues. The goal is to evaluate how models perform in diplomatic contexts, focusing on their persuasiveness, reasoning, consistency, and adherence to diplomatic norms.

## Features

- Multi-agent simulation with different LLMs via API calls (OpenAI, Hugging Face, Replicate)
- Realistic parliamentary procedure with structured debate phases:
  - Opening statements
  - Private strategic notes
  - Proposal submissions
  - Pairwise bilateral discussions about proposals
  - Voting on proposals
  - Delegate peer assessment and ranking
- Rich context memory system ensuring models maintain awareness of all prior exchanges
- Performance metrics tracking (messages, proposals, votes, peer rankings)
- Comprehensive leaderboard system with point-based rankings
- Export functionality for conversation history, metrics, and human-readable transcripts
- Voting mechanism for proposals with transparent results tracking
- Mock mode for testing without API keys

## Debate Structure

The simulation follows a formal parliamentary procedure:

1. **Opening Statements**: Each delegate presents their country's position and priorities
2. **Private Notes**: Delegates record private strategic notes (not shared directly with others but used to guide their own future decisions)
3. **Proposal Phase**: Delegates submit formal proposals addressing the debate topic
4. **Pairwise Discussions**: Delegates engage in bilateral conversations with each other discussing the submitted proposals
5. **Voting Phase**: Delegates vote on each proposal (yes/no/abstain) with explanations
6. **Delegate Ranking**: Each delegate ranks their peers based on contributions and diplomacy
7. **Leaderboard Generation**: Final rankings are calculated based on peer assessments

## Context Memory Management

The simulation employs a sophisticated context memory system:

- Each model maintains awareness of all prior statements, proposals, and voting history
- Private notes are included in context for the authoring delegate only
- Character personalities and national interests guide responses consistently
- Prompts for each phase build upon the accumulated context
- Messages are formatted appropriately for different model providers (OpenAI, Hugging Face)

This context-rich approach ensures delegates maintain consistent positions, can reference previous statements, and develop more coherent diplomatic strategies.

## Metrics System

The simulation tracks comprehensive performance metrics:

- **Messages**: Sent and received by each delegate
- **Proposals**: Created and passed
- **Votes**: Cast on proposals
- **Ranking Points**: Awarded based on peer assessments (higher ranks get more points)
- **Reputation Score**: Dynamic score affected by diplomatic behavior and proposal success

The final leaderboard ranks delegates based primarily on peer assessment points, with reputation score as a tiebreaker.

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
python3 main.py
```

## Configuration

- Modify `main.py` to change the debate topic, characters, or prompts
- Edit `models.json` to add new models or change priority settings
- Adjust `CHARACTERS` dictionary in `main.py` to change which countries participate

## Output

The simulation generates several output files in the `exports` directory:
- JSON history files with all messages, notes, proposals, and voting records
- Performance metrics tracking each agent's effectiveness
- Leaderboard rankings based on peer assessments
- Human-readable dialogue transcript that includes all exchanges, private notes, proposals, and voting results

## Adding New Models

To add support for a new LLM provider:
1. Create a new class that inherits from the `Model` abstract base class
2. Implement the required methods (`_load_model()`, `query()`, `generate_payload()`)
3. Update the `_load_model_options()` method in `ModelManager` to include your new class
4. Add models to the `models.json` configuration file

## Project Structure

- `programs/` - Core modules and classes
  - `models.py` - Model implementations for different LLM providers
  - `history.py` - Conversation tracking, metrics, and ranking systems
  - `models.json` - Configuration for available models
- `templates/` - Templates for export formats
- `exports/` - Output directory for simulation results
- `main.py` - Main simulation script

## Requirements

- Python 3.9+
- Dependencies listed in requirements.txt
- API keys for the LLM providers you want to use
