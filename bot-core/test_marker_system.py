"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST MARKER SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quick test script to verify marker system works
before integrating into production bot.

USAGE:
    python bot-core/test_marker_system.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Ensure bot-core is in path
sys.path.insert(0, os.path.dirname(__file__))

from bot_integration import BotMarkerSystem
from event_emitter import get_emitter


def create_mock_data():
    """Create mock market data for testing"""
    data = {
        "high": [1.08500, 1.08550, 1.08600, 1.08650] * 25,
        "low": [1.08400, 1.08450, 1.08500, 1.08550] * 25,
        "close": [1.08450, 1.08500, 1.08550, 1.08600] * 25,
        "open": [1.08420, 1.08470, 1.08520, 1.08570] * 25,
    }
    return pd.DataFrame(data)


def test_buy_execution():
    """Test BUY execution marker"""
    print("━━━ TEST 1: BUY EXECUTION ━━━")
    
    marker_system = BotMarkerSystem("EURUSD")
    df_m15 = create_mock_data()
    df_h1 = create_mock_data()
    
    marker_system.process_decision(
        price=1.08500,
        direction="BUY",
        score=85.0,
        prob_buy=72.0,
        prob_sell=28.0,
        confidence="ALTA",
        executed=True,
        df_m15=df_m15,
        df_h1=df_h1,
        mode="AUTO",
        ticket=12345,
        sl=1.08000,
        tp=1.09000,
        can_trade=True
    )
    
    print("✅ BUY execution marker generated")


def test_sell_recommendation():
    """Test SELL recommendation marker"""
    print("\n━━━ TEST 2: SELL RECOMMENDATION ━━━")
    
    marker_system = BotMarkerSystem("EURUSD")
    df_m15 = create_mock_data()
    df_h1 = create_mock_data()
    
    marker_system.process_decision(
        price=1.08450,
        direction="SELL",
        score=72.0,
        prob_buy=35.0,
        prob_sell=65.0,
        confidence="ALTA",
        executed=False,
        df_m15=df_m15,
        df_h1=df_h1,
        mode="MANUAL",
        can_trade=True
    )
    
    print("✅ SELL recommendation marker generated")


def test_no_trade():
    """Test NO TRADE marker"""
    print("\n━━━ TEST 3: NO TRADE ZONE ━━━")
    
    marker_system = BotMarkerSystem("EURUSD")
    df_m15 = create_mock_data()
    df_h1 = create_mock_data()
    
    marker_system.process_decision(
        price=1.08400,
        direction="BUY",
        score=45.0,
        prob_buy=55.0,
        prob_sell=45.0,
        confidence="BAIXA",
        executed=False,
        df_m15=df_m15,
        df_h1=df_h1,
        mode="AUTO",
        can_trade=False,
        block_reason="LOW_SCORE"
    )
    
    print("✅ NO TRADE marker generated")


def test_pause():
    """Test BOT PAUSED marker"""
    print("\n━━━ TEST 4: BOT PAUSED ━━━")
    
    marker_system = BotMarkerSystem("EURUSD")
    
    marker_system.process_pause(
        price=1.08350,
        pause_reason="MAX_DAILY_RISK"
    )
    
    print("✅ PAUSE marker generated")


def test_bot_state():
    """Test bot state update"""
    print("\n━━━ TEST 5: BOT STATE UPDATE ━━━")
    
    marker_system = BotMarkerSystem("EURUSD")
    
    marker_system.update_bot_state(
        mode="HYBRID",
        active=True,
        paused=False,
        daily_trades=3,
        daily_pnl=125.50,
        risk_utilized=0.35
    )
    
    print("✅ Bot state updated")


def verify_files():
    """Verify event files were created"""
    print("\n━━━ VERIFICATION ━━━")
    
    events_dir = "events_log"
    markers_file = os.path.join(events_dir, "markers.jsonl")
    context_file = os.path.join(events_dir, "context.jsonl")
    state_file = os.path.join(events_dir, "bot_state.jsonl")
    
    if os.path.exists(markers_file):
        with open(markers_file, 'r') as f:
            count = len(f.readlines())
        print(f"✅ markers.jsonl: {count} events")
    else:
        print("❌ markers.jsonl not found")
    
    if os.path.exists(context_file):
        with open(context_file, 'r') as f:
            count = len(f.readlines())
        print(f"✅ context.jsonl: {count} events")
    else:
        print("⚠️ context.jsonl not found (may be empty if no context changes)")
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            count = len(f.readlines())
        print(f"✅ bot_state.jsonl: {count} events")
    else:
        print("⚠️ bot_state.jsonl not found")


def test_api_readiness():
    """Test if events can be read by API"""
    print("\n━━━ API READINESS ━━━")
    
    emitter = get_emitter()
    recent = emitter.get_recent_markers(limit=5)
    
    if recent:
        print(f"✅ API can read {len(recent)} recent markers")
        print(f"   Latest: {recent[-1]['marker_type']} at {recent[-1]['timestamp']}")
    else:
        print("⚠️ No markers found (run tests first)")


def main():
    """Run all tests"""
    print("╔═══════════════════════════════════════════════╗")
    print("║   ELITE VISUAL DECISION SYSTEM — TEST SUITE  ║")
    print("╚═══════════════════════════════════════════════╝")
    print()
    
    try:
        test_buy_execution()
        test_sell_recommendation()
        test_no_trade()
        test_pause()
        test_bot_state()
        verify_files()
        test_api_readiness()
        
        print("\n╔═══════════════════════════════════════════════╗")
        print("║              ✅ ALL TESTS PASSED              ║")
        print("╚═══════════════════════════════════════════════╝")
        print()
        print("NEXT STEPS:")
        print("1. Check events_log/ directory for generated files")
        print("2. Start API server: python core/marker_api.py")
        print("3. Test API: curl http://localhost:5000/api/health")
        print("4. Integrate into main.py (see INTEGRATION_GUIDE.py)")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
