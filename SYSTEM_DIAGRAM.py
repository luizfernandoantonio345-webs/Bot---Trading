"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  SISTEMA DE 20 CAMADAS - DIAGRAMA VISUAL                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝


ARQUITETURA GERAL:
═══════════════════════════════════════════════════════════════════════════════

                                   📊 DADOS DE MERCADO
                                      ↓↓↓↓↓↓↓↓
                        ┌─────────────────────────────────┐
                        │  MASTER ORCHESTRATOR (Central)  │
                        │   - Coordena 20 camadas         │
                        │   - 8 fases de decisão          │
                        │   - DecisionContext completo    │
                        └────────┬────────────────────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  │              │              │
                  ↓              ↓              ↓
        ┌─────────────────────────────────────────────────┐
        │           CAMADAS 1-9 (ORIGINAL - INTOCADAS)    │
        ├─────────────────────────────────────────────────┤
        │ 1. MarketAnalyzer      - 7 dimensões            │
        │ 2. PatternEngine       - 13 padrões             │
        │ 3. ScoreEngine         - Score 0-100            │
        │ 4. RiskManager         - Risco inviolável       │
        │ 5. BinanceExecutor     - Real trading           │
        │ 6. MemoryEngine        - SQLite persistence     │
        │ 7. LearningEngine      - Pattern learning       │
        │ 8. Logger              - Professional logging   │
        │ 9. (Reservado)         - Future expansion       │
        └─────────────────────────────────────────────────┘
                  ↑              ↑              ↑
                  │              │              │
        ┌─────────────────────────────────────────────────┐
        │           CAMADAS 10-20 (NOVO - INTELIGÊNCIA)   │
        ├─────────────────────────────────────────────────┤
        │                                                 │
        │ 🔄 Camada 10: SelfEvaluator                     │
        │    └─ Auto-avaliação diária                     │
        │    └─ Ajusta pesos, frequência, agressividade   │
        │                                                 │
        │ 👁️  Camada 11: AttentionModel                   │
        │    └─ Atenção dinâmica adaptativa              │
        │    └─ 6 perfis de regime                        │
        │                                                 │
        │ 📚 Camada 12: SimilarityMatcher                 │
        │    └─ Histórico como validação                 │
        │    └─ 7-fatores de similaridade               │
        │                                                 │
        │ 🎯 Camada 13: StrategyEnsemble                  │
        │    └─ 5 estratégias simultâneas                │
        │    └─ Seleção por regime                        │
        │                                                 │
        │ ⚠️  Camada 14: AnomalyDetector                  │
        │    └─ Fake breakouts                           │
        │    └─ Liquidez artificial                      │
        │                                                 │
        │ ⏰ Camada 15: TemporalController                │
        │    └─ Horários ótimos/proibidos               │
        │    └─ Adapta stops/targets                      │
        │                                                 │
        │ 👥 Camada 16: CrowdIntelligence                 │
        │    └─ Comportamento coletivo                    │
        │    └─ FOMO & Capitulação                        │
        │                                                 │
        │ 💪 Camada 17: ResilienceEngine                  │
        │    └─ Saúde de módulos                         │
        │    └─ Safe mode automático                      │
        │                                                 │
        │ 📖 Camada 18: SecondOrderExplainer              │
        │    └─ Explicação profunda                       │
        │    └─ Cenários de invalidação                   │
        │                                                 │
        │ 🧪 Camada 19: InternalSimulator                 │
        │    └─ Stress test com 5 cenários               │
        │    └─ Validação final                          │
        │                                                 │
        │ 🔮 Camada 20: FutureReadiness                   │
        │    └─ Plugin system                            │
        │    └─ Extensível                               │
        │                                                 │
        └─────────────────────────────────────────────────┘


FLUXO DE DECISÃO:
═══════════════════════════════════════════════════════════════════════════════

                                  📊 MARKET DATA
                                        │
                                        ↓
                    ┌─────────────────────────────────┐
                    │  FASE 1: Validação Preliminar  │
                    │  • Risk check                   │
                    │  • System health check          │
                    │  → Decision: Continue or STOP   │
                    └────────┬────────────────────────┘
                             ↓
                    ┌─────────────────────────────────┐
                    │ FASE 2: Análise Multicamadas   │
                    │ • Market (Cam 1)                │
                    │ • Patterns (Cam 2)              │
                    │ → Market context                │
                    └────────┬────────────────────────┘
                             ↓
            ┌────────────────────────────────────────┐
            │ FASE 3: Análise Contextual Avançada   │
            ├────────────────────────────────────────┤
            │ • Attention (Cam 11)                   │
            │ • Strategy Selection (Cam 13)          │
            │ • Anomaly Detection (Cam 14)           │
            │ • Temporal Control (Cam 15)            │
            │ • Crowd Intelligence (Cam 16)          │
            │ → Advanced context                     │
            └────────┬───────────────────────────────┘
                     ↓
                    ┌─────────────────────────────────┐
                    │ FASE 4: Busca Histórica        │
                    │ • Similarity Matching (Cam 12) │
                    │ → Bloqueia se histórico ruim    │
                    └────────┬────────────────────────┘
                             ↓
                    ┌─────────────────────────────────┐
                    │ FASE 5: Scoring                │
                    │ • Learning (Cam 7)              │
                    │ • Score Calculation (Cam 3)     │
                    │ → Score 0-100                   │
                    └────────┬────────────────────────┘
                             ↓
                    ┌─────────────────────────────────┐
                    │ FASE 6: Validação Extrema      │
                    │ • Internal Simulator (Cam 19)  │
                    │ → Bloqueia se falha stress test │
                    └────────┬────────────────────────┘
                             ↓
                    ┌─────────────────────────────────┐
                    │ FASE 7: Explicação             │
                    │ • Second Order (Cam 18)        │
                    │ → Explicação completa          │
                    └────────┬────────────────────────┘
                             ↓
                    ┌─────────────────────────────────┐
                    │ FASE 8: DecisionContext Final   │
                    │ • Score                         │
                    │ • Recommendation                │
                    │ • Confidence                    │
                    │ • Explicação                    │
                    │ • Todos os contextos            │
                    └────────┬────────────────────────┘
                             ↓
        ╔════════════════════════════════════════════╗
        ║         EXECUTE / REJECT / ANALYZE         ║
        ║                                            ║
        ║ Si EXECUTE:                                ║
        ║ ├─ Cam 5: BinanceExecutor (Real order)    ║
        ║ ├─ Cam 6: MemoryEngine (Save history)     ║
        ║ └─ Cam 17: ResilienceEngine (Track health)║
        ║                                            ║
        ║ Si REJECT:                                 ║
        ║ └─ Explicação de rejeição                 ║
        ║                                            ║
        ║ Periódicamente:                            ║
        ║ └─ Cam 10: SelfEvaluator (Auto-adjust)    ║
        ╚════════════════════════════════════════════╝


AUTOAVALIAÇÃO DIÁRIA (Camada 10):
═══════════════════════════════════════════════════════════════════════════════

                      📅 FIM DO PERÍODO (ex: Daily)
                              │
                              ↓
                    ┌─────────────────────────────────┐
                    │ SelfEvaluator analisa trades:   │
                    │ • Taxa de acerto (WR)           │
                    │ • Expectativa Matemática (EV)   │
                    │ • Drawdown máximo               │
                    │ • Qualidade de entrada          │
                    └────────┬────────────────────────┘
                             ↓
                    ┌─────────────────────────────────┐
                    │ Ajusta automaticamente:         │
                    ├─────────────────────────────────┤
                    │ WR < 50%?                       │
                    │ └─ Aumenta peso em confirmações │
                    │                                 │
                    │ EV < 0.1?                       │
                    │ └─ Aumenta peso em risk/reward  │
                    │                                 │
                    │ DD > 15%?                       │
                    │ └─ Aumenta peso em contexto     │
                    │                                 │
                    │ Performance excelente?          │
                    │ └─ Frequência até 1.5x          │
                    │                                 │
                    │ Performance ruim?               │
                    │ └─ Frequência até 0.5x          │
                    │                                 │
                    │ DD alto?                        │
                    │ └─ Posição até 0.3x             │
                    └────────┬────────────────────────┘
                             ↓
                    ┌─────────────────────────────────┐
                    │ Salva novo estado:              │
                    │ data/self_evaluation_state.json │
                    └────────┬────────────────────────┘
                             ↓
                    ✅ Bot reinicia amanhã com
                       ajustes otimizados


EXEMPLO DE FLUXO REAL:
═══════════════════════════════════════════════════════════════════════════════

Hora: 14:30 (NY Session)

1. Bot recebe EURUSD, 5 min
   Preço: 1.0800
   Volume: Alto
   Trend: Up
   
2. FASE 1: ✓ Risk: OK | ✓ System health: 95%

3. FASE 2: 
   ✓ Market Analysis: Bullish (72/100)
   ✓ Pattern: ENGULFING detectado

4. FASE 3:
   ✓ Attention: TREND_FOLLOWING (99% confiança)
   ✓ Strategy: TREND_FOLLOWER selecionada
   ✓ Anomalies: NONE (mercado limpo)
   ✓ Temporal: Score 90/100 (hora ótima)
   ✓ Crowd: Normal bullish

5. FASE 4:
   ✓ Similaridade: 5 trades similares encontrados
   ✓ Win Rate: 62% (bom!)
   ✓ Status: SEM BLOQUEIOS

6. FASE 5:
   ✓ Learning: +5 bonus (padrão vencedor)
   ✓ Score: 92/100 → EXECUTE!

7. FASE 6:
   Stress Test:
   ├─ Gap down 2%: SL hit ❌
   ├─ Gap up 3%: TP hit ✓
   ├─ Flash crash: SL hit ❌
   ├─ Normal: TP hit ✓
   └─ Survival: 60% ok, 80% desejável
       → Status: APROVADO (60% > 50%)

8. FASE 7:
   Explicação:
   ├─ Por que EXECUTE:
   │  • Score alto (92)
   │  • Histórico positivo (62%)
   │  • Padrão confirmado
   │  • Hora ótima
   │  • Stress test passa
   │
   └─ Riscos:
      • Sentimento pode reverter
      • Se HH quebra → sair

9. RESULTADO:
   ✅ EXECUTE
   Score: 92/100
   Confiança: MUITO ALTA
   Estratégia: TREND_FOLLOWER
   WR esperada: 62%


COMPARAÇÃO COM SISTEMA ANTERIOR:
═══════════════════════════════════════════════════════════════════════════════

ANTES (9 Camadas):
  ├─ ScoreEngine → Score 0-100
  └─ RiskManager → Valida risco
     → Resultado: Score apenas (sem contexto)

DEPOIS (20 Camadas):
  ├─ 9 camadas originais (intocadas)
  ├─ + Autoavaliação (aprende continuamente)
  ├─ + Atenção (adapta-se ao regime)
  ├─ + Histórico (valida contra comprovado)
  ├─ + Múltiplas estratégias (não preso em UMA)
  ├─ + Detecção de anomalias (evita armadilhas)
  ├─ + Inteligência temporal (sabe quando não operar)
  ├─ + Leitura de multidão (evita FOMO)
  ├─ + Resiliência (recupera de falhas)
  ├─ + Explicação profunda (por que?/por que não?)
  ├─ + Stress test (valida extremos)
  └─ + Extensibilidade (pronto para futuro)
     → Resultado: Decisão completa (com contexto)


MATRIZ DE DECISÃO:
═══════════════════════════════════════════════════════════════════════════════

Score | Anomalias | Histórico | Temporal | Stress | Resultado
─────────────────────────────────────────────────────────────────
 95+  |   CLEAN   |   OK      |  ÓTIMA   |  OK    | ✅ EXECUTE (confiança MUITO ALTA)
 90+  |   CLEAN   |   OK      |  BOM     |  OK    | ✅ EXECUTE (confiança ALTA)
 85+  |   CLEAN   |   OK      |  NORMAL  |  OK    | ✅ EXECUTE (confiança MÉDIA)
 80+  |   CLEAN   |   OK      |  NORMAL  |  OK    | ✅ EXECUTE (confiança MÉDIA)
 75+  |   CLEAN   |   OK      |  NORMAL  |  OK    | ⚠️  CONSIDER (risco aumentado)
 75+  |   CLEAN   |   RUIM    |  NORMAL  |  OK    | ❌ REJECT (histórico bloqueado)
 75+  |  ANOMALY  |   OK      |  NORMAL  |  OK    | ❌ REJECT (mercado suspeito)
 75+  |   CLEAN   |   OK      |  RUIM    |  OK    | ❌ REJECT (hora proibida)
 75+  |   CLEAN   |   OK      |  NORMAL  | FAIL   | ❌ REJECT (falha em stress test)
 <75  |   CLEAN   |   OK      |  NORMAL  |  OK    | ❌ REJECT (score muito baixo)


═══════════════════════════════════════════════════════════════════════════════
                         SISTEMA PRONTO PARA PRODUÇÃO
                         20 CAMADAS INTEGRADAS COM SUCESSO
═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
