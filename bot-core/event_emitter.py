"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVENT EMISSION SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Centralized event broadcaster for all marker events.
Clean separation between trading logic and visualization.

ARCHITECTURE:
Bot generates events → EventEmitter broadcasts → Multiple consumers:
  - Backend API (real-time)
  - Local file storage (persistence)
  - Discord notifications (optional)
  - App websocket (real-time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
from datetime import datetime
from typing import List, Callable, Optional
from events import MarkerEvent, MarketContextEvent, BotStateEvent


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EVENT STORAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EVENTS_DIR = "events_log"
MARKERS_FILE = os.path.join(EVENTS_DIR, "markers.jsonl")
CONTEXT_FILE = os.path.join(EVENTS_DIR, "context.jsonl")
STATE_FILE = os.path.join(EVENTS_DIR, "bot_state.jsonl")


def ensure_events_directory():
    """Create events directory if not exists"""
    if not os.path.exists(EVENTS_DIR):
        os.makedirs(EVENTS_DIR)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EVENT EMITTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class EventEmitter:
    """
    Centralized event broadcasting system.
    
    Features:
    - Multiple subscribers (observers)
    - Persistent storage (JSONL)
    - Non-blocking (fire and forget)
    - Type-safe event handling
    """
    
    def __init__(self):
        self._marker_subscribers: List[Callable] = []
        self._context_subscribers: List[Callable] = []
        self._state_subscribers: List[Callable] = []
        ensure_events_directory()
    
    # ━━━━━ SUBSCRIPTION ━━━━━
    
    def subscribe_markers(self, callback: Callable[[MarkerEvent], None]):
        """Subscribe to marker events"""
        self._marker_subscribers.append(callback)
    
    def subscribe_context(self, callback: Callable[[MarketContextEvent], None]):
        """Subscribe to market context events"""
        self._context_subscribers.append(callback)
    
    def subscribe_state(self, callback: Callable[[BotStateEvent], None]):
        """Subscribe to bot state events"""
        self._state_subscribers.append(callback)
    
    # ━━━━━ EMISSION ━━━━━
    
    def emit_marker(self, marker: MarkerEvent):
        """
        Emit marker event to all subscribers + storage.
        
        This is THE primary integration point.
        Every bot decision flows through here.
        """
        
        # Store to file
        self._store_marker(marker)
        
        # Notify subscribers (non-blocking)
        for subscriber in self._marker_subscribers:
            try:
                subscriber(marker)
            except Exception as e:
                print(f"⚠️ Marker subscriber error: {e}")
        
        # Console log (optional, for debugging)
        self._log_marker(marker)
    
    def emit_context(self, context: MarketContextEvent):
        """Emit market context event"""
        
        self._store_context(context)
        
        for subscriber in self._context_subscribers:
            try:
                subscriber(context)
            except Exception as e:
                print(f"⚠️ Context subscriber error: {e}")
    
    def emit_state(self, state: BotStateEvent):
        """Emit bot state change event"""
        
        self._store_state(state)
        
        for subscriber in self._state_subscribers:
            try:
                subscriber(state)
            except Exception as e:
                print(f"⚠️ State subscriber error: {e}")
    
    # ━━━━━ STORAGE ━━━━━
    
    def _store_marker(self, marker: MarkerEvent):
        """Append marker to JSONL file"""
        try:
            with open(MARKERS_FILE, "a") as f:
                f.write(json.dumps(marker.to_dict()) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to store marker: {e}")
    
    def _store_context(self, context: MarketContextEvent):
        """Append context to JSONL file"""
        try:
            with open(CONTEXT_FILE, "a") as f:
                f.write(json.dumps(context.to_dict()) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to store context: {e}")
    
    def _store_state(self, state: BotStateEvent):
        """Append state to JSONL file"""
        try:
            with open(STATE_FILE, "a") as f:
                f.write(json.dumps(state.to_dict()) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to store state: {e}")
    
    # ━━━━━ LOGGING ━━━━━
    
    def _log_marker(self, marker: MarkerEvent):
        """Console log marker (compact format)"""
        
        icon_map = {
            "BUY_CANDIDATE": "🟢",
            "SELL_CANDIDATE": "🔴",
            "NO_TRADE_ZONE": "⚪",
            "BOT_PAUSED": "🛑",
            "HIGH_RISK_CONTEXT": "⚠️"
        }
        
        execution_map = {
            "EXECUTED": "✓",
            "RECOMMENDED": "→",
            "BLOCKED": "✗",
            "PENDING": "⏳"
        }
        
        icon = icon_map.get(marker.marker_type.value, "•")
        exec_icon = execution_map.get(marker.execution_status.value, "")
        
        print(
            f"{icon} {marker.marker_type.value} {exec_icon} | "
            f"Score: {marker.score:.0f} | "
            f"Confidence: {marker.confidence:.0%} | "
            f"{marker.market_context.value}"
        )
    
    # ━━━━━ RETRIEVAL ━━━━━
    
    def get_recent_markers(self, limit: int = 50) -> List[dict]:
        """Get recent markers from file"""
        if not os.path.exists(MARKERS_FILE):
            return []
        
        try:
            with open(MARKERS_FILE, "r") as f:
                lines = f.readlines()
            
            # Get last N lines
            recent = lines[-limit:] if len(lines) > limit else lines
            
            return [json.loads(line) for line in recent]
        except Exception as e:
            print(f"⚠️ Failed to read markers: {e}")
            return []
    
    def get_markers_by_timeframe(
        self,
        start_time: str,
        end_time: Optional[str] = None
    ) -> List[dict]:
        """Get markers within timeframe"""
        if not os.path.exists(MARKERS_FILE):
            return []
        
        end_time = end_time or datetime.now().isoformat()
        
        try:
            with open(MARKERS_FILE, "r") as f:
                markers = []
                for line in f:
                    marker = json.loads(line)
                    if start_time <= marker["timestamp"] <= end_time:
                        markers.append(marker)
                return markers
        except Exception as e:
            print(f"⚠️ Failed to read markers: {e}")
            return []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOBAL INSTANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_emitter = EventEmitter()


def get_emitter() -> EventEmitter:
    """Get global event emitter instance"""
    return _emitter


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONVENIENCE FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def emit_marker(marker: MarkerEvent):
    """Emit marker event (convenience wrapper)"""
    _emitter.emit_marker(marker)


def emit_context(context: MarketContextEvent):
    """Emit context event (convenience wrapper)"""
    _emitter.emit_context(context)


def emit_state(state: BotStateEvent):
    """Emit state event (convenience wrapper)"""
    _emitter.emit_state(state)


def subscribe_to_markers(callback: Callable[[MarkerEvent], None]):
    """Subscribe to marker events (convenience wrapper)"""
    _emitter.subscribe_markers(callback)


def subscribe_to_context(callback: Callable[[MarketContextEvent], None]):
    """Subscribe to context events (convenience wrapper)"""
    _emitter.subscribe_context(callback)


def subscribe_to_state(callback: Callable[[BotStateEvent], None]):
    """Subscribe to state events (convenience wrapper)"""
    _emitter.subscribe_state(callback)
