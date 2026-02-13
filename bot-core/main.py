import time
import MetaTrader5 as mt5
from datetime import datetime

from config import SYMBOL, MODE, MIN_SCORE_AUTO, MIN_PROB_AUTO
import data as data, indicators as indicators, executor as executor, risk_manager
from dashboard import print_dashboard
from score import calcular_score
from notifier import notificar
from logger import log_trade
from strategy import calcular_decisao   # 🔥 strategy ÚNICO

TIMEFRAME_M15 = mt5.TIMEFRAME_M15
TIMEFRAME_H1 = mt5.TIMEFRAME_H1


# =============================
# MT5 INIT
# =============================
if not mt5.initialize():
    print("❌ MT5 NÃO INICIALIZOU")
    quit()

if mt5.account_info() is None:
    print("❌ CONTA MT5 NÃO ENCONTRADA")
    quit()

print("🚀 BOT INICIADO — SISTEMA ATIVO")


# =============================
# LOOP PRINCIPAL
# =============================
while True:
    try:
        # 🔁 ATUALIZA RISCO / FECHAMENTOS
        risk_manager.check_closed_trades()

        # ---------- DADOS ----------
        df_m15 = data.get_data(SYMBOL, TIMEFRAME_M15, 300)
        df_h1 = data.get_data(SYMBOL, TIMEFRAME_H1, 300)

        if df_m15 is None or df_h1 is None or df_m15.empty or df_h1.empty:
            time.sleep(60)
            continue

        # ---------- INDICADORES ----------
        ema50 = float(indicators.ema(df_m15["close"], 50).iloc[-1])
        ema200 = float(indicators.ema(df_h1["close"], 200).iloc[-1])
        atr = float(indicators.atr(df_m15).iloc[-1])
        preco = float(df_m15["close"].iloc[-1])

        # ---------- TENDÊNCIA ----------
        if preco > ema200:
            tendencia = "ALTA"
        elif preco < ema200:
            tendencia = "BAIXA"
        else:
            time.sleep(60)
            continue

        # ---------- PULLBACK ----------
        distancia = abs(preco - ema50)
        pullback_ok = distancia <= atr * 0.5
        pre_pullback = atr * 0.5 < distancia <= atr

        # ---------- CANDLE ----------
        candle_open = float(df_m15["open"].iloc[-1])
        candle_close = float(df_m15["close"].iloc[-1])

        if candle_close > candle_open:
            candle_forca = "BUY"
        elif candle_close < candle_open:
            candle_forca = "SELL"
        else:
            candle_forca = None

        # ---------- SESSÃO ----------
        h = datetime.now().hour
        if 8 <= h < 12:
            sessao = "LONDRES"
        elif 13 <= h < 17:
            sessao = "NY"
        else:
            sessao = "OFF"

        # ---------- SCORE ----------
        score, motivos = calcular_score(
            tendencia_ok=True,
            pullback_ok=pullback_ok,
            atr_val=atr,
            distancia_ema=distancia,
            candle_open=candle_open,
            candle_high=float(df_m15["high"].iloc[-1]),
            candle_low=float(df_m15["low"].iloc[-1]),
            candle_close=candle_close
        )

        # ---------- STRATEGY (DECISÃO) ----------
        contexto = {
            "trend": tendencia,
            "pullback": pullback_ok,
            "candle_forca": candle_forca,
            "atr_ok": atr > 0,
            "sessao": sessao
        }

        prob_buy, prob_sell, recomendacao, confianca = calcular_decisao(contexto)

        # ---------- STATUS ----------
        if score >= 85:
            status = "SETUP FORTE"
        elif score >= 65:
            status = "OBSERVANDO"
        else:
            status = "AGUARDANDO"

        # ---------- ALERTA (DISCORD) ----------
        if MODE in ["MANUAL", "HYBRID"] and score >= 50:
            notificar(
                symbol=SYMBOL,
                direcao=recomendacao,
                score=score,
                tendencia=tendencia,
                pullback_ok=pullback_ok,
                pre_pullback=pre_pullback,
                atr=atr,
                prob_buy=prob_buy,
                prob_sell=prob_sell,
                recomendacao=recomendacao,
                modo=MODE
            )

        # ==================================================
        # 🚀 AUTO + ⚡ SEMI-AGRESSIVO (ATIVADOS)
        # ==================================================
        if MODE in ["AUTO", "HYBRID"] and risk_manager.can_trade():

            modo_execucao = None

            # 🔥 AUTO NORMAL (MAIS CONSERVADOR)
            if score >= MIN_SCORE_AUTO and confianca == "ALTA":
                modo_execucao = "AUTO"

            # ⚡ SEMI-AGRESSIVO (SÓ MERCADO VIVO)
            elif (
                70 <= score < MIN_SCORE_AUTO
                and confianca == "ALTA"
                and sessao in ["LONDRES", "NY"]
                and pullback_ok
            ):
                modo_execucao = "SEMI"

            if modo_execucao:
                executado = False

                if recomendacao == "BUY" and prob_buy >= MIN_PROB_AUTO:
                    executado = executor.executar_ordem(
                        "BUY",
                        preco - atr,
                        preco + atr * 2
                    )

                elif recomendacao == "SELL" and prob_sell >= MIN_PROB_AUTO:
                    executado = executor.executar_ordem(
                        "SELL",
                        preco + atr,
                        preco - atr * 2
                    )

                if executado:
                    status = f"{modo_execucao} {recomendacao}"
                    log_trade({
                        "timestamp": datetime.now().isoformat(),
                        "symbol": SYMBOL,
                        "direcao": recomendacao,
                        "score": score,
                        "prob_buy": prob_buy,
                        "prob_sell": prob_sell,
                        "confianca": confianca,
                        "sessao": sessao,
                        "tipo": modo_execucao
                    })

        # ---------- DASHBOARD ----------
        print_dashboard(
            symbol=SYMBOL,
            tendencia_h1=tendencia,
            pullback_m15="CONFIRMADO" if pullback_ok else "NÃO",
            atr_m15=round(atr, 6),
            status_entrada=status,
            posicao_aberta=risk_manager.posicao_ativa(),
            trades_hoje=risk_manager.trades_today,
            pnl_hoje=risk_manager.daily_profit,
            drawdown_dia=0,
            score=score,
            prob_buy=prob_buy,
            prob_sell=prob_sell,
            recomendacao=recomendacao,
            confianca=confianca,
            modo=MODE
        )

        time.sleep(60)

    except Exception as e:
        print("❌ ERRO NO LOOP:", e)
        time.sleep(60)
