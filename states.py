from enum import Enum, auto
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BotState(Enum):
    """Bot states for conversation management"""
    IDLE = auto()                    # Normal state
    WAITING_FOR_BROADCAST = auto()   # Waiting for broadcast message
    WAITING_FOR_USER_TARGET = auto() # Waiting for user target selection
    SENDING_TO_USER = auto()         # Sending to specific user
    REPLYING_TO_USER = auto()        # Replying to user
    WAITING_FOR_CONFIRMATION = auto() # Waiting for send confirmation
    BLOCKING_USER = auto()           # Blocking user
    UNBLOCKING_USER = auto()         # Unblocking user

class StateManager:
    """Manages bot states and transitions"""
    
    def __init__(self):
        self._states: Dict[int, BotState] = {}
        self._state_data: Dict[int, Dict[str, Any]] = {}
    
    def get_state(self, user_id: int) -> BotState:
        """Get current state for user"""
        return self._states.get(user_id, BotState.IDLE)
    
    def set_state(self, user_id: int, state: BotState, data: Optional[Dict[str, Any]] = None):
        """Set state for user with optional data"""
        old_state = self.get_state(user_id)
        self._states[user_id] = state
        
        if data:
            if user_id not in self._state_data:
                self._state_data[user_id] = {}
            self._state_data[user_id].update(data)
        
        logger.info(f"User {user_id} state changed: {old_state.name} -> {state.name}")
    
    def clear_state(self, user_id: int):
        """Clear state and data for user"""
        old_state = self.get_state(user_id)
        self._states.pop(user_id, None)
        self._state_data.pop(user_id, None)
        logger.info(f"User {user_id} state cleared from {old_state.name}")
    
    def get_state_data(self, user_id: int, key: str = None) -> Any:
        """Get state data for user"""
        user_data = self._state_data.get(user_id, {})
        if key:
            return user_data.get(key)
        return user_data
    
    def set_state_data(self, user_id: int, key: str, value: Any):
        """Set specific state data for user"""
        if user_id not in self._state_data:
            self._state_data[user_id] = {}
        self._state_data[user_id][key] = value
    
    def remove_state_data(self, user_id: int, key: str):
        """Remove specific state data for user"""
        if user_id in self._state_data and key in self._state_data[user_id]:
            del self._state_data[user_id][key]
    
    def is_in_state(self, user_id: int, state: BotState) -> bool:
        """Check if user is in specific state"""
        return self.get_state(user_id) == state
    
    def can_transition_to(self, user_id: int, target_state: BotState) -> bool:
        """Check if transition to target state is allowed"""
        current_state = self.get_state(user_id)
        
        # Define allowed transitions
        allowed_transitions = {
            BotState.IDLE: [
                BotState.WAITING_FOR_BROADCAST,
                BotState.WAITING_FOR_USER_TARGET,
                BotState.REPLYING_TO_USER,
                BotState.BLOCKING_USER,
                BotState.UNBLOCKING_USER
            ],
            BotState.WAITING_FOR_BROADCAST: [
                BotState.IDLE,
                BotState.WAITING_FOR_CONFIRMATION
            ],
            BotState.WAITING_FOR_USER_TARGET: [
                BotState.IDLE,
                BotState.SENDING_TO_USER
            ],
            BotState.SENDING_TO_USER: [
                BotState.IDLE,
                BotState.WAITING_FOR_CONFIRMATION
            ],
            BotState.REPLYING_TO_USER: [
                BotState.IDLE,
                BotState.WAITING_FOR_CONFIRMATION
            ],
            BotState.WAITING_FOR_CONFIRMATION: [
                BotState.IDLE
            ],
            BotState.BLOCKING_USER: [
                BotState.IDLE
            ],
            BotState.UNBLOCKING_USER: [
                BotState.IDLE
            ]
        }
        
        return target_state in allowed_transitions.get(current_state, [])
    
    def transition_to(self, user_id: int, target_state: BotState, data: Optional[Dict[str, Any]] = None) -> bool:
        """Safely transition to target state"""
        if self.can_transition_to(user_id, target_state):
            self.set_state(user_id, target_state, data)
            return True
        else:
            current_state = self.get_state(user_id)
            logger.warning(f"Invalid state transition for user {user_id}: {current_state.name} -> {target_state.name}")
            return False
    
    def reset_to_idle(self, user_id: int):
        """Reset user to idle state"""
        self.set_state(user_id, BotState.IDLE)
        self._state_data.pop(user_id, None)
    
    def get_all_users_in_state(self, state: BotState) -> list:
        """Get all users currently in specific state"""
        return [user_id for user_id, user_state in self._states.items() if user_state == state]
    
    def cleanup_inactive_states(self, active_users: set):
        """Clean up states for inactive users"""
        inactive_users = set(self._states.keys()) - active_users
        for user_id in inactive_users:
            self.clear_state(user_id)
        
        if inactive_users:
            logger.info(f"Cleaned up states for {len(inactive_users)} inactive users")

# Global state manager instance
state_manager = StateManager()