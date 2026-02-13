/// SETUP & INTEGRATION GUIDE
/// 
/// This guide covers integrating the Flutter Trading Dashboard with your Python backend.

import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

// ═══════════════════════════════════════════════════════════════════
// 1. API CLIENT SETUP
// ═══════════════════════════════════════════════════════════════════

class TradingAPIClient {
  final Dio dio;
  final String baseUrl;
  final String? apiKey;

  TradingAPIClient({
    required this.baseUrl,
    this.apiKey,
  }) : dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: Duration(seconds: 10),
    receiveTimeout: Duration(seconds: 10),
    headers: {
      'Content-Type': 'application/json',
      if (apiKey != null) 'Authorization': 'Bearer $apiKey',
    },
  )) {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    dio.interceptors.add(
      InterceptorsWrapper(
        onError: (error, handler) {
          print('API Error: ${error.message}');
          return handler.next(error);
        },
      ),
    );
  }

  // Get health status of backend
  Future<Map<String, dynamic>> getHealth() async {
    try {
      final response = await dio.get('/health');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get health status: $e');
    }
  }

  // Get current market data
  Future<Map<String, dynamic>> getMarketData(String symbol) async {
    try {
      final response = await dio.get(
        '/api/market/$symbol',
        queryParameters: {'timeframe': '1m'},
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to get market data: $e');
    }
  }

  // Get AI analysis
  Future<Map<String, dynamic>> getAIAnalysis(String symbol) async {
    try {
      final response = await dio.post(
        '/api/ai/analyze',
        data: {'symbol': symbol},
      );
      return response.data;
    } catch (e) {
      throw Exception('Failed to get AI analysis: $e');
    }
  }

  // Get historical data
  Future<List<Map<String, dynamic>>> getHistoricalData(
    String symbol, {
    int limit = 100,
  }) async {
    try {
      final response = await dio.get(
        '/api/history/$symbol',
        queryParameters: {'limit': limit},
      );
      return List<Map<String, dynamic>>.from(response.data['data'] ?? []);
    } catch (e) {
      throw Exception('Failed to get historical data: $e');
    }
  }

  // Get indices (fear, RSI, etc)
  Future<Map<String, dynamic>> getIndices() async {
    try {
      final response = await dio.get('/api/indices');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get indices: $e');
    }
  }
}

// ═══════════════════════════════════════════════════════════════════
// 2. WEBSOCKET CLIENT FOR REAL-TIME UPDATES
// ═══════════════════════════════════════════════════════════════════

class RealtimeDataClient {
  late WebSocketChannel channel;
  final String wsUrl;
  Stream<dynamic>? _stream;

  RealtimeDataClient({required this.wsUrl});

  void connect(String symbol) {
    try {
      channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      // Subscribe to symbol
      channel.sink.add('{\"action\":\"subscribe\",\"symbol\":\"$symbol\"}');
      
      _stream = channel.stream.asBroadcastStream();
    } catch (e) {
      print('WebSocket connection error: $e');
    }
  }

  Stream<dynamic>? getStream() => _stream;

  void disconnect() {
    channel.sink.close();
  }
}

// ═══════════════════════════════════════════════════════════════════
// 3. INTEGRATION EXAMPLE WITH PROVIDER
// ═══════════════════════════════════════════════════════════════════

/*
// In your main.dart or app setup:

import 'package:provider/provider.dart';

void main() {
  const apiClient = TradingAPIClient(
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key',
  );

  const realtimeClient = RealtimeDataClient(
    wsUrl: 'ws://localhost:8001',
  );

  runApp(
    MultiProvider(
      providers: [
        Provider<TradingAPIClient>(create: (_) => apiClient),
        Provider<RealtimeDataClient>(create: (_) => realtimeClient),
        // Add your other providers here
      ],
      child: const TradingDashboardApp(),
    ),
  );
}

// ═══════════════════════════════════════════════════════════════════
// 4. STATE NOTIFIER FOR DASHBOARD (with Riverpod)
// ═══════════════════════════════════════════════════════════════════

import 'package:riverpod/riverpod.dart';

final apiClientProvider = Provider<TradingAPIClient>((ref) {
  return TradingAPIClient(
    baseUrl: 'http://localhost:8000',
  );
});

final dashboardDataProvider = FutureProvider<DashboardState>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  
  // Fetch all required data in parallel
  final results = await Future.wait([
    apiClient.getMarketData('BTC/USD'),
    apiClient.getAIAnalysis('BTC/USD'),
    apiClient.getIndices(),
    apiClient.getHistoricalData('BTC/USD', limit: 100),
  ]);

  return DashboardState(
    assetInfo: _parseAssetInfo(results[0]),
    latestAnalysis: _parseAnalysis(results[1]),
    indices: _parseIndices(results[2]),
    realtimeData: _parseHistoricalData(results[3]),
    indicators: TechnicalIndicators(...),
    lastUpdated: DateTime.now(),
    isLoading: false,
    error: null,
  );
});

// ═══════════════════════════════════════════════════════════════════
// 5. BACKEND API ENDPOINTS REFERENCE
// ═══════════════════════════════════════════════════════════════════

/*
GET /health
  └─ Check backend service status

GET /api/market/{symbol}
  ├─ Query params: timeframe (1m, 5m, 15m, 1h, 4h, 1d)
  └─ Response: Current price, volume, trend

GET /api/history/{symbol}
  ├─ Query params: limit (default 100), offset
  └─ Response: List of historical OHLCV data

POST /api/ai/analyze
  ├─ Body: {"symbol": "BTC/USD"}
  └─ Response: signal, confidence, explanation

GET /api/indices
  └─ Response: fear index, MVP index, RSI, etc

WebSocket: ws://localhost:8001
  ├─ Subscribe: {"action":"subscribe","symbol":"BTC/USD"}
  ├─ Unsubscribe: {"action":"unsubscribe","symbol":"BTC/USD"}
  └─ Stream: Real-time price updates

// ═══════════════════════════════════════════════════════════════════
// 6. CONNECTING TO YOUR PYTHON BOT
// ═══════════════════════════════════════════════════════════════════

/*
Update your main_api.py to include these endpoints:

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/market/{symbol}")
def get_market(symbol: str, timeframe: str = "1m"):
    # Get current market data from your bot
    market_data = bot.get_market_data(symbol, timeframe)
    return {
        "symbol": symbol,
        "price": market_data["current_price"],
        "volume": market_data["volume"],
        "trend": "UP" if market_data["trend"] > 0 else "DOWN",
        "high_24h": market_data["high_24h"],
        "low_24h": market_data["low_24h"],
        "change_24h": market_data["change_24h"],
    }

@app.get("/api/history/{symbol}")
def get_history(symbol: str, limit: int = 100):
    # Return historical data
    data = bot.get_historical_data(symbol, limit)
    return {
        "symbol": symbol,
        "data": [
            {
                "timestamp": d["time"],
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"],
            }
            for d in data
        ]
    }

@app.post("/api/ai/analyze")
def analyze(request: AnalysisRequest):
    symbol = request.symbol
    # Get AI analysis from your master orchestrator
    decision = bot.make_complete_decision(symbol)
    return {
        "symbol": symbol,
        "signal": "UP" if decision.score > 50 else "DOWN",
        "confidence": decision.confidence * 100,
        "explanation": decision.explanation,
        "indicators": decision.used_indicators,
    }

@app.get("/api/indices")
def get_indices():
    # Return market indices
    return {
        "fear_index": bot.get_fear_index(),
        "mvp_index": bot.get_mvp_index(),
        "rsi": bot.get_rsi(),
        "timestamp": datetime.now().isoformat(),
    }

// ═══════════════════════════════════════════════════════════════════
// 7. REAL-TIME DATA STREAMING (WebSocket)
// ═══════════════════════════════════════════════════════════════════

from fastapi import WebSocket

@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        while True:
            # Stream real-time data
            price_data = bot.get_realtime_price(symbol)
            await websocket.send_json({
                "type": "price_update",
                "symbol": symbol,
                "price": price_data["price"],
                "volume": price_data["volume"],
                "timestamp": datetime.now().isoformat(),
            })
            await asyncio.sleep(1)  # Update every second
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

// ═══════════════════════════════════════════════════════════════════
// 8. ENVIRONMENT CONFIGURATION
// ═══════════════════════════════════════════════════════════════════

/*
Create .env file in Flutter project root:

API_BASE_URL=http://localhost:8000
WS_URL=ws://localhost:8001
API_KEY=your-api-key-here
ENVIRONMENT=development

Then load in main.dart:
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  await dotenv.load();
  runApp(const TradingDashboardApp());
}

// ═══════════════════════════════════════════════════════════════════
// 9. TESTING THE INTEGRATION
// ═══════════════════════════════════════════════════════════════════

/*
1. Start your Python backend:
   $ python run_api.py

2. Start Flutter emulator/device:
   $ flutter run

3. Test API connectivity:
   - Check logs in Flutter DevTools
   - Verify network requests in backend logs
   - Monitor WebSocket connection

4. Verify data flow:
   - Real-time charts updating
   - AI analysis refreshing
   - Index values changing

// ═══════════════════════════════════════════════════════════════════
// 10. DEPLOYMENT CHECKLIST
// ═══════════════════════════════════════════════════════════════════

- [ ] Backend API running and stable
- [ ] CORS properly configured
- [ ] WebSocket connection stable
- [ ] Error handling implemented
- [ ] Offline mode works
- [ ] Authentication configured
- [ ] Rate limiting set up
- [ ] Logging configured
- [ ] Performance optimized
- [ ] Security measures in place
*/
