"""
═══════════════════════════════════════════════════════════════════
API REST - TRADING BOT
═══════════════════════════════════════════════════════════════════
Servidor FastAPI com endpoints para controlar o bot de trading
e acessar dados dos engines de IA.

Uso:
    python run_api.py

Acessar:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

import uvicorn
import sys

if __name__ == "__main__":
    print("═" * 70)
    print("🚀 INICIANDO API REST - TRADING BOT")
    print("═" * 70)
    print("\n📍 Endpoints disponíveis:")
    print("   • GET  /health                              - Health check")
    print("   • GET  /state                               - Estado atual")
    print("   • POST /buy                                 - Executar BUY")
    print("   • POST /sell                                - Executar SELL")
    print("   • POST /close                               - Fechar posição")
    print("   • GET  /position                            - Dados da posição")
    print("   • GET  /api/ai/health                       - AI Health check")
    print("   • GET  /api/ai/engines/status               - Status dos engines")
    print("   • GET  /api/ai/decision/latest              - Última decisão")
    print("   • GET  /api/ai/decisions/export             - Histórico")
    print("\n🌐 Dashboard:")
    print("   http://localhost:8000/docs")
    print("\n⚠️  Ctrl+C para parar")
    print("═" * 70 + "\n")
    
    # Iniciar servidor
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
