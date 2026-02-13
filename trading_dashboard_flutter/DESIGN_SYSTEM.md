# 🎨 INSTITUTIONAL TRADING DASHBOARD - DESIGN SYSTEM

Complete design documentation for pixel-perfect mobile trading UI implementation.

---

## TABLE OF CONTENTS

1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Spacing System](#spacing-system)
4. [Components](#components)
5. [Layouts](#layouts)
6. [Best Practices](#best-practices)

---

## COLOR PALETTE

### Primary Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Background | #0F1116 | rgb(15, 17, 22) | Main app background |
| Card BG | #1B1F2A | rgb(27, 31, 42) | Card backgrounds |
| Separator | #2A2F3A | rgb(42, 47, 58) | Borders, dividers |

### Text Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Primary | #FFFFFF | rgb(255, 255, 255) | Main text |
| Secondary | #9AA4B2 | rgb(154, 164, 178) | Labels, hints |
| Tertiary | #6B7280 | rgb(107, 114, 128) | Disabled, muted |

### Status Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Profit | #00C48C | rgb(0, 196, 140) | Gains, up trends |
| Loss | #FF4D57 | rgb(255, 77, 87) | Losses, down trends |
| Action | #2F80ED | rgb(47, 128, 237) | Buttons, links |

### Chart Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Chart Green | #00D084 | rgb(0, 208, 132) | Positive trends |
| Chart Red | #FF5A6B | rgb(255, 90, 107) | Negative trends |
| Chart Yellow | #FDB022 | rgb(253, 176, 34) | SMA lines |
| Chart Grid | #2A2F3A | rgb(42, 47, 58) | Grid lines |

---

## TYPOGRAPHY

### Font Families
- **Primary**: Inter (sans-serif)
  - Display: 22px, Weight 600 (SemiBold)
  - Heading: 18px, Weight 600 (SemiBold)
  - Body: 14px, Weight 400 (Regular)
  - Caption: 12px, Weight 400 (Regular)

- **Secondary**: Roboto Mono (monospace)
  - Price displays: 14px, Weight 600
  - Data values: 12-14px, Weight 400-700

### Text Styles

#### Display Large
- Size: 22px
- Weight: 600 (SemiBold)
- Line Height: 1.2
- Letter Spacing: -0.5px
- Usage: Screen titles

#### Heading Medium
- Size: 18px
- Weight: 600 (SemiBold)
- Line Height: 1.3
- Usage: Card titles

#### Title Large
- Size: 14px
- Weight: 600 (SemiBold)
- Usage: Subheadings, labels

#### Body Medium
- Size: 14px
- Weight: 400 (Regular)
- Line Height: 1.5
- Usage: Main body text

#### Body Small
- Size: 14px
- Weight: 400 (Regular)
- Color: Secondary text
- Line Height: 1.5
- Usage: Secondary descriptions

#### Label Small (Caption)
- Size: 12px
- Weight: 400 (Regular)
- Color: Secondary text
- Letter Spacing: 0.3px
- Usage: Captions, small labels

---

## SPACING SYSTEM

### Base Unit: 4px

| Scale | Value | Use Cases |
|-------|-------|-----------|
| XS | 4px | Tight spacing, icon margins |
| SM | 8px | Element spacing, padding |
| MD | 12px | Card internal padding |
| LG | 16px | Large padding, screen margins |
| XL | 24px | Sections spacing |
| XXL | 32px | Major layout gaps |

### Card Specifications
- **Internal Padding**: 14-16px
- **External Spacing**: 10-12px
- **Border Radius**: 12px
- **Border Width**: 1px
- **Border Color**: #2A2F3A (Separator)

### Layout Constants
- **Screen Horizontal Padding**: 16px
- **Max Chart Height**: 280px
- **Min Touch Target**: 48x48dp
- **Grid Gap**: 10-12px

---

## COMPONENTS

### Card Component
Reusable container with consistent styling.

**Specifications:**
- Background: #1B1F2A
- Border: 1px solid #2A2F3A
- Border Radius: 12px
- Padding: 14-16px (internal)
- Margin: 10-12px (external)

**States:**
- Default: Static background
- Pressed/Tapped: Slight opacity change
- Disabled: Reduced opacity, muted colors

### Button Component
Primary and secondary action buttons.

**Primary Button:**
- Background: #2F80ED (Action Blue)
- Text Color: #FFFFFF
- Padding: 12px horizontal, 10px vertical
- Border Radius: 12px
- Font Size: 14px
- Min Width: 44px (touch target)

**Secondary Button:**
- Background: Transparent
- Border: 1px solid #2F80ED
- Text Color: #2F80ED
- Same padding & radius as primary

**States:**
- Default: Normal appearance
- Hover: Slight opacity increase
- Pressed: Darker shade
- Disabled: Grayed out (#2A2F3A background)
- Loading: Spinner overlay

### Badge Component
Small status indicators.

**Specifications:**
- Padding: 4-8px horizontal, 4px vertical
- Border Radius: 4px
- Font Size: 12px
- Font Weight: 600
- Color coding:
  - Green for positive/buy
  - Red for negative/sell
  - Blue for neutral/info

### Data Row Component
Label-value display pair.

**Layout:**
- Label: Left aligned, secondary text color
- Value: Right aligned, primary text color
- Separator: Horizontal line between items
- Height: ~32px
- Padding: 8px vertical, 0px horizontal

---

## LAYOUTS

### Screen Layout Structure

```
┌─────────────────────────────────┐
│         AppBar (56px)           │  ← Title centered, back + action
├─────────────────────────────────┤
│                                 │
│   Real-time Chart Card  (280px) │  ← Full width
│                                 │
├────────────────────┬────────────┤
│  AI Analysis       │ Asset Info │  ← 50/50 split row
│  Panel             │ Card       │
├────────────────────┴────────────┤
│                                 │
│      Metrics Grid (2-col)       │  ← 4 cards in 2x2
│                                 │
├─────────────────────────────────┤
│                                 │
│   SMA vs EMA Chart (200px)      │  ← Full width
│                                 │
└─────────────────────────────────┘
```

### Card Grid Layout
- **Columns**: 2
- **Cross Spacing**: 10-12px
- **Main Spacing**: 10-12px
- **Aspect Ratio**: Variable
- **Responsive**: Adjusts on tablet to 3-4 columns

### Typography Hierarchy in Card
1. **Card Title**: 18px, SemiBold, white
2. **Subheading**: 14px, SemiBold, white
3. **Labels**: 14px, Regular, secondary gray
4. **Values**: 14px, Mono Font, white (or color-coded)
5. **Captions**: 12px, Regular, tertiary gray

---

## BEST PRACTICES

### Color Usage
✅ **DO:**
- Use secondary gray for disabled/inactive states
- Apply profit green for gains, loss red for losses
- Use action blue consistently for primary CTA
- Maintain sufficient contrast (WCAG AA minimum)

❌ **DON'T:**
- Mix multiple accent colors in same card
- Use full opacity overlays
- Apply more than 2 colors per data point

### Spacing
✅ **DO:**
- Use multiples of 4px
- Maintain consistent padding (14-16px in cards)
- Add breathing room between sections
- Align elements to grid

❌ **DON'T:**
- Use arbitrary spacing values
- Overcrowd information
- Inconsistent padding between cards
- Ignore touch targets (min 48px)

### Typography
✅ **DO:**
- Use Inter for UI text
- Use Mono font for prices/data
- Maintain 1.2-1.5x line height
- Limit to 2-3 font weights per screen

❌ **DON'T:**
- Mix 4+ different font sizes
- Use light weights on dark backgrounds
- Exceed 60 characters per line (body text)
- Underline non-link text

### Charts
✅ **DO:**
- Use grid for reference
- Include tooltips on hover/tap
- Animate smooth transitions
- Provide data labels

❌ **DON'T:**
- Overcomplicate with 3D effects
- Use jarring colors
- Hide axis labels
- Skip loading states

### Responsive Design
✅ **DO:**
- Start mobile-first
- Test on multiple screen sizes
- Maintain readable text at all sizes
- Adjust layout for landscape

❌ **DON'T:**
- Force desktop layout on mobile
- Use fixed widths
- Ignore tablet optimization
- Skip accessibility testing

---

## IMPLEMENTATION CHECKLIST

- [ ] All colors match hex values exactly
- [ ] Spacing uses 4px base unit
- [ ] Cards have 12px border radius
- [ ] Internal card padding 14-16px
- [ ] Cards separated by 10-12px gap
- [ ] Typography matches specifications
- [ ] Touch targets minimum 48x48dp
- [ ] Animations smooth (200-500ms)
- [ ] Dark theme tested in high/low light
- [ ] Accessibility WCAG AA compliant
- [ ] Performance: <50ms render time
- [ ] FPS: Consistent 60fps scrolling

---

## FILES & RESOURCES

- `design_constants.dart` - Color/spacing definitions
- `fintech_theme.dart` - Material theme configuration
- `common_widgets.dart` - Reusable components
- `line_charts.dart` - Chart implementations
- `gauge_charts.dart` - Gauge/strength charts
- `trading_dashboard_screen.dart` - Main screen layout

---

**Version**: 1.0  
**Last Updated**: Feb 2026  
**Status**: Production Ready
