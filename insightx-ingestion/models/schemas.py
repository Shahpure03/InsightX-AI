from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class Profile(str, Enum):
    general = "general"
    student = "student"
    investor = "investor"
    explorer = "explorer"
    youngExplorer = "youngExplorer" # Matching frontend state

class ArticleInput(BaseModel):
    url: Optional[str] = None
    article_id: Optional[str] = None
    profile: Profile

class UserCreate(BaseModel):
    name: str = ""
    email: str
    role: str = "student"
    interests: list[str] = []

class AgentContext(BaseModel):
    # Base inputs
    article_text: str = ""
    article_title: str = ""
    article_url: str = ""
    profile: Profile
    
    # 1. Event Agent Outputs
    event_facts: Dict[str, Any] = Field(default_factory=dict) # who, what, where, when, why
    fact_check: Dict[str, Any] = Field(default_factory=dict) # verdict, score
    
    # 2. Reasoning Agent Outputs
    cause_effect_chain: Dict[str, Any] = Field(default_factory=dict)
    sentiment: Dict[str, Any] = Field(default_factory=dict) # label, score
    simplified_text: str = ""
    concept_links: Dict[str, Any] = Field(default_factory=dict) # Set by Student
    stock_impact: Dict[str, Any] = Field(default_factory=dict) # Set by Investor
    mini_glossary: Dict[str, Any] = Field(default_factory=dict) # Set by Explorer
    
    # 3. Personalization Agent Outputs
    topic_deep_dive: str = ""
    translation: str = ""
    summary_short: str = ""
    summary_long: str = ""
    career_impact: Dict[str, Any] = Field(default_factory=dict) # Set by Student
    macro_trend: str = "" # Set by Investor
    
    # 4. Action Agent Outputs
    action_suggestions: List[str] = Field(default_factory=list)
    tts_audio_path: str = ""
    quiz: List[Dict[str, Any]] = Field(default_factory=list) # Set by Explorer
    
    # 5. Prediction Agent Outputs
    predictions: List[str] = Field(default_factory=list)
    portfolio_signals: Dict[str, Any] = Field(default_factory=dict) # Set by Investor

class InsightOutput(BaseModel):
    """The final payload assembled from the AgentContext returned to the frontend."""
    profile_used: Profile
    title: str
    original_url: str
    
    # Core Facts
    summary: str
    event_context: Dict[str, Any]
    fact_check_confidence: str
    
    # Reasoning
    sentiment_label: str
    cause_effect: Dict[str, Any]
    simplified_explainer: str
    
    # Personalization Features
    deep_dive: str
    translated_context: str
    profile_specific_insights: Dict[str, Any] # Dumps career_impact, concept_links, macro_trends etc dynamically
    
    # Action & Outlook
    next_steps: List[str]
    future_predictions: List[str]
    quiz: List[Dict[str, Any]]
    audio_path: str
