from dataclasses import dataclass
from typing import Any, Dict, List, Set
from datetime import datetime
from dateutil.parser import parse
from icecream import ic

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
class CommitteeHistory :
    '''
    Class to keep track of all chat histories, logs, notes left 
    from a "agent" to itself, etc.
    '''
    
    history: list                   # Chat history
    notes:  Dict[str: List[Note]]   # Notes left by the agent
    
    character_contexts: Dict[str: str] # {character name: context about character} 
                                       # E.g. context="You are a warlord pirate from the 1700s 
                                       #               in the Mediterranean."
    # msg_id: int = 0               # Message ID for the next message - USE INDEX IN SELF.HISTORY
    
    
    def __init__(self) :
        self.history = []                           # Message history in chat order
        self.notes = {}      # {author: [Note, Note, ...]}
    
    def _add_note(self, note: Note) -> None :
        '''
        Add a note to the notes dictionary.
        
        Args:
            note (Note): Note to be added.
        '''
        if note.author not in self.notes :
            self.notes[note.author] = []
        
        self.notes[note.author].append(note)
    
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
    
    def get_all(self) -> Dict :
        '''
        Get all chat histories, notes, etc.
        '''
        return {
            "history": self.history,
            "notes":   self.notes
        }