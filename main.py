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

PROPOSAL_PROMPT = """
Based on the discussion so far, create a formal proposal on {topic}.

Your proposal should:
1. Have a clear title
2. Include 2-3 specific action items
3. Consider different national perspectives
4. Be politically viable

Keep your proposal under 300 words and make it specific enough to vote on.
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

def run_simulation(mock_mode=False):
    # Initialize model manager and committee history
    mm = ModelManager()
    history = CommitteeHistory()
    
    # Assign different Hugging Face models to different delegates
    # Using smaller models that work better with the Inference API
    models = {
        "USA": "gpt2",                      # GPT-2 model for USA
        "China": "gpt2",       # OPT-125m for China
        "EU": "gpt2",          # Phi-1.5 for EU 
        "India": "gpt2"               # DistilGPT-2 for India
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
    
    # Mock responses for testing without API calls
    mock_responses = {
        "opening": {
            "USA": "As the representative of the United States, I want to emphasize our commitment to addressing climate change through innovation and market-based approaches. We believe that a global carbon tax must be implemented carefully to avoid economic disruption while still reducing emissions effectively.",
            "China": "China recognizes the urgent need to address climate change as a global challenge. We support the principle of common but differentiated responsibilities. Developing nations should have flexibility in implementation timelines for any carbon tax proposal.",
            "EU": "The European Union stands firmly behind ambitious climate action. We advocate for a binding global carbon tax framework with clear emissions reduction targets. This approach has proven effective within our borders and should be expanded globally.",
            "India": "India believes that any climate policy must recognize historical responsibilities of developed nations. We support climate action that doesn't hinder the development of emerging economies and emphasize the need for climate finance and technology transfer alongside any carbon tax."
        },
        "response": {
            "USA": "I appreciate China's emphasis on differentiated responsibilities, but innovation rather than rigid timelines should be our focus. The US proposes increased investment in clean energy research shared globally, which would benefit all nations while maintaining economic growth.",
            "China": "I agree with India's point about historical responsibilities. China proposes a graduated carbon tax system with different rates for developed versus developing nations, acknowledging different starting points while working toward a common goal.",
            "EU": "While I understand the US concerns about economic impacts, the EU's experience shows that clear carbon pricing drives innovation. We propose a global carbon market with trade adjustments to ensure fair competition while reducing emissions.",
            "India": "Building on the EU's point about a global framework, India proposes that any carbon tax must include substantial technology transfer mechanisms and climate finance for developing nations to ensure equitable transition paths."
        },
        "note": {
            "USA": "China and India seem aligned on differentiated responsibilities. The EU is pushing hard for binding targets which might be too rigid. Need to emphasize innovation and flexibility while showing climate leadership. Potential ally: EU on innovation, but need to moderate their regulatory approach.",
            "China": "The US and EU have different approaches but both represent developed economies. India is a natural ally on demanding flexibility and support for developing nations. Need to avoid appearing obstructionist while protecting our growth priorities.",
            "EU": "The US shares our climate concerns but is too hesitant on binding measures. India and China are aligned against strict uniform standards. Need to emphasize economic opportunities of green transition to bring the US onboard while offering some flexibility to developing nations.",
            "India": "China is our strongest potential ally. The EU has ambitious goals but doesn't adequately address equity. The US focus on innovation could be leveraged if tied to technology transfer. Need to maintain firm position on differentiated responsibilities."
        },
        "proposal": {
            "USA": "PROPOSAL: GLOBAL CLEAN ENERGY INNOVATION COMPACT\n\n1. Establish a $100 billion annual clean energy innovation fund with contributions scaled to GDP and historical emissions\n2. Create a global carbon pricing framework with flexibility for implementation based on economic development level\n3. Develop a clean technology transfer mechanism to accelerate adoption in developing economies while respecting intellectual property",
            "China": "DIFFERENTIATED CARBON TAX FRAMEWORK\n\n1. Implement a three-tiered carbon tax system with different rates and timelines for high, middle, and low-income countries\n2. Create a technology sharing platform with joint research initiatives on clean energy\n3. Establish a climate adaptation fund prioritizing vulnerable regions",
            "EU": "GLOBAL CARBON MARKET INITIATIVE\n\n1. Create a binding international carbon market with annually decreasing caps on total emissions\n2. Implement border carbon adjustments to prevent carbon leakage while ensuring fair competition\n3. Establish an independent monitoring body to verify emissions reductions and ensure compliance",
            "India": "EQUITABLE CLIMATE TRANSITION PROPOSAL\n\n1. Implement a graduated carbon tax based on historical cumulative emissions and current development status\n2. Create a mandatory clean technology transfer framework from developed to developing nations\n3. Establish a $200 billion climate finance mechanism for renewable energy projects in developing economies"
        },
        "vote": {
            "USA": {
                "USA": "yes",
                "China": "abstain - While we appreciate the innovation focus, this proposal doesn't adequately address differentiated responsibilities for developing nations.",
                "EU": "yes - We support the innovation fund and recognize the flexible implementation approach as a positive step forward.",
                "India": "no - This proposal fails to adequately address historical responsibilities and doesn't provide sufficient guarantees for technology transfer to developing nations."
            },
            "China": {
                "USA": "abstain - While we appreciate the differentiated approach, we believe more emphasis on innovation is needed rather than rigid tax structures.",
                "China": "yes",
                "EU": "abstain - The differentiated approach has merit, but we prefer more binding emissions reduction targets.",
                "India": "yes - This proposal recognizes the different circumstances of nations and provides a fair framework for global action."
            },
            "EU": {
                "USA": "yes - While we prefer more flexibility, we support the market-based approach and monitoring mechanisms.",
                "China": "no - This proposal imposes overly strict regulations that don't adequately consider different development stages.",
                "EU": "yes",
                "India": "no - This framework doesn't sufficiently address equity concerns and places undue burden on developing economies."
            },
            "India": {
                "USA": "no - The proposal places too much emphasis on historical emissions which is backward-looking rather than focusing on future innovation.",
                "China": "yes - This approach properly recognizes historical responsibility and provides necessary support for developing nations.",
                "EU": "abstain - While we support the climate finance mechanism, we have concerns about the mandatory technology transfer framework.",
                "India": "yes"
            }
        }
    }
    
    # Opening statements
    print("\n=== OPENING STATEMENTS ===\n")
    for delegate in all_delegates:
        prompt = OPENING_PROMPT.format(topic=TOPIC, country=delegate)
        try:
            if mock_mode:
                response = mock_responses["opening"][delegate]
            else:
                response = mm.query_character(delegate, prompt, history)
                
            history.add_history(create_message(response, delegate, all_delegates))
            print(f"[{delegate}]: {response}\n")
            time.sleep(1)  # Pause between responses
        except Exception as e:
            print(f"Error getting response from {delegate}: {e}")
    
    # Responses to other delegates
    print("\n=== RESPONSES AND DISCUSSIONS ===\n")
    for delegate in all_delegates:
        prompt = RESPONSE_PROMPT.format(topic=TOPIC)
        try:
            if mock_mode:
                response = mock_responses["response"][delegate]
            else:
                response = mm.query_character(delegate, prompt, history)
                
            history.add_history(create_message(response, delegate, all_delegates))
            print(f"[{delegate}]: {response}\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error getting response from {delegate}: {e}")
    
    # Private notes
    print("\n=== DELEGATES TAKING PRIVATE NOTES ===\n")
    for delegate in all_delegates:
        prompt = NOTE_PROMPT
        try:
            if mock_mode:
                response = mock_responses["note"][delegate]
            else:
                response = mm.query_character(delegate, prompt, history)
                
            history.add_history(create_note(response, delegate))
            print(f"[{delegate} - PRIVATE NOTE]: {response}\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error getting note from {delegate}: {e}")
    
    # Proposal phase - let each delegate submit a proposal
    print("\n=== PROPOSAL PHASE ===\n")
    proposals = []
    for delegate in all_delegates:
        prompt = PROPOSAL_PROMPT.format(topic=TOPIC)
        try:
            if mock_mode:
                response = mock_responses["proposal"][delegate]
            else:
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
    
    # Voting phase - vote on each proposal
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
                if mock_mode:
                    response = mock_responses["vote"][proposal.author][delegate]
                    vote = response.split(" ")[0]  # Extract the vote part
                else:
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
    
    # Export history and metrics
    history_file = history.export_to_file()
    metrics_file = history.export_metrics()
    
    print("\n=== SIMULATION COMPLETE ===\n")
    print(f"History exported to: {history_file}")
    print(f"Metrics exported to: {metrics_file}")
    
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
        # Set mock_mode=False to use actual API calls to models
        # Set mock_mode=True if you don't have API keys for testing
        history = run_simulation(mock_mode=False)  # Set to True for testing without API keys
        print("Simulation completed successfully!")
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()