from typing import List, Dict, Any
import re

class ConversationMemory:
    def __init__(self, max_history: int = 5):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history

    def add_turn(self, user_query: str, assistant_response: str):
        self.history.append({
            "user": user_query,
            "assistant": assistant_response
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context_summary(self) -> str:
        if not self.history:
            return ""
        turns = []
        for turn in self.history[-3:]:
            turns.append(f"User: {turn['user']}\nAssistant: {turn['assistant']}")
        return "\n".join(turns)

    def contextualize_query(self, query: str) -> str:
        """If query contains explicit follow-up pronouns/references, contextualize with previous prompt."""
        if not self.history:
            return query
            
        q_lower = query.lower().strip()
        followup_triggers = ["it", "this", "that", "them", "those", "its", "the same", "what about", "how about", "why"]
        
        # Only contextualize if query contains explicit follow-up words
        words = q_lower.split()
        is_followup = any(w in words for w in ["it", "this", "that", "them", "those", "its"]) or any(q_lower.startswith(p) for p in ["what about", "how about", "why"])
        
        if is_followup:
            last_user = self.history[-1]["user"]
            return f"{last_user} - {query}"
            
        return query

    def clear(self):
        self.history = []

conversation_memory = ConversationMemory()

