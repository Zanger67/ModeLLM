import os
import time
from typing import Dict, List, Any

from programs.models import ModelManager
from programs.history import CommitteeHistory, Message, Note, Proposal

# Topic for debate
TOPIC = "Climate Change Policy: Global Carbon Tax"

# Character definitions with country and personality
CHARACTERS = {
    "USA": "You are representing the United States of America. You believe in technological innovation and market-based solutions. You are concerned about economic impacts of strict regulations but acknowledge climate change is real.",
    "China": "You are representing China. You emphasize developing nations should have different responsibilities than developed ones. You support ambitious climate goals but with flexibility for economic growth.",
    "EU": "You are representing the European Union. You are strongly pro-climate action and support aggressive targets. You want binding international agreements and favor carbon taxes.",
    "India": "You are representing India. You advocate for equitable solutions that don't hinder development. You emphasize historical responsibility of developed nations and need for climate finance."
}

# Templates for generating messages
OPENING_PROMPT = """
You are participating in a Model UN debate on {topic}. 
Your country is {country}. 

Present your opening statement outlining your position and priorities.
Be diplomatic but represent your national interests authentically.

Keep your statement under 250 words and maintain formal diplomatic language.
"""

RESPONSE_PROMPT = """
Consider the statements made by other countries so far. 

Respond to at least one point raised by another delegation and either:
1. Build upon it if you agree, or
2. Politely challenge it if you disagree.

Then, offer one specific proposal related to {topic} that aligns with your national interests.

Keep your response under 200 words and maintain formal diplomatic language.
"""

PAIRWISE_DISCUSSION_PROMPT = """
You are having a direct conversation with the delegate from {other_country} about the various proposals on {topic}.

The following proposals have been submitted:
{proposals_summary}

As the representative of {country}, engage in a focused discussion with {other_country} about these proposals.
In your response:
1. Address at least one specific aspect of {other_country}'s positions or proposals
2. Clearly state your position on their ideas
3. Suggest potential areas of collaboration or compromise
4. Be diplomatic but represent your national interests authentically

This is a bilateral conversation, so focus specifically on {other_country}'s interests and your potential alignment or disagreement.
Keep your response under 250 words and maintain formal diplomatic language.
"""

PROPOSAL_PROMPT = """
Based on the discussion so far, create a formal proposal on {topic}.

Your proposal should:
1. Have a clear title
2. Include 2-3 specific action items
3. Consider different national perspectives
4. Be politically viable

Keep your proposal under 300 words and make it specific enough to vote on.
"""

DELEGATE_RANKING_PROMPT = """
The debate on {topic} is nearing its conclusion. As the representative of {country}, you need to rank the other delegates based on their contributions, proposals, and diplomatic engagement.

Here are the other delegates:
{other_delegates}

For each delegate, consider:
1. The quality and feasibility of their proposals
2. Their willingness to collaborate and find common ground
3. Their diplomatic skill and respectful engagement
4. How well they represented their national interests

Provide a ranking of all other delegates (not including yourself) from 1 (highest) to {num_delegates} (lowest).
For each delegate, briefly explain your ranking (1-2 sentences).

Format your response as:
Rank 1: [Country Name] - [Brief explanation]
Rank 2: [Country Name] - [Brief explanation]
And so on...

Be diplomatic but honest in your assessment.
"""

VOTING_PROMPT = """
The following proposal has been submitted:

TITLE: {title}
AUTHOR: {author}
CONTENT:
{content}

As {country}, how do you vote on this proposal? Vote 'yes', 'no', or 'abstain' and provide a brief explanation for your vote.

Start your response with your vote choice (yes/no/abstain) and then provide your rationale.
"""

NOTE_PROMPT = """
Take a moment to reflect on the current state of negotiations. 
Write a private note to yourself about your strategy moving forward.

Consider:
1. Which countries are potential allies?
2. How can you achieve your goals?
3. What concerns do you need to address?

This note will not be shared with other delegates.
"""

def create_message(content: str, speaker: str, all_delegates: List[str]) -> Message:
    """Create a message from a delegate to all other delegates."""
    return Message(
        content=content,
        speaker=speaker,
        listeners=all_delegates,
        context="moderated debate"
    )

def create_note(content: str, author: str) -> Note:
    """Create a private note for a delegate."""
    return Note(
        content=content,
        author=author
    )

def create_proposal(title: str, content: str, author: str) -> Proposal:
    """Create a proposal from a delegate."""
    return Proposal(
        title=title,
        content=content,
        author=author
    )

def extract_vote(response: str) -> str:
    """Extract yes/no/abstain from the model's response."""
    response = response.lower().strip()
    
    if response.startswith("yes"):
        return "yes"
    elif response.startswith("no"):
        return "no"
    else:
        return "abstain"  # Default to abstain if unclear

def extract_proposal_parts(response: str) -> Dict[str, str]:
    """Extract title and content from a proposal response."""
    lines = response.strip().split('\n')
    
    # Try to find a title (usually at the beginning)
    title = "Untitled Proposal"
    content = response
    
    # If first line looks like a title (short, all caps, contains "PROPOSAL")
    if lines and len(lines[0]) < 100:
        if "PROPOSAL" in lines[0].upper() or lines[0].isupper() or ":" in lines[0]:
            title = lines[0].strip()
            content = '\n'.join(lines[1:]).strip()
    
    return {
        "title": title,
        "content": content
    }

def parse_model_response(response: str, prompt_type: str, delegate: str) -> Dict[str, Any]:
    """Parse the model's response based on prompt type."""
    result = {
        "raw_response": response,
        "type": prompt_type,
        "delegate": delegate
    }
    
    if prompt_type == "proposal":
        proposal_parts = extract_proposal_parts(response)
        result["title"] = proposal_parts["title"]
        result["content"] = proposal_parts["content"]
    elif prompt_type == "vote":
        result["vote"] = extract_vote(response)
    
    return result

def extract_delegate_rankings(response: str, all_delegates: List[str], ranker: str) -> Dict[str, int]:
    """
    Extract delegate rankings from the model's response.
    
    Args:
        response (str): The model's response containing rankings
        all_delegates (List[str]): List of all delegates
        ranker (str): The delegate who made the ranking (will be excluded from results)
        
    Returns:
        Dict[str, int]: Map of delegate names to their rank (1, 2, 3, etc.)
    """
    rankings = {}
    other_delegates = [d for d in all_delegates if d != ranker]
    
    # Try to extract rankings from formatted response
    lines = response.strip().split('\n')
    for line in lines:
        if line.lower().startswith("rank "):
            # Extract the rank number
            try:
                rank_part = line.split(":", 1)[0].strip()
                rank = int(rank_part.replace("Rank ", ""))
                
                # Extract the country name
                country_part = line.split(":", 1)[1].strip()
                if "-" in country_part:
                    country = country_part.split("-", 1)[0].strip()
                else:
                    country = country_part
                
                # Check if this is a valid country
                for delegate in other_delegates:
                    if delegate.lower() in country.lower():
                        rankings[delegate] = rank
                        break
            except:
                continue
    
    # If we couldn't extract all rankings, assign default ones
    missing_delegates = [d for d in other_delegates if d not in rankings]
    used_ranks = set(rankings.values())
    available_ranks = [r for r in range(1, len(other_delegates) + 1) if r not in used_ranks]
    
    for delegate in missing_delegates:
        if available_ranks:
            rankings[delegate] = available_ranks.pop(0)
        else:
            # In case something went wrong, assign a default rank
            rankings[delegate] = len(rankings) + 1
    
    return rankings

def generate_delegate_pairs(delegates: List[str]) -> List[tuple]:
    """
    Generate all possible pairs of delegates for bilateral discussions.
    
    Args:
        delegates (List[str]): List of delegate names
        
    Returns:
        List[tuple]: List of tuples containing pairs of delegates
    """
    pairs = []
    for i in range(len(delegates)):
        for j in range(i + 1, len(delegates)):
            pairs.append((delegates[i], delegates[j]))
    return pairs

def format_proposals_summary(proposals: List[Proposal]) -> str:
    """
    Format a list of proposals into a readable summary.
    
    Args:
        proposals (List[Proposal]): List of proposals
        
    Returns:
        str: Formatted summary of proposals
    """
    summary = ""
    for i, proposal in enumerate(proposals):
        summary += f"PROPOSAL {i+1} from {proposal.author}:\n"
        summary += f"TITLE: {proposal.title}\n"
        summary += f"CONTENT: {proposal.content}\n\n"
    return summary

def run_simulation():
    # Initialize model manager and committee history
    mm = ModelManager()
    history = CommitteeHistory()
    
    # Assign different Hugging Face models to different delegates
    # Using smaller models that work better with the Inference API
    models = {
        "USA": "gpt-4.1",                      # GPT-2 model for USA
        "China": "gpt-4o-2024-11-20",       # OPT-125m for China
        "EU": "o1",          # Phi-1.5 for EU 
        "India": "gpt-4"               # DistilGPT-2 for India
    }
    
    # Setup characters with their respective models
    for country, description in CHARACTERS.items():
        model_name = models.get(country, "gpt2")  # Fallback to gpt2 if not specified
        mm.add_character(country, model_name)
        history.add_character_context(country, description)
        print(f"Assigned {model_name} to {country}")
    
    all_delegates = list(CHARACTERS.keys())
    print(f"Debate Topic: {TOPIC}")
    print(f"Participating countries: {', '.join(all_delegates)}")
    print("=" * 50)
    
    # 1. Opening statements
    print("\n=== OPENING STATEMENTS ===\n")
    for delegate in all_delegates:
        prompt = OPENING_PROMPT.format(topic=TOPIC, country=delegate)
        try:
            response = mm.query_character(delegate, prompt, history)
            history.add_history(create_message(response, delegate, all_delegates))
            print(f"[{delegate}]: {response}\n")
            time.sleep(1)  # Pause between responses
        except Exception as e:
            print(f"Error getting response from {delegate}: {e}")
    
    # 2. Proposal phase - let each delegate submit a proposal
    print("\n=== PROPOSAL PHASE ===\n")
    proposals = []
    for delegate in all_delegates:
        prompt = PROPOSAL_PROMPT.format(topic=TOPIC)
        try:
            response = mm.query_character(delegate, prompt, history)
            parsed = parse_model_response(response, "proposal", delegate)
            
            # Create and add proposal
            proposal = create_proposal(parsed["title"], parsed["content"], delegate)
            history.add_proposal(proposal)
            proposals.append(proposal)
            
            print(f"[{delegate} - PROPOSAL]: {proposal.title}\n{proposal.content}\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error getting proposal from {delegate}: {e}")
    
    # 3. Pairwise discussion phase - delegates discuss each other's proposals
    print("\n=== PAIRWISE DISCUSSIONS ===\n")
    
    # Generate all possible pairs of delegates
    delegate_pairs = generate_delegate_pairs(all_delegates)
    proposals_summary = format_proposals_summary(proposals)
    
    for delegate1, delegate2 in delegate_pairs:
        print(f"\n--- Discussion between {delegate1} and {delegate2} ---\n")
        
        # Delegate 1 speaks to Delegate 2
        prompt = PAIRWISE_DISCUSSION_PROMPT.format(
            topic=TOPIC,
            country=delegate1,
            other_country=delegate2,
            proposals_summary=proposals_summary
        )
        
        try:
            response = mm.query_character(delegate1, prompt, history)
            # Set specific listeners (the other delegate) but include all as listeners
            # for the history tracking
            history.add_history(create_message(response, delegate1, all_delegates))
            print(f"[{delegate1} to {delegate2}]: {response}\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error getting response from {delegate1}: {e}")
        
        # Delegate 2 responds to Delegate 1
        prompt = PAIRWISE_DISCUSSION_PROMPT.format(
            topic=TOPIC,
            country=delegate2,
            other_country=delegate1,
            proposals_summary=proposals_summary
        )
        
        try:
            response = mm.query_character(delegate2, prompt, history)
            history.add_history(create_message(response, delegate2, all_delegates))
            print(f"[{delegate2} to {delegate1}]: {response}\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error getting response from {delegate2}: {e}")
    
    # 4. Private notes
    print("\n=== DELEGATES TAKING PRIVATE NOTES ===\n")
    for delegate in all_delegates:
        prompt = NOTE_PROMPT
        try:
            response = mm.query_character(delegate, prompt, history)
            history.add_history(create_note(response, delegate))
            print(f"[{delegate} - PRIVATE NOTE]: {response}\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error getting note from {delegate}: {e}")
    
    # 5. Voting phase - vote on each proposal
    print("\n=== VOTING PHASE ===\n")
    for proposal in proposals:
        print(f"\nVoting on: {proposal.title} (by {proposal.author})\n")
        print(f"Content: {proposal.content}\n")
        
        voting_record = history.start_vote(proposal)
        
        for delegate in all_delegates:
            if delegate == proposal.author:
                # Author automatically votes yes
                voting_record.add_vote(delegate, "yes")
                print(f"[{delegate}]: Automatically votes YES as the proposal author.")
                continue
                
            prompt = VOTING_PROMPT.format(
                title=proposal.title,
                author=proposal.author,
                content=proposal.content,
                country=delegate
            )
            
            try:
                response = mm.query_character(delegate, prompt, history)
                parsed = parse_model_response(response, "vote", delegate)
                vote = parsed["vote"]
                    
                voting_record.add_vote(delegate, vote)
                print(f"[{delegate}]: Votes {vote.upper()}")
                print(f"Explanation: {response}\n")
                time.sleep(1)
            except Exception as e:
                print(f"Error getting vote from {delegate}: {e}")
                # Default to abstain on error
                voting_record.add_vote(delegate, "abstain")
        
        # Close vote and show results
        history.close_vote(proposal.id)
        result = voting_record.get_result()
        status = "PASSED" if result["passed"] else "FAILED"
        print(f"\nVote Result: {result['yes']} Yes, {result['no']} No, {result['abstain']} Abstain")
        print(f"Proposal has {status}")
        print("=" * 50)
    
    # 6. Delegate ranking phase
    print("\n=== DELEGATE RANKING PHASE ===\n")
    
    for delegate in all_delegates:
        # Create a string of other delegates
        other_delegates_str = "\n".join([d for d in all_delegates if d != delegate])
        num_delegates = len(all_delegates) - 1  # Exclude self
        
        prompt = DELEGATE_RANKING_PROMPT.format(
            topic=TOPIC,
            country=delegate,
            other_delegates=other_delegates_str,
            num_delegates=num_delegates
        )
        
        try:
            response = mm.query_character(delegate, prompt, history)
            print(f"[{delegate} - RANKINGS]:\n{response}\n")
            
            # Parse the rankings
            rankings = extract_delegate_rankings(response, all_delegates, delegate)
            
            # Add to history
            ranking = DelegateRanking(delegate, rankings)
            history.add_delegate_ranking(ranking)
            
            # Display the parsed rankings
            print(f"Parsed rankings from {delegate}:")
            for ranked_delegate, rank in sorted(rankings.items(), key=lambda x: x[1]):
                print(f"  Rank {rank}: {ranked_delegate}")
            print()
            
            time.sleep(1)
        except Exception as e:
            print(f"Error getting rankings from {delegate}: {e}")
    
    # Create and display leaderboard
    print("\n=== DELEGATE LEADERBOARD ===\n")
    leaderboard = history.get_leaderboard()
    
    print("Final rankings based on peer assessments:")
    for entry in leaderboard:
        print(f"Rank {entry['rank']}: {entry['delegate']} - {entry['ranking_points']} points")
    print()
    
    # Export all data
    history_file = history.export_to_file()
    metrics_file = history.export_metrics()
    leaderboard_file = history.export_leaderboard()
    dialogue_file = history.export_dialogue()
    
    print("\n=== SIMULATION COMPLETE ===\n")
    print(f"History exported to: {history_file}")
    print(f"Metrics exported to: {metrics_file}")
    print(f"Leaderboard exported to: {leaderboard_file}")
    print(f"Dialogue transcript exported to: {dialogue_file}")
    
    # Display performance metrics
    print("\n=== PERFORMANCE METRICS ===\n")
    for delegate, metrics in history.get_metrics().items():
        print(metrics)
        print("-" * 40)
    
    return history

def main() -> None:
    """Run the Model UN simulation."""
    print("Starting Model UN Simulation")
    print("=" * 50)
    
    try:
        history = run_simulation()
        print("Simulation completed successfully!")
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()