"""
Quota Tracker Module
Tracks API usage and prevents calls when quota is exceeded.

SOLID Principles Applied:
    - SRP: Only handles quota tracking and validation
    - OCP: New tracking strategies can be added without modifying existing code
    - ISP: Minimal interface with focused methods
"""
from typing import Dict, Set
from threading import Lock
from datetime import datetime, timedelta


class QuotaTracker:
    """
    Tracks quota status for AI providers.
    
    Prevents API calls to providers that have exceeded their quota.
    Thread-safe for async operations.
    
    Attributes:
        _blocked_providers (Set[str]): Providers currently blocked due to quota
        _block_until (Dict[str, datetime]): When each provider's block expires
        _lock (Lock): Thread lock for concurrent access
    
    SOLID Principle Applied:
        - SRP: Only tracks quota status, no other responsibilities
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """
        Singleton pattern to ensure one tracker instance.
        
        SOLID Principle Applied:
            - SRP: Only handles instance creation
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._blocked_providers = set()
                    cls._instance._block_until = {}
        return cls._instance
    
    def is_provider_blocked(self, provider: str) -> bool:
        """
        Check if a provider is currently blocked.
        
        Args:
            provider: Name of the AI provider
        
        Returns:
            bool: True if provider is blocked
        
        Source/Caller:
            - Called by: AIService before making API calls
        
        SOLID Principle Applied:
            - SRP: Only checks block status
        """
        with self._lock:
            # Check if block has expired
            if provider in self._block_until:
                if datetime.utcnow() >= self._block_until[provider]:
                    self._unblock_provider(provider)
                    return False
            
            return provider in self._blocked_providers
    
    def block_provider(self, provider: str, duration_minutes: int = 60):
        """
        Block a provider due to quota exceeded.
        
        Args:
            provider: Name of the AI provider
            duration_minutes: How long to block (default 60 minutes)
        
        Source/Caller:
            - Called by: Adapters when quota exceeded error occurs
        
        SOLID Principle Applied:
            - SRP: Only handles blocking logic
        """
        with self._lock:
            self._blocked_providers.add(provider)
            self._block_until[provider] = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def _unblock_provider(self, provider: str):
        """
        Internal method to unblock a provider.
        
        Args:
            provider: Name of the AI provider
        
        SOLID Principle Applied:
            - SRP: Only handles unblocking logic
        """
        self._blocked_providers.discard(provider)
        self._block_until.pop(provider, None)
    
    def manually_unblock_provider(self, provider: str):
        """
        Manually unblock a provider (e.g., admin action).
        
        Args:
            provider: Name of the AI provider
        
        Source/Caller:
            - Called by: Admin endpoints or manual intervention
        
        SOLID Principle Applied:
            - SRP: Only handles manual unblock
        """
        with self._lock:
            self._unblock_provider(provider)
    
    def get_blocked_providers(self) -> Dict[str, str]:
        """
        Get list of currently blocked providers with expiry times.
        
        Returns:
            Dict mapping provider names to expiry timestamps
        
        Source/Caller:
            - Called by: Status endpoints
        
        SOLID Principle Applied:
            - SRP: Only retrieves status information
        """
        with self._lock:
            return {
                provider: expiry.isoformat()
                for provider, expiry in self._block_until.items()
                if provider in self._blocked_providers
            }
    
    def reset(self):
        """
        Reset all quota tracking (for testing or admin reset).
        
        Source/Caller:
            - Called by: Test teardown or admin endpoints
        
        SOLID Principle Applied:
            - SRP: Only resets state
        """
        with self._lock:
            self._blocked_providers.clear()
            self._block_until.clear()
