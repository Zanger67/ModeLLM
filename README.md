# Model UN Simulation with LLMs

A simulation platform for testing how different Large Language Models (LLMs) perform in Model UN-style diplomatic negotiations.

## Overview

This project creates a simulated environment where LLM agents representing different countries debate, propose solutions, and vote on resolutions related to international issues. The goal is to evaluate how models perform in diplomatic contexts, focusing on their persuasiveness, reasoning, consistency, and adherence to diplomatic norms.

## Features

- Multi-agent simulation with different LLMs via API calls (OpenAI)
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
- Messages are formatted appropriately for different model providers (OpenAI)

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
git clone https://github.com/Zanger67/CS4650_NLP_GroupProject.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key_here
```

4. Run the simulation:
```bash
python3 src/main.py
```

## Configuration

- Edit `src/models/models.json` to add new models or change priority settings
- Adjust topics and characters in `src/topics.json` to create new debate scenarios
- Run with custom parameters:
  ```bash
  python3 src/main.py -t [topic_name] -m '{"USA":"gpt-3.5-turbo","China":"gpt-4o","EU":"claude-3-opus-20240229","India":"gemini-1.0-pro"}'
  ```

## Output

The simulation generates several output files in the `results` directory with a timestamp:
- `committee_history.json`: Complete record of all messages, notes, proposals, and voting
- `performance_metrics.json`: Detailed metrics for each delegate's performance
- `delegate_leaderboard.json`: Final rankings and scores for all delegates
- `dialogue_transcript.txt`: Human-readable transcript of the entire debate session

## Data Analysis Tools

The project includes utilities for analyzing simulation results:
- `src/model_evaluation.py`: Script to aggregate performance metrics across multiple simulation runs

## Project Structure

- `src/` - Core source code
  - `main.py` - Main simulation script
  - `models/` - Model implementations and management
    - `models.py` - Model class implementations for different LLM providers
    - `history.py` - Conversation tracking, metrics, and ranking systems
    - `models.json` - Configuration for available models
  - `prompts.py` - Prompt templates for different debate phases
  - `topics.json` - Debate topics and country profiles
  - `utils.py` - Utility functions for parsing and formatting
- `templates/` - Templates for export formats
- `results/` - Output directory for simulation results -> dataset for evaluation. Note that we didn't use any external dataset but created our own for benchmarking + evaluation
- `deprecated/` - Legacy code kept for reference

## Requirements

- Python 3.9+
- Dependencies listed in requirements.txt
- API keys for the LLM providers, in our case openAI
