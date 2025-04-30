from models.history import Message, Note, Proposal
from typing import Dict, List, Any


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
