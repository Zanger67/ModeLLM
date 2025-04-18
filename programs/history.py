from dataclasses import dataclass
from typing import Any, Dict, List
from datetime import datetime
from dateutil.parser import parse

def _convert_datetime(self, 
                        dt: str | datetime | None) -> str :
    '''
    Convert a datetime object to a string.
    
    Args:
        dt (str | datetime): Datetime object or string to be converted.
    
    Returns:
        str: Converted datetime string.
    '''
    if isinstance(dt, str) :
        try :
            dt = parse(dt)
        except ValueError as ve :
            print(f"Error parsing datetime string: {ve}. Defaulting to datetime.now()")
            dt = None
    if dt is None :
        dt = datetime.now()
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
    speaker:   str
    listeners: List[str] = None
    context:   str
    word_cap:  int = 0

    def __init__(self, 
                 content: str,
                 speaker: str,
                 listeners: List[str] = None,
                 time: str | datetime | None = None,
                 context: str = "",
                 word_cap: int = 0) :
        self.content   = content
        self.speaker   = speaker
        self.listeners = listeners if listeners else []
        self.time      = _convert_datetime(time)
        self.context   = context
        self.word_cap  = word_cap
        


@dataclass
class Note:
    '''
    Class to represent a note left by the agent.
    '''
    
    time: str
    content: str
    
    def __init__(self,
                 content: str,
                 time: str | datetime | None = None) :
        self.content = content
        self.time    = _convert_datetime(time)
    
    
    

@dataclass
class CommitteeHistory :
    '''
    Class to keep track of all chat histories, logs, notes left 
    from a "agent" to itself, etc.
    '''
    
    history: list           # Chat history
    # notes: Dict[str, Any]   # Notes left by the agent
    msg_id: int = 0         # Message ID
    
    
    def __init__(self) :
        self.history = []
        self.notes = []
    
    def add_history(self, 
                    hist: Message | Note) -> None :
        '''
        Add a message to the chat history.
        

        '''
        raise NotImplementedError()
    
    def add_note(self, )
    
    def get_all(self) -> Dict :
        '''
        Get all chat histories, notes, etc.
        '''
        return {
            "history": self.history,
            "notes":   self.notes
        }