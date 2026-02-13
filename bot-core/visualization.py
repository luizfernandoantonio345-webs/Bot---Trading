"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUALIZATION LAYER — CHART MARKERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Professional chart marker renderer with institutional aesthetics.

DESIGN PHILOSOPHY:
- Deep dark theme with minimal glow
- Visual intensity matches confidence
- Dashed lines = recommendations
- Solid lines = executions
- NO clutter, NO aggressive alerts
- Subtle glass morphism effects

OUTPUT: Structured data for chart rendering (app consumes this)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, List, Tuple
from events import MarkerEvent, MarketContext, MarkerType, ExecutionStatus


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COLOR PALETTE — INSTITUTIONAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Colors:
    """Elite color palette — deep dark institutional"""
    
    # Primary decision colors
    BUY = "#10B981"  # Emerald green
    SELL = "#EF4444"  # Ruby red
    NEUTRAL = "#6B7280"  # Slate gray
    PAUSE = "#F59E0B"  # Amber
    WARNING = "#F97316"  # Orange
    
    # Context backgrounds (subtle)
    TRENDING_BG = "rgba(59, 130, 246, 0.05)"  # Blue tint
    RANGING_BG = "rgba(107, 114, 128, 0.05)"  # Gray tint
    VOLATILE_BG = "rgba(239, 68, 68, 0.08)"  # Red tint
    NEWS_BG = "rgba(245, 158, 11, 0.08)"  # Amber tint
    LOW_LIQ_BG = "rgba(107, 114, 128, 0.03)"  # Very subtle gray
    
    # Glow effects
    GLOW_BUY = "rgba(16, 185, 129, 0.3)"
    GLOW_SELL = "rgba(239, 68, 68, 0.3)"
    GLOW_WARNING = "rgba(245, 158, 11, 0.4)"
    
    # Text
    TEXT_PRIMARY = "#F9FAFB"  # Almost white
    TEXT_SECONDARY = "#9CA3AF"  # Gray
    TEXT_TERTIARY = "#6B7280"  # Darker gray


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VISUAL SPECS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class VisualSpecs:
    """Visual rendering specifications"""
    
    # Line styles
    LINE_SOLID = "solid"
    LINE_DASHED = "dashed"
    LINE_DOTTED = "dotted"
    
    # Marker sizes (relative)
    SIZE_SMALL = 8
    SIZE_MEDIUM = 12
    SIZE_LARGE = 16
    
    # Opacity levels
    OPACITY_LOW = 0.4
    OPACITY_MEDIUM = 0.7
    OPACITY_HIGH = 1.0
    
    # Glow radius
    GLOW_SMALL = 4
    GLOW_MEDIUM = 8
    GLOW_LARGE = 12


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MARKER RENDERER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MarkerRenderer:
    """
    Converts MarkerEvent into visual rendering data.
    
    Output is consumed by:
    - Flutter app (NEXUS COPILOT)
    - Web dashboard
    - Any charting library
    """
    
    @staticmethod
    def render(marker: MarkerEvent) -> dict:
        """
        Convert marker to visual rendering specification.
        
        Returns:
            {
                "id": str,
                "type": str,
                "timestamp": str,
                "price": float,
                "color": str,
                "glow_color": str,
                "line_style": str,
                "size": int,
                "opacity": float,
                "glow_radius": int,
                "icon": str,
                "label": str,
                "label_position": str,
                "tooltip": str,
                "is_actionable": bool,
                "z_index": int
            }
        """
        
        # Base data
        visual = {
            "id": f"{marker.timestamp}_{marker.marker_type.value}",
            "type": marker.marker_type.value,
            "timestamp": marker.timestamp,
            "price": marker.price,
            "is_actionable": marker.is_actionable,
        }
        
        # Type-specific rendering
        if marker.marker_type == MarkerType.BUY_CANDIDATE:
            visual.update(MarkerRenderer._render_buy(marker))
        
        elif marker.marker_type == MarkerType.SELL_CANDIDATE:
            visual.update(MarkerRenderer._render_sell(marker))
        
        elif marker.marker_type == MarkerType.NO_TRADE_ZONE:
            visual.update(MarkerRenderer._render_no_trade(marker))
        
        elif marker.marker_type == MarkerType.BOT_PAUSED:
            visual.update(MarkerRenderer._render_pause(marker))
        
        elif marker.marker_type == MarkerType.HIGH_RISK_CONTEXT:
            visual.update(MarkerRenderer._render_high_risk(marker))
        
        # Add common tooltip
        visual["tooltip"] = MarkerRenderer._build_tooltip(marker)
        
        return visual
    
    # ━━━━━ TYPE-SPECIFIC RENDERERS ━━━━━
    
    @staticmethod
    def _render_buy(marker: MarkerEvent) -> dict:
        """Render BUY marker"""
        
        is_executed = marker.execution_status == ExecutionStatus.EXECUTED
        intensity = marker.visual_intensity
        
        return {
            "color": Colors.BUY,
            "glow_color": Colors.GLOW_BUY,
            "line_style": VisualSpecs.LINE_SOLID if is_executed else VisualSpecs.LINE_DASHED,
            "size": VisualSpecs.SIZE_LARGE if is_executed else VisualSpecs.SIZE_MEDIUM,
            "opacity": VisualSpecs.OPACITY_HIGH if is_executed else VisualSpecs.OPACITY_MEDIUM,
            "glow_radius": int(VisualSpecs.GLOW_MEDIUM * intensity),
            "icon": "▲" if is_executed else "△",
            "label": "BUY" if is_executed else "buy?",
            "label_position": "top",
            "z_index": 100 if is_executed else 50
        }
    
    @staticmethod
    def _render_sell(marker: MarkerEvent) -> dict:
        """Render SELL marker"""
        
        is_executed = marker.execution_status == ExecutionStatus.EXECUTED
        intensity = marker.visual_intensity
        
        return {
            "color": Colors.SELL,
            "glow_color": Colors.GLOW_SELL,
            "line_style": VisualSpecs.LINE_SOLID if is_executed else VisualSpecs.LINE_DASHED,
            "size": VisualSpecs.SIZE_LARGE if is_executed else VisualSpecs.SIZE_MEDIUM,
            "opacity": VisualSpecs.OPACITY_HIGH if is_executed else VisualSpecs.OPACITY_MEDIUM,
            "glow_radius": int(VisualSpecs.GLOW_MEDIUM * intensity),
            "icon": "▼" if is_executed else "▽",
            "label": "SELL" if is_executed else "sell?",
            "label_position": "bottom",
            "z_index": 100 if is_executed else 50
        }
    
    @staticmethod
    def _render_no_trade(marker: MarkerEvent) -> dict:
        """Render NO TRADE marker — educational"""
        
        return {
            "color": Colors.NEUTRAL,
            "glow_color": "transparent",
            "line_style": VisualSpecs.LINE_DOTTED,
            "size": VisualSpecs.SIZE_SMALL,
            "opacity": VisualSpecs.OPACITY_LOW,
            "glow_radius": 0,
            "icon": "◯",
            "label": "no trade",
            "label_position": "right",
            "z_index": 10
        }
    
    @staticmethod
    def _render_pause(marker: MarkerEvent) -> dict:
        """Render BOT PAUSED marker"""
        
        return {
            "color": Colors.PAUSE,
            "glow_color": Colors.GLOW_WARNING,
            "line_style": VisualSpecs.LINE_SOLID,
            "size": VisualSpecs.SIZE_MEDIUM,
            "opacity": VisualSpecs.OPACITY_HIGH,
            "glow_radius": VisualSpecs.GLOW_SMALL,
            "icon": "■",
            "label": "PAUSED",
            "label_position": "right",
            "z_index": 200
        }
    
    @staticmethod
    def _render_high_risk(marker: MarkerEvent) -> dict:
        """Render HIGH RISK marker"""
        
        return {
            "color": Colors.WARNING,
            "glow_color": Colors.GLOW_WARNING,
            "line_style": VisualSpecs.LINE_DASHED,
            "size": VisualSpecs.SIZE_SMALL,
            "opacity": VisualSpecs.OPACITY_MEDIUM,
            "glow_radius": VisualSpecs.GLOW_SMALL,
            "icon": "⚠",
            "label": "high risk",
            "label_position": "right",
            "z_index": 75
        }
    
    # ━━━━━ TOOLTIP BUILDER ━━━━━
    
    @staticmethod
    def _build_tooltip(marker: MarkerEvent) -> str:
        """Build rich tooltip content"""
        
        lines = [
            f"**{marker.marker_type.value}**",
            f"Price: {marker.price:.5f}",
            f"Score: {marker.score:.0f}/100",
            f"Confidence: {marker.confidence:.0%}",
            f"Context: {marker.market_context.value}",
            f"Risk: {marker.risk_level.value}",
            "",
            marker.reason
        ]
        
        if marker.execution_status == ExecutionStatus.EXECUTED and marker.ticket:
            lines.insert(2, f"Ticket: #{marker.ticket}")
        
        return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTEXT BACKGROUND RENDERER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ContextBackgroundRenderer:
    """
    Render subtle chart background shading based on market context.
    
    These are time-based zones, not price levels.
    """
    
    @staticmethod
    def render(context: MarketContext, start_time: str, end_time: str) -> dict:
        """
        Render context background zone.
        
        Returns:
            {
                "start_time": str,
                "end_time": str,
                "background_color": str,
                "border_color": str,
                "label": str,
                "opacity": float
            }
        """
        
        context_map = {
            MarketContext.TRENDING: {
                "background_color": Colors.TRENDING_BG,
                "border_color": "rgba(59, 130, 246, 0.2)",
                "label": "Trending",
                "opacity": 0.3
            },
            MarketContext.RANGING: {
                "background_color": Colors.RANGING_BG,
                "border_color": "rgba(107, 114, 128, 0.2)",
                "label": "Ranging",
                "opacity": 0.2
            },
            MarketContext.VOLATILE: {
                "background_color": Colors.VOLATILE_BG,
                "border_color": "rgba(239, 68, 68, 0.3)",
                "label": "Volatile",
                "opacity": 0.4
            },
            MarketContext.NEWS_WINDOW: {
                "background_color": Colors.NEWS_BG,
                "border_color": "rgba(245, 158, 11, 0.3)",
                "label": "News Window",
                "opacity": 0.5
            },
            MarketContext.LOW_LIQUIDITY: {
                "background_color": Colors.LOW_LIQ_BG,
                "border_color": "rgba(107, 114, 128, 0.1)",
                "label": "Low Liquidity",
                "opacity": 0.2
            },
            MarketContext.UNKNOWN: {
                "background_color": "transparent",
                "border_color": "transparent",
                "label": "",
                "opacity": 0.0
            }
        }
        
        spec = context_map.get(context, context_map[MarketContext.UNKNOWN])
        
        return {
            "start_time": start_time,
            "end_time": end_time,
            **spec
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BATCH RENDERER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_markers(markers: List[MarkerEvent]) -> List[dict]:
    """Batch render multiple markers"""
    return [MarkerRenderer.render(m) for m in markers]


def render_marker_with_context(
    marker: MarkerEvent,
    include_background: bool = False
) -> dict:
    """Render marker with optional context background"""
    
    result = {
        "marker": MarkerRenderer.render(marker)
    }
    
    if include_background and marker.market_context != MarketContext.UNKNOWN:
        # Create time window around marker (e.g., ±30 minutes)
        from datetime import datetime, timedelta
        
        timestamp = datetime.fromisoformat(marker.timestamp)
        start = (timestamp - timedelta(minutes=30)).isoformat()
        end = (timestamp + timedelta(minutes=30)).isoformat()
        
        result["context_background"] = ContextBackgroundRenderer.render(
            marker.market_context,
            start,
            end
        )
    
    return result
