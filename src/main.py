import os
import json
import time
from datetime import datetime

from models.models import ModelManager
from models.history import CommitteeHistory, Proposal, DelegateRanking

from utils import *
from prompts import prompts


import argparse

default_topic = "climate_change"
default_models = {
    "USA": "gpt-3.5-turbo",
    "China": "gpt-3.5-turbo",
    "EU": "gpt-3.5-turbo", 
    "India": "gpt-3.5-turbo",
}

class Committee:
    def __init__(self, topic_name, topics_file="src/topics.json"):
        topics = json.loads(open(topics_file).read())
        
        self.topic: str = topics[topic_name]['topic']
        self.characters: dict[str, str] = topics[topic_name]['characters']
        
        self.opening_prompt: str = prompts["OPENING_PROMPT"]
        self.response_prompt: str = prompts["RESPONSE_PROMPT"]
        self.pairwise_discussion_prompt: str = prompts["PAIRWISE_DISCUSSION_PROMPT"]
        self.proprosal_prompt: str = prompts["PROPOSAL_PROMPT"]
        self.delegate_ranking_propmt: str = prompts["DELEGATE_RANKING_PROMPT"]
        self.voting_prompt: str = prompts["VOTING_PROMPT"]
        self.note_prompt: str = prompts["NOTE_PROMPT"]
        
        self.all_delegates = list(self.characters.keys())
        
class Context:
    def __init__(self, comm: Committee, mm: ModelManager, history: CommitteeHistory):
        self.comm = comm
        self.mm = mm
        self.history = history

class Simulation:
    def __init__(self, topic, models, output_dir="results"):
        # Initialize model manager and committee history
        self.comm: Committee = Committee(topic)
        self.mm: ModelManager = ModelManager()
        self.history: CommitteeHistory = CommitteeHistory()
        self.ctx: Context = Context(self.comm, self.mm, self.history)
        
        self.output_dir = output_dir
        
        # Assign different Hugging Face models to different delegates
        # Using smaller models that work better with the Inference API
        self.models = models
        
        if len(models) != len(self.comm.characters):
            raise ValueError
        
        # Setup characters with their respective models
        for country, description in self.comm.characters.items():
            model_name = models.get(country, "gpt2")  # Fallback to gpt2 if not specified
            self.mm.add_character(country, model_name)
            self.history.add_character_context(country, description)
            self.history.add_model_name(country, model_name)
            print(f"Assigned {model_name} to {country}")
            
            all_delegates = list(self.comm.characters.keys())
            print(f"Debate Topic: {self.comm.topic}")
            print(f"Participating countries: {', '.join(all_delegates)}")
            print("=" * 50)
        
        
    def run(self):
        '''
        Runs simulation
        '''
        
        all_delegates = list(self.comm.characters.keys())
        print(f"Debate Topic: {self.comm.topic}")
        print(f"Participating countries: {', '.join(all_delegates)}")
        print("=" * 50)
        
        # 1. opening statement
        self.opening_statement()
        
        # 2. Private notes - MOVED UP before proposals to use notes in discussion
        self.private_notes()
        
        # 3. Proposal phase - let each delegate submit a proposal
        proposals = self.proposal_phase()
        
        # 4. Pairwise discussion phase - delegates discuss each other's proposals
        self.pairwise_dicussion_phase(proposals)
        
        # 5. Voting phase - vote on each proposal
        self.voting_phase(proposals)
        
        # 6. Delegate ranking phase
        self.rank_delegates()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(self.output_dir, timestamp)
        os.makedirs(results_dir, exist_ok=True)
            
        # Export all data
        history_file = self.history.export_to_file(os.path.join(results_dir, f"committee_history.json"))
        leaderboard_file = self.history.export_leaderboard(os.path.join(results_dir, f"delegate_leaderboards.json"))
        dialogue_file = self.history.export_dialogue(os.path.join(results_dir, f"dialogue_transcripts.txt"))
        metrics_file = self.history.export_metrics(os.path.join(results_dir, f"performance_metrics.json"))
        
        print("\n=== SIMULATION COMPLETE ===\n")
        print(f"History exported to: {history_file}")
        print(f"Metrics exported to: {metrics_file}")
        print(f"Leaderboard exported to: {leaderboard_file}")
        print(f"Dialogue transcript exported to: {dialogue_file}")
        
        # Display performance metrics
        print("\n=== PERFORMANCE METRICS ===\n")
        for delegate, metrics in self.history.get_metrics().items():
            print(metrics)
            print("-" * 40)
        
        return self.history
    
    def opening_statement(self):
        # 1. Opening statements
        print("\n=== OPENING STATEMENTS ===\n")
        for delegate in self.comm.all_delegates:
            prompt = self.comm.opening_prompt.format(topic=self.comm.topic, country=delegate)
            try:
                response = self.mm.query_character(delegate, prompt, self.history)
                self.history.add_history(create_message(response, delegate, self.comm.all_delegates))
                print(f"[{delegate}]: {response}\n")
                time.sleep(1)  # Pause between responses
            except Exception as e:
                print(f"Error getting response from {delegate}: {e}")
                
    def private_notes(self):
        # 2. Private notes - MOVED UP before proposals to use notes in discussion
        print("\n=== DELEGATES TAKING PRIVATE NOTES ===\n")
        for delegate in self.comm.all_delegates:
            prompt = self.comm.note_prompt
            try:
                response = self.mm.query_character(delegate, prompt, self.history)
                self.history.add_history(create_note(response, delegate))
                print(f"[{delegate} - PRIVATE NOTE]: {response}\n")
                time.sleep(1)
            except Exception as e:
                print(f"Error getting note from {delegate}: {e}")
                    
    def proposal_phase(self):
        # 3. Proposal phase - let each delegate submit a proposal
        print("\n=== PROPOSAL PHASE ===\n")
        proposals: list[Proposal] = []
        for delegate in self.comm.all_delegates:
            prompt = self.comm.proprosal_prompt.format(topic=self.comm.topic)
            try:
                response = self.mm.query_character(delegate, prompt, self.history)
                parsed = parse_model_response(response, "proposal", delegate)
                
                # Create and add proposal
                proposal: Proposal = create_proposal(parsed["title"], parsed["content"], delegate)
                self.history.add_proposal(proposal)
                proposals.append(proposal)
                
                print(f"[{delegate} - PROPOSAL]: {proposal.title}\n{proposal.content}\n")
                time.sleep(1)
            except Exception as e:
                print(f"Error getting proposal from {delegate}: {e}")
        
        return proposals

    def pairwise_dicussion_phase(self, proposals):
        print("\n=== PAIRWISE DISCUSSIONS ===\n")
        
        # Generate all possible pairs of delegates
        delegate_pairs = generate_delegate_pairs(self.comm.all_delegates)
        proposals_summary = format_proposals_summary(proposals)
        
        for delegate1, delegate2 in delegate_pairs:
            print(f"\n--- Discussion between {delegate1} and {delegate2} ---\n")
            
            # Delegate 1 speaks to Delegate 2
            prompt = self.comm.pairwise_discussion_prompt.format(
                topic=self.comm.topic,
                country=delegate1,
                other_country=delegate2,
                proposals_summary=proposals_summary
            )
            
            try:
                response = self.mm.query_character(delegate1, prompt, self.history)
                # Set specific listeners (the other delegate) but include all as listeners
                # for the history tracking
                self.history.add_history(create_message(response, delegate1, self.comm.all_delegates))
                print(f"[{delegate1} to {delegate2}]: {response}\n")
                time.sleep(1)
            except Exception as e:
                print(f"Error getting response from {delegate1}: {e}")
            
            # Delegate 2 responds to Delegate 1
            prompt = self.comm.pairwise_discussion_prompt.format(
                topic=self.comm.topic,
                country=delegate2,
                other_country=delegate1,
                proposals_summary=proposals_summary
            )
            
            try:
                response = self.mm.query_character(delegate2, prompt, self.history)
                self.history.add_history(create_message(response, delegate2, self.comm.all_delegates))
                print(f"[{delegate2} to {delegate1}]: {response}\n")
                time.sleep(1)
            except Exception as e:
                print(f"Error getting response from {delegate2}: {e}")
        
    def voting_phase(self, proposals: list[Proposal]):
        self.comm: Committee
        self.mm: ModelManager
        self.history: CommitteeHistory
        
        print("\n=== VOTING PHASE ===\n")
        for proposal in proposals:
            print(f"\nVoting on: {proposal.title} (by {proposal.author})\n")
            print(f"Content: {proposal.content}\n")
            
            voting_record = self.history.start_vote(proposal)
            
            for delegate in self.comm.all_delegates:
                if delegate == proposal.author:
                    # Author automatically votes yes
                    voting_record.add_vote(delegate, "yes")
                    print(f"[{delegate}]: Automatically votes YES as the proposal author.")
                    continue
                    
                prompt = self.comm.voting_prompt.format(
                    title=proposal.title,
                    author=proposal.author,
                    content=proposal.content,
                    country=delegate
                )
                
                try:
                    response = self.mm.query_character(delegate, prompt, self.history)
                    parsed = parse_model_response(response, "vote", delegate)
                    vote: str = parsed["vote"]
                        
                    voting_record.add_vote(delegate, vote)
                    # Ensure the vote is recorded in the history's record_vote method
                    self.history.record_vote(delegate, proposal.id, vote)
                    print(f"[{delegate}]: Votes {vote.upper()}")
                    print(f"Explanation: {response}\n")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error getting vote from {delegate}: {e}")
                    # Default to abstain on error
                    voting_record.add_vote(delegate, "abstain")
                    self.history.record_vote(delegate, proposal.id, "abstain")
            
            # Close vote and show results
            self.history.close_vote(proposal.id)
            result = voting_record.get_result()
            status = "PASSED" if result["passed"] else "FAILED"
            print(f"\nVote Result: {result['yes']} Yes, {result['no']} No, {result['abstain']} Abstain")
            print(f"Proposal has {status}")
            print("=" * 50)
        
    def rank_delegates(self):
        self.comm: Committee
        self.mm: ModelManager
        self.history: CommitteeHistory
        
        print("\n=== DELEGATE RANKING PHASE ===\n")
        
        for delegate in self.comm.all_delegates:
            # Create a string of other delegates
            other_delegates_str = "\n".join([d for d in self.comm.all_delegates if d != delegate])
            num_delegates = len(self.comm.all_delegates) - 1  # Exclude self
            
            prompt = self.comm.delegate_ranking_propmt.format(
                topic=self.comm.topic,
                country=delegate,
                other_delegates=other_delegates_str,
                num_delegates=num_delegates
            )
            
            try:
                response = self.mm.query_character(delegate, prompt, self.history)
                print(f"[{delegate} - RANKINGS]:\n{response}\n")
                
                # Parse the rankings
                rankings = extract_delegate_rankings(response, self.comm.all_delegates, delegate)
                
                # Add to history
                ranking = DelegateRanking(delegate, rankings)
                self.history.add_delegate_ranking(ranking)
                
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
        leaderboard = self.history.get_leaderboard()
        
        print("Final rankings based on peer assessments:")
        for entry in leaderboard:
            print(f"Rank {entry['rank']}: {entry['delegate']} - {entry['ranking_points']} points")
        print()
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Model UN Simulation")
    parser.add_argument("-t", "--topic", type=str, help="topic for the Model UN simulation", default=default_topic)
    parser.add_argument("-m", "--models", type=json.loads, help="model for the Model UN simulation", default=default_models,)
    args = parser.parse_args()

    """Run the Model UN simulation."""
    print("Starting Model UN Simulation")
    print("=" * 50)
    sim = Simulation(args.topic, args.models)
    
    try:
        history = sim.run()
        print("Simulation completed successfully!")
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()