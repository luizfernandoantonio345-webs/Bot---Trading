# Trading Dashboard - Institutional-Grade Mobile UI

Professional fintech trading dashboard built with Flutter, implementing pixel-perfect design with institutional standards.

## 🎨 Design Specification

### Color Palette
- **Background**: `#0F1116` - Deep fintech black
- **Card Background**: `#1B1F2A` - Elevated surface
- **Card Separator**: `#2A2F3A` - Subtle dividers
- **Text Primary**: `#FFFFFF` - Main text
- **Text Secondary**: `#9AA4B2` - Secondary labels
- **Profit Green**: `#00C48C` - Positive movement
- **Loss Red**: `#FF4D57` - Negative movement
- **Action Blue**: `#2F80ED` - Interactive elements

### Typography
- **Font Family**: Inter / Roboto Mono
- **Title**: 22px, SemiBold
- **Heading**: 18px, SemiBold  
- **Body**: 14px, Regular
- **Caption**: 12px, Regular
- **Tiny**: 10px, Regular

### Spacing System
- **Card Internal Padding**: 14-16px
- **Card External Spacing**: 10-12px
- **Border Radius**: 12px (all cards)
- **Line Height**: 1.2-1.5x

## 📱 Screens

### Trading Dashboard Screen
Components:
- **Top Bar**: Centered title "Reels", back button, exit mode button
- **Real-time Chart Card**: Line chart with neon green, grid background
- **AI Analysis Panel**: Signal boxes (up/down), analysis button, explanation
- **Asset Info Card**: Vertical data list with live quotes
- **Metrics Grid**: 2-column layout with:
  - Fear Index (semicircle gauge with red-yellow-green gradient)
  - MVP Index (mini vertical bar chart)
  - RSI (strength bar indicator)
  - Quick Stats (high/low/change)
- **SMA vs EMA Chart**: Dual line chart with yellow/green lines

## 🏗️ Project Structure

```
lib/
├── main.dart                           # App entry point
├── core/
│   ├── constants/
│   │   └── design_constants.dart       # Colors, spacing, typography
│   └── theme/
│       └── fintech_theme.dart          # Material theme configuration
├── presentation/
│   ├── screens/
│   │   └── trading_dashboard_screen.dart    # Main dashboard
│   └── widgets/
│       ├── common/
│       │   └── common_widgets.dart     # Reusable card, button, badge components
│       ├── cards/
│       │   └── (card-specific widgets)
│       └── charts/
│           ├── line_charts.dart        # Realtime & dual line charts
│           └── gauge_charts.dart       # Gauge, strength, bar charts
└── data/
    ├── models/                         # Data classes
    └── repositories/                   # Data sources
```

## 🚀 Getting Started

### Prerequisites
- Flutter 3.0+
- Dart 3.0+
- VSCode or Android Studio

### Installation

```bash
# Clone repository
git clone <repo-url>
cd trading_dashboard_flutter

# Get dependencies
flutter pub get

# Run on device/emulator
flutter run

# Build APK
flutter build apk

# Build iOS
flutter build ios
```

## 📦 Core Dependencies

- **UI Components**: Material 3, Flutter
- **Charts**: fl_chart, syncfusion_flutter_charts
- **State Management**: Provider, Riverpod
- **Networking**: Dio, WebSocket
- **Local Storage**: shared_preferences, sqflite
- **Utilities**: Freezed, Json_serializable

## ✨ Key Features

### Pixel-Perfect Design
- Exact spacing and alignment
- Institutional fintech aesthetic
- Dark theme optimized for eyes
- Clean, minimal visual hierarchy

### Performance Optimized
- Lazy loading for charts
- Efficient rebuilds with Provider/Riverpod
- Optimized list rendering
- Cached network images

### Responsive Layout
- Mobile-first design
- Tablet support via flexible layouts
- Touch-friendly minimum targets (48x48dp)
- Adaptive spacing

### Real-time Updates
- WebSocket integration ready
- Streaming data support
- Live chart animations
- Auto-refresh mechanisms

## 🎯 Architecture

### Clean Architecture Pattern
- **Presentation Layer**: UI, screens, widgets
- **Domain Layer**: Business logic (coming soon)
- **Data Layer**: Repositories, API clients, local storage

### State Management
- **Provider**: For simple state
- **Riverpod**: For complex async operations
- **Freezed**: For immutable data classes

## 📊 Chart Components

### RealtimeLineChart
Smooth line chart with grid, tooltips, and gradient fills.
```dart
RealtimeLineChart(
  dataPoints: List<FlSpot>,
  title: 'Chart Title',
  lineColor: Color,
  unit: 'USD',
)
```

### DualLineChart
Comparison chart for SMA vs EMA indicators.
```dart
DualLineChart(
  dataPoints1: List<FlSpot>,
  dataPoints2: List<FlSpot>,
  label1: 'SMA',
  label2: 'EMA',
  color1: Color,
  color2: Color,
)
```

### SemicircleGaugeChart
Fear/sentiment index with gradient gradient.
```dart
SemicircleGaugeChart(
  value: 60,
  label: 'Fear Index',
  gradient: LinearGradient,
)
```

### StrengthBar
RSI or strength indicator with zones.
```dart
StrengthBar(
  value: 44,
  label: 'RSI',
  showZones: true,
)
```

## 🔧 Configuration

### Theme Customization
Edit `lib/core/constants/design_constants.dart`:
```dart
class FinTechColors {
  static const Color background = Color(0xFF0F1116);
  // ... more colors
}
```

### Spacing System
```dart
class FinTechSpacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  // ... more sizes
}
```

## 🎨 Common Widgets

### FinTechCard
Standard card container with padding and borders.

### ActionButton
Primary/secondary buttons with loading states.

### DataRow
Label-value data display with optional styling.

### StatusBadge
Small status indicators with color coding.

## 📈 Performance Metrics

- **Target FPS**: 60fps
- **Build Size**: <20MB (APK)
- **Chart Render Time**: <50ms
- **Memory Usage**: <100MB

## 🔐 Security

- No hardcoded secrets
- Environment-based configuration
- API key management via .env
- Secure local storage for sensitive data

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

## 📝 License

Proprietary - Institutional Trading Platform

---

**Build Time**: ~2-3 hours  
**Complexity**: Professional Grade  
**Maintainability**: High (modular, well-documented)
