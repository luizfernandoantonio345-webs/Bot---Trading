"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCTION VALIDATION TESTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Comprehensive tests for live trading validation.
MUST pass ALL tests before using real capital.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from safety import SafetyMonitor, SafetyLimits, KillSwitch, BotState, TradingMode, emergency_stop


def test_kill_switch():
    """Test kill switch activation"""
    print("━━━ TEST: Kill Switch ━━━")
    
    kill_switch = KillSwitch()
    kill_switch.deactivate()  # Reset
    
    assert not kill_switch.is_active(), "Kill switch should be inactive"
    
    kill_switch.activate("TEST_ACTIVATION")
    assert kill_switch.is_active(), "Kill switch should be active"
    assert kill_switch.get_reason() == "TEST_ACTIVATION", "Reason should match"
    
    # Test persistence
    kill_switch2 = KillSwitch()
    assert kill_switch2.is_active(), "Kill switch should persist"
    
    kill_switch.deactivate()
    assert not kill_switch.is_active(), "Kill switch should be deactivated"
    
    print("✅ Kill switch works correctly")


def test_daily_loss_limit():
    """Test daily loss limit enforcement"""
    print("\n━━━ TEST: Daily Loss Limit ━━━")
    
    limits = SafetyLimits()
    limits.MAX_DAILY_LOSS = 100.0
    
    monitor = SafetyMonitor(limits)
    monitor.state = BotState.RUNNING
    monitor.daily_loss = 0.0
    monitor.consecutive_losses = 0  # Reset
    
    # Should allow trading
    can_trade, reason = monitor.can_trade()
    assert can_trade, f"Should allow trading: {reason}"
    
    # Simulate losses approaching limit
    monitor.record_trade_result(-50.0)
    can_trade, reason = monitor.can_trade()
    assert can_trade, f"Should still allow trading: {reason}"
    
    # Exceed limit
    monitor.record_trade_result(-60.0)
    can_trade, reason = monitor.can_trade()
    assert not can_trade, "Should block trading after loss limit"
    assert monitor.state == BotState.PAUSED, "Bot should be paused"
    
    print("✅ Daily loss limit enforced")


def test_consecutive_losses():
    """Test consecutive losses auto-pause"""
    print("\n━━━ TEST: Consecutive Losses ━━━")
    
    limits = SafetyLimits()
    limits.MAX_CONSECUTIVE_LOSSES = 3
    limits.MAX_DAILY_LOSS = 1000.0  # High limit to not interfere
    limits.MAX_DAILY_TRADES = 100  # High limit to not interfere
    
    monitor = SafetyMonitor(limits)
    monitor.state = BotState.RUNNING
    monitor.consecutive_losses = 0
    monitor.daily_loss = 0.0
    monitor.daily_trades = 0
    
    # Record 2 losses
    monitor.record_trade_result(-10.0)
    monitor.record_trade_result(-10.0)
    
    can_trade, reason = monitor.can_trade()
    assert can_trade, f"Should still allow trading after 2 losses: {reason}"
    
    # 3rd loss should pause
    monitor.record_trade_result(-10.0)
    can_trade, reason = monitor.can_trade()
    assert not can_trade, "Should block trading after 3 losses"
    assert monitor.state == BotState.PAUSED, "Bot should be paused"
    
    print("✅ Consecutive losses handled correctly")


def test_trades_limit():
    """Test daily trades limit"""
    print("\n━━━ TEST: Daily Trades Limit ━━━")
    
    limits = SafetyLimits()
    limits.MAX_DAILY_TRADES = 5
    limits.MAX_DAILY_LOSS = 1000.0  # High limit to not interfere
    
    monitor = SafetyMonitor(limits)
    monitor.state = BotState.RUNNING
    monitor.daily_trades = 0
    monitor.daily_loss = 0.0
    
    # Execute 4 trades
    for i in range(4):
        monitor.record_trade_result(10.0)
        can_trade, reason = monitor.can_trade()
        assert can_trade, f"Should allow trading (trade {i+1}/5)"
    
    # 5th trade
    monitor.record_trade_result(10.0)
    can_trade, reason = monitor.can_trade()
    assert not can_trade, "Should block trading after 5 trades"
    assert monitor.state == BotState.PAUSED, "Bot should be paused"
    
    print("✅ Daily trades limit enforced")


def test_score_validation():
    """Test score threshold validation"""
    print("\n━━━ TEST: Score Validation ━━━")
    
    limits = SafetyLimits()
    limits.MIN_SCORE_HYBRID = 65.0
    limits.MIN_SCORE_AUTO = 90.0
    
    monitor = SafetyMonitor(limits)
    monitor.state = BotState.RUNNING
    
    # HYBRID mode - score 70 should pass
    monitor.mode = TradingMode.HYBRID
    valid, reason = monitor.validate_trade(score=70.0, lot_size=0.01)
    assert valid, f"Score 70 should pass in HYBRID: {reason}"
    
    # HYBRID mode - score 60 should fail
    valid, reason = monitor.validate_trade(score=60.0, lot_size=0.01)
    assert not valid, "Score 60 should fail in HYBRID"
    
    # AUTO mode - score 85 should fail
    monitor.mode = TradingMode.AUTO
    valid, reason = monitor.validate_trade(score=85.0, lot_size=0.01)
    assert not valid, "Score 85 should fail in AUTO (needs 90+)"
    
    # AUTO mode - score 92 should pass
    valid, reason = monitor.validate_trade(score=92.0, lot_size=0.01)
    assert valid, f"Score 92 should pass in AUTO: {reason}"
    
    print("✅ Score validation works correctly")


def test_lot_size_validation():
    """Test lot size limit"""
    print("\n━━━ TEST: Lot Size Validation ━━━")
    
    limits = SafetyLimits()
    limits.MAX_POSITION_SIZE = 0.01
    
    monitor = SafetyMonitor(limits)
    monitor.state = BotState.RUNNING
    monitor.mode = TradingMode.AUTO
    
    # Valid lot size
    valid, reason = monitor.validate_trade(score=95.0, lot_size=0.01)
    assert valid, f"Lot size 0.01 should pass: {reason}"
    
    # Excessive lot size
    valid, reason = monitor.validate_trade(score=95.0, lot_size=0.05)
    assert not valid, "Lot size 0.05 should fail"
    
    print("✅ Lot size validation works correctly")


def test_state_transitions():
    """Test bot state transitions"""
    print("\n━━━ TEST: State Transitions ━━━")
    
    limits = SafetyLimits()
    monitor = SafetyMonitor(limits)
    kill_switch = KillSwitch()
    kill_switch.deactivate()
    
    # Reset to clean state
    monitor.daily_loss = 0.0
    monitor.daily_trades = 0
    monitor.consecutive_losses = 0
    monitor.state = BotState.STOPPED
    
    # Start bot
    assert monitor.state == BotState.STOPPED, "Should start in STOPPED"
    monitor.start()
    assert monitor.state == BotState.RUNNING, "Should transition to RUNNING"
    
    # Pause bot
    monitor.pause("TEST_PAUSE")
    assert monitor.state == BotState.PAUSED, "Should transition to PAUSED"
    
    # Resume bot
    monitor.resume()
    assert monitor.state == BotState.RUNNING, "Should transition back to RUNNING"
    
    # Error state
    monitor.error("TEST_ERROR")
    # Note: error() sets state to ERROR then immediately to PAUSED
    # So we check PAUSED not ERROR
    assert monitor.state == BotState.PAUSED, "Should auto-pause on error"
    
    print("✅ State transitions work correctly")


def test_kill_switch_prevents_trading():
    """Test kill switch blocks all trading"""
    print("\n━━━ TEST: Kill Switch Blocks Trading ━━━")
    
    limits = SafetyLimits()
    monitor = SafetyMonitor(limits)
    kill_switch = KillSwitch()
    kill_switch.deactivate()
    
    # Reset monitor
    monitor.state = BotState.RUNNING
    monitor.daily_loss = 0.0
    monitor.daily_trades = 0
    monitor.consecutive_losses = 0
    
    # Should allow trading
    can_trade, reason = monitor.can_trade()
    assert can_trade, f"Should allow trading: {reason}"
    
    # Activate kill switch
    kill_switch.activate("MANUAL_EMERGENCY_STOP")
    
    # Should block trading
    can_trade, reason = monitor.can_trade()
    assert not can_trade, "Kill switch should block trading"
    assert "KILL_SWITCH" in reason, f"Reason should mention kill switch: {reason}"
    
    # Cannot start bot with active kill switch
    monitor.state = BotState.STOPPED
    result = monitor.start()
    assert not result, "Should not start with active kill switch"
    
    # Deactivate and retry
    kill_switch.deactivate()
    result = monitor.start()
    assert result, "Should start after kill switch deactivation"
    
    print("✅ Kill switch blocks trading correctly")


def test_error_handling():
    """Test error triggers safety mechanisms"""
    print("\n━━━ TEST: Error Handling ━━━")
    
    monitor = SafetyMonitor(SafetyLimits())
    monitor.state = BotState.RUNNING
    
    # Simulate error
    monitor.error("SIMULATED_EXCEPTION")
    
    # Bot should be paused
    assert monitor.state == BotState.PAUSED, "Bot should auto-pause on error"
    
    # Trading should be blocked
    can_trade, reason = monitor.can_trade()
    assert not can_trade, "Trading should be blocked after error"
    
    print("✅ Error handling works correctly")


def test_mode_enforcement():
    """Test mode enforcement"""
    print("\n━━━ TEST: Mode Enforcement ━━━")
    
    limits = SafetyLimits()
    monitor = SafetyMonitor(limits)
    monitor.state = BotState.RUNNING
    monitor.daily_loss = 0.0
    monitor.daily_trades = 0
    monitor.consecutive_losses = 0
    
    # NO_TRADE mode should block everything
    monitor.set_mode(TradingMode.NO_TRADE)
    can_trade, reason = monitor.can_trade()
    assert not can_trade, "NO_TRADE mode should block trading"
    assert "NO_TRADE" in reason, f"Reason should mention mode: {reason}"
    
    # HYBRID mode should allow trading
    monitor.set_mode(TradingMode.HYBRID)
    can_trade, reason = monitor.can_trade()
    assert can_trade, f"HYBRID mode should allow trading: {reason}"
    
    print("✅ Mode enforcement works correctly")


def run_all_tests():
    """Run complete validation suite"""
    print("╔═══════════════════════════════════════════════╗")
    print("║   PRODUCTION VALIDATION — CAPITAL REAL        ║")
    print("╚═══════════════════════════════════════════════╝\n")
    
    tests = [
        test_kill_switch,
        test_daily_loss_limit,
        test_consecutive_losses,
        test_trades_limit,
        test_score_validation,
        test_lot_size_validation,
        test_state_transitions,
        test_kill_switch_prevents_trading,
        test_error_handling,
        test_mode_enforcement
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n╔═══════════════════════════════════════════════╗")
    if failed == 0:
        print("║         ✅ ALL TESTS PASSED (10/10)          ║")
        print("╚═══════════════════════════════════════════════╝")
        print("\n🛡️ SYSTEM VALIDATED FOR LIVE TRADING")
        return True
    else:
        print(f"║      ❌ TESTS FAILED: {failed}/{len(tests)}                  ║")
        print("╚═══════════════════════════════════════════════╝")
        print("\n⚠️ SYSTEM NOT READY FOR LIVE TRADING")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
