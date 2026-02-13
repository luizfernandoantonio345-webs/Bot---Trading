"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MARKER API — BACKEND LAYER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESTful API for Flutter app (NEXUS COPILOT) to consume markers.

ENDPOINTS:
- GET /api/markers/recent — Latest markers
- GET /api/markers/range — Time-range query
- GET /api/markers/{id} — Single marker with explanation
- GET /api/context/current — Current market context
- GET /api/bot/state — Bot operational state
- WS /api/stream — Real-time marker stream (WebSocket)

ARCHITECTURE:
Flask-based API with CORS enabled for Flutter.
Can be deployed standalone or integrated with existing backend.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add bot-core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'bot-core'))

from event_emitter import get_emitter
from copilot_ai import CopilotAI
from visualization import MarkerRenderer, render_marker_with_context
from events import MarkerEvent

# PRODUCTION: Import safety layer
try:
    from safety import get_safety_monitor, emergency_stop, KillSwitch, TradingMode, BotState
    SAFETY_ENABLED = True
except ImportError:
    SAFETY_ENABLED = False
    print("⚠️ Safety layer not available - production features disabled")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APP SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app

emitter = get_emitter()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MARKER ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/markers/recent', methods=['GET'])
def get_recent_markers():
    """
    Get recent markers with optional limit.
    
    Query params:
        limit: int (default 50)
        include_visual: bool (default true)
        include_explanation: bool (default false)
    """
    try:
        limit = int(request.args.get('limit', 50))
        include_visual = request.args.get('include_visual', 'true').lower() == 'true'
        include_explanation = request.args.get('include_explanation', 'false').lower() == 'true'
        
        markers = emitter.get_recent_markers(limit)
        
        # Enrich markers
        enriched = []
        for marker_dict in markers:
            item = {"event": marker_dict}
            
            if include_visual:
                # Reconstruct MarkerEvent for rendering
                # (In production, store MarkerEvent objects or use proper serialization)
                item["visual"] = _render_marker_dict(marker_dict)
            
            if include_explanation:
                item["explanation"] = _explain_marker_dict(marker_dict)
            
            enriched.append(item)
        
        return jsonify({
            "success": True,
            "count": len(enriched),
            "markers": enriched
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/markers/range', methods=['GET'])
def get_markers_by_range():
    """
    Get markers within time range.
    
    Query params:
        start: ISO timestamp
        end: ISO timestamp (optional, defaults to now)
        include_visual: bool
        include_explanation: bool
    """
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        include_visual = request.args.get('include_visual', 'true').lower() == 'true'
        include_explanation = request.args.get('include_explanation', 'false').lower() == 'true'
        
        if not start:
            return jsonify({
                "success": False,
                "error": "start parameter required"
            }), 400
        
        markers = emitter.get_markers_by_timeframe(start, end)
        
        # Enrich
        enriched = []
        for marker_dict in markers:
            item = {"event": marker_dict}
            
            if include_visual:
                item["visual"] = _render_marker_dict(marker_dict)
            
            if include_explanation:
                item["explanation"] = _explain_marker_dict(marker_dict)
            
            enriched.append(item)
        
        return jsonify({
            "success": True,
            "count": len(enriched),
            "start_time": start,
            "end_time": end or datetime.now().isoformat(),
            "markers": enriched
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/markers/<marker_id>', methods=['GET'])
def get_marker_detail(marker_id: str):
    """
    Get single marker with full explanation.
    
    marker_id format: {timestamp}_{marker_type}
    """
    try:
        # Parse marker_id
        parts = marker_id.split('_', 1)
        if len(parts) != 2:
            return jsonify({
                "success": False,
                "error": "Invalid marker_id format"
            }), 400
        
        timestamp, marker_type = parts
        
        # Search in recent markers (in production, use database)
        markers = emitter.get_recent_markers(200)
        
        target = None
        for m in markers:
            if m["timestamp"].startswith(timestamp) and m["marker_type"] == marker_type:
                target = m
                break
        
        if not target:
            return jsonify({
                "success": False,
                "error": "Marker not found"
            }), 404
        
        return jsonify({
            "success": True,
            "marker": {
                "event": target,
                "visual": _render_marker_dict(target),
                "explanation": _explain_marker_dict(target)
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTEXT ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/context/current', methods=['GET'])
def get_current_context():
    """
    Get current market context.
    
    This is computed on-demand from latest market data.
    """
    try:
        # In production, fetch from latest context event or compute fresh
        # For now, return placeholder
        
        return jsonify({
            "success": True,
            "context": {
                "regime": "TRENDING",
                "session": "NY",
                "volatility": 0.45,
                "liquidity": 0.78,
                "risk_level": "MODERATE",
                "is_tradeable": True,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT STATE ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/bot/state', methods=['GET'])
def get_bot_state():
    """
    Get current bot operational state.
    """
    try:
        # Read from risk_manager or state file
        # For now, return mock data
        
        return jsonify({
            "success": True,
            "state": {
                "mode": "HYBRID",
                "active": True,
                "paused": False,
                "daily_trades": 3,
                "daily_pnl": 125.50,
                "risk_utilized": 0.35,
                "positions_open": 0,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COPILOT CHAT ENDPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/copilot/ask', methods=['POST'])
def copilot_ask():
    """
    Ask Copilot AI a question about a marker.
    
    Body:
        {
            "marker_id": str,
            "question": str
        }
    """
    try:
        data = request.get_json()
        marker_id = data.get('marker_id')
        question = data.get('question')
        
        if not marker_id or not question:
            return jsonify({
                "success": False,
                "error": "marker_id and question required"
            }), 400
        
        # Find marker (simplified)
        markers = emitter.get_recent_markers(200)
        
        target = None
        for m in markers:
            mid = f"{m['timestamp']}_{m['marker_type']}"
            if mid.startswith(marker_id):
                target = m
                break
        
        if not target:
            return jsonify({
                "success": False,
                "error": "Marker not found"
            }), 404
        
        # Get answer (simplified - would use CopilotChat in production)
        explanation = _explain_marker_dict(target)
        
        # Simple keyword matching for demo
        question_lower = question.lower()
        if "why" in question_lower:
            answer = explanation["details"]
        elif "risk" in question_lower:
            answer = explanation["risk"]
        elif "should" in question_lower or "do" in question_lower:
            answer = explanation["action"]
        else:
            answer = explanation["summary"]
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "full_explanation": explanation
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEALTH CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check with safety status"""
    response = {
        "success": True,
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
    
    if SAFETY_ENABLED:
        try:
            monitor = get_safety_monitor()
            response["safety"] = monitor.get_status()
        except:
            response["safety"] = "unavailable"
    
    return jsonify(response)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRODUCTION CONTROL ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/bot/pause', methods=['POST'])
def pause_bot():
    """Pause bot immediately"""
    if not SAFETY_ENABLED:
        return jsonify({"success": False, "error": "Safety layer not enabled"}), 503
    
    data = request.json or {}
    reason = data.get('reason', 'APP_REQUESTED')
    
    monitor = get_safety_monitor()
    monitor.pause(reason)
    
    return jsonify({
        "success": True,
        "state": monitor.state.value,
        "reason": reason
    })


@app.route('/api/bot/resume', methods=['POST'])
def resume_bot():
    """Resume bot"""
    if not SAFETY_ENABLED:
        return jsonify({"success": False, "error": "Safety layer not enabled"}), 503
    
    monitor = get_safety_monitor()
    result = monitor.resume()
    
    if not result:
        return jsonify({
            "success": False,
            "error": "Cannot resume - kill switch active",
            "state": monitor.state.value
        }), 400
    
    return jsonify({
        "success": True,
        "state": monitor.state.value
    })


@app.route('/api/bot/kill_switch', methods=['POST'])
def activate_kill_switch():
    """Activate kill switch (EMERGENCY STOP)"""
    if not SAFETY_ENABLED:
        return jsonify({"success": False, "error": "Safety layer not enabled"}), 503
    
    data = request.json or {}
    reason = data.get('reason', 'APP_EMERGENCY_STOP')
    
    emergency_stop(reason)
    
    return jsonify({
        "success": True,
        "kill_switch_active": True,
        "reason": reason
    })


@app.route('/api/bot/mode', methods=['POST'])
def set_mode():
    """Change trading mode"""
    if not SAFETY_ENABLED:
        return jsonify({"success": False, "error": "Safety layer not enabled"}), 503
    
    data = request.json or {}
    mode_str = data.get('mode', '').upper()
    
    try:
        mode = TradingMode(mode_str)
    except ValueError:
        return jsonify({
            "success": False,
            "error": f"Invalid mode: {mode_str}. Use HYBRID, AUTO, or NO_TRADE"
        }), 400
    
    monitor = get_safety_monitor()
    monitor.set_mode(mode)
    
    return jsonify({
        "success": True,
        "mode": mode.value
    })


@app.route('/api/safety/status', methods=['GET'])
def safety_status():
    """Get comprehensive safety status"""
    if not SAFETY_ENABLED:
        return jsonify({"success": False, "error": "Safety layer not enabled"}), 503
    
    monitor = get_safety_monitor()
    return jsonify(monitor.get_status())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_marker_dict(marker_dict: dict) -> dict:
    """Render marker dict to visual spec"""
    # Simplified rendering - in production, reconstruct MarkerEvent properly
    from events import MarkerType, ExecutionStatus, MarketContext, RiskLevel, BotMode
    
    return {
        "color": "#10B981" if "BUY" in marker_dict["marker_type"] else "#EF4444",
        "icon": "▲" if "BUY" in marker_dict["marker_type"] else "▼",
        "label": marker_dict["marker_type"],
        "opacity": 1.0 if marker_dict["execution_status"] == "EXECUTED" else 0.7
    }


def _explain_marker_dict(marker_dict: dict) -> dict:
    """Generate explanation from marker dict"""
    # Simplified - in production, reconstruct MarkerEvent and use CopilotAI
    
    return {
        "title": marker_dict["marker_type"],
        "summary": marker_dict.get("reason", "Market event detected"),
        "details": marker_dict.get("reason", ""),
        "context": f"Context: {marker_dict.get('market_context', 'UNKNOWN')}",
        "risk": f"Risk: {marker_dict.get('risk_level', 'UNKNOWN')}",
        "action": "Review marker for trading decision.",
        "learning": "Monitor market conditions and adjust strategy accordingly."
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    print("🚀 Marker API starting...")
    print("📍 Endpoints:")
    print("   - GET  /api/markers/recent")
    print("   - GET  /api/markers/range")
    print("   - GET  /api/markers/{id}")
    print("   - GET  /api/context/current")
    print("   - GET  /api/bot/state")
    print("   - POST /api/copilot/ask")
    print("   - GET  /api/health")
    print()
    print("🌐 Server: http://localhost:5000")
    print("📱 Flutter app can now connect!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
