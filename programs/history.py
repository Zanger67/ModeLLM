from dataclasses import dataclass
from typing import Any, Dict, List, Set
from datetime import datetime
from dateutil.parser import parse
from icecream import ic
import os

def _convert_datetime(dt: str | datetime | None) -> str :
    '''
    Convert a datetime object to a string.
    
    Args:
        dt (str | datetime): Datetime object or string to be converted.
    
    Returns:
        str: Converted datetime string.
    '''
    if dt is None :
        dt = datetime.now()
        
    if isinstance(dt, str) :
        try :
            dt = parse(dt)
        except ValueError as ve :
            print(f"Error parsing datetime string: {ve}. Defaulting to datetime.now()")
            dt = None
    
    if isinstance(dt, datetime) :
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        
    return dt

@dataclass
class Message:
    '''
    Class to represent a single message in the chat history.
    
    Attributes:
        content (str):          Content of the message.
        speaker (str):          Speaker of the message.
        listeners (List[str]):  List of listeners for the message.
        context (str):          Context of the message.
        word_cap (int):         Word cap for the message. Default is zero indicating no limit.
    '''
    
    time:      str
    content:   str
    speakers:  List[str]    # The overhead of sets likely wouldn't outweigh 
    listeners: List[str]    # the benefits of using a list in this situation
    context:   str
    word_cap:  int = 0

    def __init__(self, 
                 content: str,
                 speaker: Set[str] | List[str] | str,
                 listeners: Set[str] | List[str] | str = None,
                 time: str | datetime | None = None,
                 context: str = "",
                 word_cap: int = 0) :
        
        if speaker is None :
            raise ValueError("Speaker cannot be None.")
        if listeners is None :
            ic("Listeners is None. Should be NOTE not Message.")
            ic(speaker, listeners, content, word_cap, time)
        
        # Simulates speaking time cutoffs
        split_content = content.split()
        
        self.content   = content if len(split_content) <= word_cap or word_cap == 0 \
                         else " ".join(split_content[:word_cap])
                         
        # Sets due to potential joint speeches being implemented in the future
        self.speakers  = list(speaker if isinstance(speaker, (list, set)) else [speaker])
        self.listeners = list(listeners) if isinstance(listeners, (list, set)) else \
                         [listeners] if listeners is not None \
                         else None

        # Metadata
        self.time      = _convert_datetime(time)
        self.context   = context
        self.word_cap  = word_cap
        
    
    def add_listeners(self, listeners: str | List[str] | Set[str]) -> None :
        '''
        Add a listener to the message.
        
        Args:
            listeners: Listener to be added.
        '''
        if isinstance(listeners, str) :
            listeners = [x.trim() for x in listeners.split(",")]
            
        if isinstance(listeners, (list, set)) :
            self.listeners.extend(list(listeners))
        else :
            raise ValueError("Listeners must be a string, list, or set.")
    
    def add_speakers(self, speakers: str | Set[str] | List[str]) -> None :
        '''
        Add speakers to the message.
        
        Args:
            speakers (str | Set[str] | List[str]): Speakers to be added.
        '''
        if isinstance(speakers, str) :
            speakers = [x.strip() for x in speakers.split(",")]
            
        if isinstance(speakers, (list, set)) :
            self.speakers.extend(list(speakers))
        else :
            raise ValueError("Speakers must be a string, list, or set.")



@dataclass
class Note:
    '''
    Class to represent a note left by the agent.
    '''
    
    time: str
    author: str
    content: str
    word_cap: int = 0
    
    def __init__(self,
                 content: str,
                 author: str,
                 time: str | datetime | None = None,
                 word_cap: int = 0) :
        split_content = content.split()
        self.content  = content if len(split_content) <= word_cap or word_cap == 0 \
                        else " ".join(split_content[:word_cap])

        self.author   = author
        self.time     = _convert_datetime(time)
        self.word_cap = word_cap
    
    
    
    

@dataclass
class Proposal:
    """
    Class to represent a proposal that delegates can vote on.
    """
    id: str
    title: str
    content: str
    author: str
    time: str
    
    def __init__(self,
                title: str,
                content: str,
                author: str,
                time: str | datetime | None = None,
                id: str = None):
        
        self.title = title
        self.content = content
        self.author = author
        self.time = _convert_datetime(time)
        
        # Generate a simple ID if none provided
        if id is None:
            import uuid
            self.id = str(uuid.uuid4())[:8]
        else:
            self.id = id
            
    def __str__(self):
        return f"Proposal {self.id}: {self.title} (by {self.author})"


@dataclass
class VotingRecord:
    """
    Class to record votes on proposals.
    """
    proposal: Proposal
    votes: Dict[str, str]  # {character_name: vote (yes/no/abstain)}
    time_opened: str
    time_closed: str = None
    
    def __init__(self,
                proposal: Proposal,
                time_opened: str | datetime | None = None):
        
        self.proposal = proposal
        self.votes = {}
        self.time_opened = _convert_datetime(time_opened)
        self.time_closed = None
        
    def add_vote(self, character: str, vote: str):
        """
        Record a vote from a character.
        
        Args:
            character (str): The character casting the vote
            vote (str): The vote cast ('yes', 'no', 'abstain')
        """
        if vote.lower() not in ['yes', 'no', 'abstain']:
            raise ValueError(f"Invalid vote: {vote}. Must be 'yes', 'no', or 'abstain'")
        
        self.votes[character] = vote.lower()
        
    def close_voting(self, time: str | datetime | None = None):
        """Mark the voting as closed."""
        self.time_closed = _convert_datetime(time)
        
    def get_result(self) -> Dict[str, Any]:
        """Get the results of the vote."""
        yes_votes = sum(1 for v in self.votes.values() if v == 'yes')
        no_votes = sum(1 for v in self.votes.values() if v == 'no')
        abstain_votes = sum(1 for v in self.votes.values() if v == 'abstain')
        total_votes = len(self.votes)
        
        passed = yes_votes > no_votes
        
        return {
            'proposal_id': self.proposal.id,
            'proposal_title': self.proposal.title,
            'yes': yes_votes,
            'no': no_votes,
            'abstain': abstain_votes,
            'total': total_votes,
            'passed': passed
        }
        
    def __str__(self):
        result = self.get_result()
        status = "PASSED" if result['passed'] else "FAILED"
        return f"Vote on {self.proposal.title}: {result['yes']} Yes, {result['no']} No, {result['abstain']} Abstain - {status}"

@dataclass
class PerformanceMetrics:
    """
    Class to track metrics for evaluating agent performance.
    """
    character_name: str
    messages_sent: int = 0
    messages_received: int = 0
    notes_created: int = 0
    proposals_created: int = 0
    votes_cast: int = 0
    proposals_passed: int = 0
    reputation_score: float = 0.0  # 0-10 scale
    ranking_points: int = 0  # Points from delegate rankings
    
    def __init__(self, character_name: str):
        self.character_name = character_name
        self.messages_sent = 0
        self.messages_received = 0
        self.notes_created = 0
        self.proposals_created = 0
        self.votes_cast = 0
        self.proposals_passed = 0
        self.reputation_score = 5.0  # Neutral starting point
        self.ranking_points = 0
        
    def update_reputation(self, amount: float):
        """Adjust the reputation score by the given amount."""
        self.reputation_score += amount
        # Clamp between 0 and 10
        self.reputation_score = max(0, min(10, self.reputation_score))
        
    def add_ranking_points(self, points: int):
        """Add points from delegate rankings."""
        self.ranking_points += points
        
    def __str__(self):
        return (f"Metrics for {self.character_name}:\n"
                f"- Messages sent: {self.messages_sent}\n"
                f"- Messages received: {self.messages_received}\n"
                f"- Notes created: {self.notes_created}\n"
                f"- Proposals created: {self.proposals_created}\n"
                f"- Votes cast: {self.votes_cast}\n"
                f"- Proposals passed: {self.proposals_passed}\n"
                f"- Ranking points: {self.ranking_points}\n"
                f"- Reputation score: {self.reputation_score:.1f}/10.0")

@dataclass
class DelegateRanking:
    """
    Class to represent a delegate's ranking of other delegates.
    """
    ranker: str  # The delegate making the ranking
    rankings: Dict[str, int]  # Dictionary mapping delegate names to their rank (1, 2, 3, etc.)
    time: str
    
    def __init__(self, 
                 ranker: str,
                 rankings: Dict[str, int],
                 time: str | datetime | None = None):
        self.ranker = ranker
        self.rankings = rankings
        self.time = _convert_datetime(time)
        
    def get_points_map(self) -> Dict[str, int]:
        """
        Convert rankings to points, where highest rank gets most points.
        E.g., in a committee with 4 delegates, 1st place gets 3 points, 2nd gets 2, 3rd gets 1.
        """
        points = {}
        max_points = len(self.rankings)
        
        for delegate, rank in self.rankings.items():
            # Convert rank to points (highest rank = most points)
            points[delegate] = max_points - (rank - 1)
            
        return points
        
    def __str__(self):
        ranking_str = ", ".join([f"{delegate}: Rank {rank}" for delegate, rank in self.rankings.items()])
        return f"{self.ranker}'s rankings: {ranking_str}"

@dataclass
class CommitteeHistory :
    '''
    Class to keep track of all chat histories, logs, notes left 
    from a "agent" to itself, etc.
    '''
    
    history: list                   # Chat history
    notes:  Dict[str, List[Note]]   # Notes left by the agent
    
    character_contexts: Dict[str, str] # {character name: context about character} 
                                       # E.g. context="You are a warlord pirate from the 1700s 
                                       #               in the Mediterranean."
    # msg_id: int = 0               # Message ID for the next message - USE INDEX IN SELF.HISTORY
    
    
    def __init__(self) :
        self.history = []                           # Message history in chat order
        self.notes = {}      # {author: [Note, Note, ...]}
        self.character_contexts = {}                # Character descriptions
        self.proposals = []                         # List of proposals
        self.voting_records = []                    # List of voting records
        self.metrics = {}                           # {character_name: PerformanceMetrics}
        self.delegate_rankings = []                 # List of delegate rankings
    
    def _add_note(self, note: Note) -> None :
        '''
        Add a note to the notes dictionary.
        
        Args:
            note (Note): Note to be added.
        '''
        if note.author not in self.notes :
            self.notes[note.author] = []
        
        self.notes[note.author].append(note)
        
        # Update metrics
        if note.author not in self.metrics:
            self.metrics[note.author] = PerformanceMetrics(note.author)
        self.metrics[note.author].notes_created += 1
    
    def add_character_context(self,
                              character_name: str,
                              context: str) -> None :
        '''
        Add a character context to the history.
        
        Args:
            character_name (str): Name of the character.
            context (str): Context about the character.
        '''
        self.character_contexts[character_name] = context
    
    def get_character_context(self, character_name: str) -> str :
        '''
        Get the character context for a specific character.
        
        Args:
            character_name (str): Name of the character.
        
        Returns:
            str: Context about the character.
        '''
        return self.character_contexts.get(character_name, "")
    
    # TODO: Think how to do this. Should this be a description that's public
    #       like with a background guide or should it be an agent's stated intro?
    #       I'm leaning to having a hardcoded "intro speech" part in the beginning
    #       of moderation.
    def get_character_contexts_all(self) -> Dict[str, str] :
        '''
        Get all character contexts.
        
        Returns:
            Dict[str, str]: Dictionary of all character contexts.
        '''
        return self.character_contexts
    
    def _add_message(self, msg: Message) -> None :
        '''
        Add a message to the history.
        
        Args:
            msg (Message): Message to be added.
        '''
        self.history.append(msg)
        
        # Update metrics
        for speaker in msg.speakers:
            if speaker not in self.metrics:
                self.metrics[speaker] = PerformanceMetrics(speaker)
            self.metrics[speaker].messages_sent += 1
            
        for listener in msg.listeners:
            if listener not in self.metrics:
                self.metrics[listener] = PerformanceMetrics(listener)
            self.metrics[listener].messages_received += 1
    
    def add_history(self, 
                    hist: Message | Note | List[Message | Note]) -> None :
        '''
        Add a message to the chat history.
        '''
        
        if hist is None :
            raise ValueError("History cannot be None.")
        if isinstance(hist, str) :
            raise ValueError("History must be a Message or Note.")
        
        if isinstance(hist, list) :
            for x in hist :
                self.add_history(x)
        elif isinstance(hist, Message) :
            self._add_message(hist)
        elif isinstance(hist, Note) :
            self._add_note(hist)
        else :
            raise ValueError("History must be a Message, Note, or list of Messages and Notes.")
    
    def get_chat_history(self, listener: str) -> List[Message] :
        '''
        Get the chat history for a specific listener.
        
        Args:
            listener (str): Listener to get the chat history for.
        
        Returns:
            List[Message]: List of messages for the specified listener.
        '''
        return [x for x in self.history if listener in x.listeners or listener in x.speakers]
    
    def get_past_speeches(self, speaker: str) -> List[Message] :
        '''
        Get the past speeches for a specific speaker.
        
        Args:
            speaker (str): Speaker to get the past speeches for.
        
        Returns:
            List[Message]: List of past speeches for the specified speaker.
        '''
        return [x for x in self.history if speaker in x.speakers]
    
    def get_notes(self, author: str) -> List[Note] :
        '''
        Get the notes left by a specific author.
        
        Args:
            author (str): Author to get the notes for.
        
        Returns:
            List[Note]: List of notes for the specified author.
        '''
        return self.notes.get(author, [])
    
    def get_all(self) -> Dict[str, Any] :
        '''
        Get all chat histories, notes, etc.
        '''
        return {
            "history": self.history,
            "notes":   self.notes
        }
        
    def export_to_file(self, output_file: str = None) -> str:
        """
        Export the committee history to a JSON file in the template format.
        
        Args:
            output_file (str): Path to save the JSON file. If None, a default filename with timestamp will be used.
            
        Returns:
            str: Path to the saved file
        """
        output = []
        
        # Convert regular messages
        for i, msg in enumerate(self.history):
            entry = {
                "time": msg.time,
                "type": "message",
                "id": str(i + 1),
                "speaker": ", ".join(msg.speakers),
                "listeners": msg.listeners,
                "content": msg.content,
                "context": msg.context
            }
            if msg.word_cap > 0:
                entry["word_cap"] = msg.word_cap
            output.append(entry)
        
        # Convert notes
        note_id = len(self.history) + 1
        for author, notes in self.notes.items():
            for note in notes:
                entry = {
                    "time": note.time,
                    "type": "personal note",
                    "id": str(note_id),
                    "author": note.author,
                    "content": note.content
                }
                if note.word_cap > 0:
                    entry["word_cap"] = note.word_cap
                output.append(entry)
                note_id += 1
        
        # Sort by time
        output.sort(key=lambda x: x["time"])
        
        # Generate a default filename if none provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
            
            # Create exports directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"committee_history_{timestamp}.json")
        
        # Convert to JSON and save
        import json
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=4)
        
        print(f"Exported committee history to {output_file}")
        return output_file

    def add_proposal(self, proposal: Proposal) -> None:
        """
        Add a proposal to the committee.
        
        Args:
            proposal (Proposal): The proposal to add.
        """
        self.proposals.append(proposal)
        
        # Update metrics
        if proposal.author not in self.metrics:
            self.metrics[proposal.author] = PerformanceMetrics(proposal.author)
        self.metrics[proposal.author].proposals_created += 1
        
    def get_proposals(self) -> List[Proposal]:
        """Get all proposals."""
        return self.proposals
        
    def get_proposal_by_id(self, proposal_id: str) -> Proposal:
        """Get a proposal by its ID."""
        for proposal in self.proposals:
            if proposal.id == proposal_id:
                return proposal
        return None
        
    def start_vote(self, proposal: Proposal) -> VotingRecord:
        """
        Start a vote on a proposal.
        
        Args:
            proposal (Proposal): The proposal to vote on.
            
        Returns:
            VotingRecord: The voting record.
        """
        voting_record = VotingRecord(proposal)
        self.voting_records.append(voting_record)
        return voting_record
        
    def close_vote(self, proposal_id: str) -> VotingRecord:
        """
        Close voting on a proposal.
        
        Args:
            proposal_id (str): The ID of the proposal to close voting on.
            
        Returns:
            VotingRecord: The voting record.
        """
        for voting_record in self.voting_records:
            if voting_record.proposal.id == proposal_id and voting_record.time_closed is None:
                voting_record.close_voting()
                
                # Update metrics for proposal author if it passed
                result = voting_record.get_result()
                if result['passed']:
                    author = voting_record.proposal.author
                    if author in self.metrics:
                        self.metrics[author].proposals_passed += 1
                        # Give a small reputation boost for passed proposals
                        self.metrics[author].update_reputation(0.5)
                
                return voting_record
        return None
        
    def get_open_votes(self) -> List[VotingRecord]:
        """Get all open votes."""
        return [vr for vr in self.voting_records if vr.time_closed is None]
        
    def get_all_voting_records(self) -> List[VotingRecord]:
        """Get all voting records."""
        return self.voting_records

    def record_vote(self, character: str, proposal_id: str, vote: str) -> bool:
        """
        Record a vote from a character.
        
        Args:
            character (str): The character casting the vote
            proposal_id (str): The ID of the proposal
            vote (str): The vote cast ('yes', 'no', 'abstain')
            
        Returns:
            bool: Whether the vote was recorded successfully
        """
        for voting_record in self.get_open_votes():
            if voting_record.proposal.id == proposal_id:
                voting_record.add_vote(character, vote)
                
                # Update metrics
                if character not in self.metrics:
                    self.metrics[character] = PerformanceMetrics(character)
                self.metrics[character].votes_cast += 1
                
                return True
        return False
    
    def get_metrics(self, character_name: str = None) -> Dict[str, PerformanceMetrics]:
        """
        Get performance metrics.
        
        Args:
            character_name (str, optional): The character to get metrics for.
                If None, returns metrics for all characters.
                
        Returns:
            Dict[str, PerformanceMetrics]: The metrics.
        """
        if character_name:
            if character_name not in self.metrics:
                return None
            return self.metrics[character_name]
        return self.metrics
    
    def export_metrics(self, output_file: str = None) -> str:
        """
        Export performance metrics to a JSON file.
        
        Args:
            output_file (str, optional): The file to save to.
                If None, a default filename with timestamp will be used.
                
        Returns:
            str: The path to the saved file.
        """
        metrics_data = {}
        for name, metrics in self.metrics.items():
            metrics_data[name] = {
                "messages_sent": metrics.messages_sent,
                "messages_received": metrics.messages_received,
                "notes_created": metrics.notes_created,
                "proposals_created": metrics.proposals_created,
                "votes_cast": metrics.votes_cast,
                "proposals_passed": metrics.proposals_passed,
                "ranking_points": metrics.ranking_points,
                "reputation_score": metrics.reputation_score
            }
        
        # Generate a default filename if none provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
            
            # Create exports directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"performance_metrics_{timestamp}.json")
        
        # Convert to JSON and save
        import json
        with open(output_file, 'w') as f:
            json.dump(metrics_data, f, indent=4)
        
        print(f"Exported performance metrics to {output_file}")
        return output_file
        
    def export_dialogue(self, output_file: str = None) -> str:
        """
        Export a human-readable dialogue transcript of the debate.
        
        This creates a text file that focuses on the dialogue between characters,
        formatted in a readable way for humans to follow the conversation flow.
        
        Args:
            output_file (str, optional): The file to save to.
                If None, a default filename with timestamp will be used.
                
        Returns:
            str: The path to the saved file.
        """
        # Generate a default filename if none provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
            
            # Create exports directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"dialogue_transcript_{timestamp}.txt")
        
        # Sort all history entries by time
        all_entries = []
        
        # Add messages
        for i, msg in enumerate(self.history):
            # Detect the debate phase based on message position
            # First batch of messages are opening statements
            phase = ""
            if i < len(self.character_contexts):  # First round - opening statements
                phase = "opening"
            elif not any(isinstance(item, Proposal) for item in all_entries):  # Before any proposals
                phase = "response"
                
            all_entries.append({
                "time": msg.time,
                "type": "message",
                "speaker": ", ".join(msg.speakers),
                "content": msg.content,
                "context": msg.context,
                "phase": phase,
                "index": i
            })
        
        # Add notes (private thoughts)
        for author, notes_list in self.notes.items():
            for note in notes_list:
                all_entries.append({
                    "time": note.time,
                    "type": "private_note",
                    "author": note.author,
                    "content": note.content
                })
        
        # Add proposals
        for proposal in self.proposals:
            all_entries.append({
                "time": proposal.time,
                "type": "proposal",
                "speaker": proposal.author,
                "title": proposal.title,
                "content": proposal.content
            })
        
        # Add voting records
        for vote_record in self.voting_records:
            if vote_record.time_closed:  # Only include completed votes
                result = vote_record.get_result()
                status = "PASSED" if result["passed"] else "FAILED"
                all_entries.append({
                    "time": vote_record.time_closed,
                    "type": "vote_result",
                    "proposal_title": vote_record.proposal.title,
                    "proposal_author": vote_record.proposal.author,
                    "yes": result["yes"],
                    "no": result["no"],
                    "abstain": result["abstain"],
                    "status": status
                })
        
        # Add delegate rankings
        for ranking in self.delegate_rankings:
            all_entries.append({
                "time": ranking.time,
                "type": "delegate_ranking",
                "ranker": ranking.ranker,
                "rankings": ranking.rankings
            })
        
        # Sort all entries by time
        all_entries.sort(key=lambda x: x["time"])
        
        # Write the dialogue transcript
        with open(output_file, 'w') as f:
            # Write header with the debate topic
            topic = "UN Model Debate"
            for msg in self.history:
                if msg.context and "topic" in msg.context.lower():
                    topic = msg.context.split(":", 1)[1].strip() if ":" in msg.context else msg.context
                    break
            
            f.write(f"DEBATE TRANSCRIPT: {topic}\n")
            f.write(f"================\n\n")
            
            # Write participant information
            f.write("PARTICIPANTS:\n")
            for country, description in self.character_contexts.items():
                f.write(f"- {country}\n")
            f.write("\n\n")
            
            current_phase = None
            message_count = 0
            
            for entry in all_entries:
                entry_type = entry["type"]
                
                # Add phase headers based on message type and order
                if entry_type == "message":
                    message_count += 1
                    
                    # First set of messages are opening statements
                    if message_count <= len(self.character_contexts) and current_phase != "opening":
                        f.write("\n\n=== OPENING STATEMENTS ===\n\n")
                        current_phase = "opening"
                    # Next set of messages are responses/discussions
                    elif message_count > len(self.character_contexts) and message_count <= 2*len(self.character_contexts) and current_phase != "responses":
                        f.write("\n\n=== RESPONSES AND DISCUSSIONS ===\n\n")
                        current_phase = "responses"
                
                elif entry_type == "private_note" and current_phase != "private_notes":
                    f.write("\n\n=== PRIVATE NOTES ===\n\n")
                    current_phase = "private_notes"
                    
                elif entry_type == "proposal" and current_phase != "proposals":
                    f.write("\n\n=== PROPOSALS ===\n\n")
                    current_phase = "proposals"
                elif entry_type == "vote_result" and current_phase != "voting":
                    f.write("\n\n=== VOTING RESULTS ===\n\n")
                    current_phase = "voting"
                elif entry_type == "delegate_ranking" and current_phase != "rankings":
                    f.write("\n\n=== DELEGATE RANKINGS ===\n\n")
                    current_phase = "rankings"
                
                # Format the entry based on type
                if entry_type == "message":
                    f.write(f"[{entry['time']}] {entry['speaker']}:\n")
                    f.write(f"{entry['content']}\n\n")
                
                elif entry_type == "private_note":
                    f.write(f"[{entry['time']}] {entry['author']} - PRIVATE NOTE:\n")
                    f.write(f"{entry['content']}\n\n")
                    
                elif entry_type == "proposal":
                    f.write(f"[{entry['time']}] PROPOSAL by {entry['speaker']}:\n")
                    f.write(f"Title: {entry['title']}\n")
                    f.write(f"{entry['content']}\n\n")
                    
                elif entry_type == "vote_result":
                    f.write(f"[{entry['time']}] VOTE RESULT for \"{entry['proposal_title']}\" (by {entry['proposal_author']}):\n")
                    f.write(f"Result: {entry['status']} with {entry['yes']} Yes, {entry['no']} No, {entry['abstain']} Abstain votes\n\n")
                
                elif entry_type == "delegate_ranking":
                    f.write(f"[{entry['time']}] {entry['ranker']}'s DELEGATE RANKINGS:\n")
                    rankings = sorted([(delegate, rank) for delegate, rank in entry['rankings'].items()], key=lambda x: x[1])
                    for delegate, rank in rankings:
                        f.write(f"  Rank {rank}: {delegate}\n")
                    f.write("\n")
        
        print(f"Exported dialogue transcript to {output_file}")
        return output_file

    def add_delegate_ranking(self, ranking: DelegateRanking) -> None:
        """
        Add a delegate's ranking of other delegates.
        
        Args:
            ranking (DelegateRanking): The ranking to add
        """
        self.delegate_rankings.append(ranking)
        
        # Apply ranking points to each delegate's metrics
        points_map = ranking.get_points_map()
        for delegate, points in points_map.items():
            if delegate not in self.metrics:
                self.metrics[delegate] = PerformanceMetrics(delegate)
            self.metrics[delegate].add_ranking_points(points)
    
    def get_delegate_rankings(self) -> List[DelegateRanking]:
        """Get all delegate rankings."""
        return self.delegate_rankings
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """
        Get a sorted leaderboard of delegates based on ranking points.
        
        Returns:
            List[Dict[str, Any]]: Sorted list of delegates with rankings and other metrics
        """
        leaderboard = []
        
        for delegate, metrics in self.metrics.items():
            leaderboard.append({
                "delegate": delegate,
                "ranking_points": metrics.ranking_points,
                "proposals_passed": metrics.proposals_passed,
                "reputation_score": metrics.reputation_score
            })
        
        # Sort by ranking points (primary) and reputation score (secondary)
        leaderboard.sort(key=lambda x: (x["ranking_points"], x["reputation_score"]), reverse=True)
        
        # Add rank to each entry
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
            
        return leaderboard
    
    def export_leaderboard(self, output_file: str = None) -> str:
        """
        Export the delegate leaderboard to a JSON file.
        
        Args:
            output_file (str, optional): The file to save to.
                If None, a default filename with timestamp will be used.
                
        Returns:
            str: The path to the saved file.
        """
        leaderboard = self.get_leaderboard()
        
        # Generate a default filename if none provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
            
            # Create exports directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"delegate_leaderboard_{timestamp}.json")
        
        # Convert to JSON and save
        import json
        with open(output_file, 'w') as f:
            json.dump(leaderboard, f, indent=4)
        
        print(f"Exported delegate leaderboard to {output_file}")
        return output_file