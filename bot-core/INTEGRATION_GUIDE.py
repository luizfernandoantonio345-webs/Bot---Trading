"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAIN.PY INTEGRATION PATCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

How to integrate marker system into existing main.py:

STEP 1: Add import at top of file
STEP 2: Initialize marker system
STEP 3: Call marker system in decision flow
STEP 4: Update bot state

NO CHANGES TO CORE TRADING LOGIC REQUIRED.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: ADD IMPORT (at top of main.py)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
from bot_integration import BotMarkerSystem
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: INITIALIZE (after MT5 init, before loop)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# Initialize marker system
marker_system = BotMarkerSystem(SYMBOL)
print("✅ Marker system initialized")
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: INTEGRATE INTO DECISION FLOW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# After calculating prob_buy, prob_sell, recomendacao, confianca
# and BEFORE execution logic:

# Determine if trade can be executed
can_trade_now = risk_manager.can_trade()
block_reason = None

if not can_trade_now:
    if risk_manager.posicao_ativa():
        block_reason = "POSITION_ACTIVE"
    elif risk_manager.trades_today >= MAX_TRADES_PER_DAY:
        block_reason = "MAX_TRADES"
    elif risk_manager.daily_loss >= MAX_DAILY_RISK:
        block_reason = "MAX_RISK"
    elif risk_manager.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
        block_reason = "CONSECUTIVE_LOSSES"
    elif risk_manager.daily_profit >= DAILY_PROFIT_TARGET:
        block_reason = "PROFIT_TARGET"
    elif risk_manager.paused:
        block_reason = "PAUSED"
    else:
        block_reason = "LOW_SCORE"

# Process decision with marker system
marker_system.process_decision(
    price=preco,
    direction=recomendacao,
    score=score,
    prob_buy=prob_buy,
    prob_sell=prob_sell,
    confidence=confianca,
    executed=False,  # Will update to True after execution
    df_m15=df_m15,
    df_h1=df_h1,
    mode=MODE,
    can_trade=can_trade_now,
    block_reason=block_reason
)

# Then continue with existing execution logic...
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3B: AFTER EXECUTION (if trade executed)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# After executor.executar_ordem() returns True:

if executado:
    # Generate execution marker
    marker_system.process_decision(
        price=preco,
        direction=recomendacao,
        score=score,
        prob_buy=prob_buy,
        prob_sell=prob_sell,
        confidence=confianca,
        executed=True,
        df_m15=df_m15,
        df_h1=df_h1,
        mode=MODE,
        ticket=result.order if result else None,
        sl=preco - atr if recomendacao == "BUY" else preco + atr,
        tp=preco + atr * 2 if recomendacao == "BUY" else preco - atr * 2,
        can_trade=True
    )
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: UPDATE BOT STATE (after each cycle)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# At end of loop, before time.sleep():

marker_system.update_bot_state(
    mode=MODE,
    active=True,
    paused=risk_manager.paused,
    paused_reason="MAX_DAILY_RISK" if risk_manager.paused else None,
    daily_trades=risk_manager.trades_today,
    daily_pnl=risk_manager.daily_profit,
    risk_utilized=risk_manager.daily_loss / risk_manager.MAX_DAILY_RISK
)
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPLETE INTEGRATION EXAMPLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
Full integration in main.py loop:

while True:
    try:
        # [... existing code: get data, calculate indicators, etc ...]
        
        # [... calculate prob_buy, prob_sell, recomendacao, confianca ...]
        
        # ━━━━━ MARKER INTEGRATION START ━━━━━
        
        # Determine trade eligibility
        can_trade_now = risk_manager.can_trade()
        block_reason = None
        
        if not can_trade_now:
            if risk_manager.posicao_ativa():
                block_reason = "POSITION_ACTIVE"
            elif risk_manager.trades_today >= risk.MAX_TRADES_PER_DAY:
                block_reason = "MAX_TRADES"
            elif risk_manager.daily_loss >= risk.MAX_DAILY_RISK:
                block_reason = "MAX_RISK"
            elif risk_manager.paused:
                block_reason = "PAUSED"
            else:
                block_reason = "LOW_SCORE"
        
        # Generate recommendation marker (before execution attempt)
        if score >= 50:  # Only generate markers for meaningful setups
            marker_system.process_decision(
                price=preco,
                direction=recomendacao,
                score=score,
                prob_buy=prob_buy,
                prob_sell=prob_sell,
                confidence=confianca,
                executed=False,
                df_m15=df_m15,
                df_h1=df_h1,
                mode=MODE,
                can_trade=can_trade_now,
                block_reason=block_reason
            )
        
        # ━━━━━ MARKER INTEGRATION END ━━━━━
        
        # [... existing execution logic ...]
        
        if MODE in ["AUTO", "HYBRID"] and can_trade_now:
            if score >= MIN_SCORE_AUTO and confianca == "ALTA":
                executado = False
                
                if recomendacao == "BUY" and prob_buy >= MIN_PROB_AUTO:
                    executado = executor.executar_ordem("BUY", preco - atr, preco + atr * 2)
                    
                    # ━━━━━ EXECUTION MARKER ━━━━━
                    if executado:
                        marker_system.process_decision(
                            price=preco,
                            direction="BUY",
                            score=score,
                            prob_buy=prob_buy,
                            prob_sell=prob_sell,
                            confidence=confianca,
                            executed=True,
                            df_m15=df_m15,
                            df_h1=df_h1,
                            mode=MODE,
                            sl=preco - atr,
                            tp=preco + atr * 2,
                            can_trade=True
                        )
                
                elif recomendacao == "SELL" and prob_sell >= MIN_PROB_AUTO:
                    executado = executor.executar_ordem("SELL", preco + atr, preco - atr * 2)
                    
                    # ━━━━━ EXECUTION MARKER ━━━━━
                    if executado:
                        marker_system.process_decision(
                            price=preco,
                            direction="SELL",
                            score=score,
                            prob_buy=prob_buy,
                            prob_sell=prob_sell,
                            confidence=confianca,
                            executed=True,
                            df_m15=df_m15,
                            df_h1=df_h1,
                            mode=MODE,
                            sl=preco + atr,
                            tp=preco - atr * 2,
                            can_trade=True
                        )
        
        # [... existing dashboard print ...]
        
        # Update bot state
        marker_system.update_bot_state(
            mode=MODE,
            active=True,
            paused=risk_manager.paused,
            daily_trades=risk_manager.trades_today,
            daily_pnl=risk_manager.daily_profit,
            risk_utilized=risk_manager.daily_loss / risk.MAX_DAILY_RISK if risk.MAX_DAILY_RISK > 0 else 0
        )
        
        time.sleep(60)
        
    except Exception as e:
        print("❌ ERRO:", e)
        time.sleep(60)
"""
