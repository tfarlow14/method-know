# Design Tokens Reference

This document maps Figma design tokens to Tailwind CSS classes used in the application.

## Color Tokens

### From Figma
- `slate/900` → `#0F172A` → Tailwind: `slate-900`
- `slate/400` → `#94A3B8` → Tailwind: `slate-400`
- `slate/300` → `#CBD5E1` → Tailwind: `slate-300` (used for borders)

### Background Colors
- Background: `#FCFCFC` → Tailwind: `bg-background` (matches CSS variable `--background`)
- Card borders: `rgba(0,0,0,0.12)` → Tailwind: `border-slate-900/12`

## Typography Tokens

### From Figma
- **h2**: Inter, Semi Bold, 30px, weight 600, lineHeight 36, letterSpacing -0.75
- **h4**: Inter, Semi Bold, 20px, weight 600, lineHeight 28, letterSpacing -0.5
- **large**: Inter, Semi Bold, 18px, weight 600, lineHeight 28, letterSpacing 0
- **p-ui**: Inter, Regular, 16px, weight 400, lineHeight 24, letterSpacing 0
- **body-medium**: Inter, Medium, 14px, weight 500, lineHeight 24, letterSpacing 0
- **p**: Inter, Regular, 16px, weight 400, lineHeight 28, letterSpacing 0

### Implementation Notes
- Font family: Inter (loaded from Google Fonts)
- Font smoothing: `-webkit-font-smoothing: antialiased` and `-moz-osx-font-smoothing: grayscale` applied globally
- Negative letter-spacing values (e.g., `tracking-[-0.225px]`) are kept as arbitrary values since Tailwind doesn't provide negative tracking utilities

## Arbitrary Values

The following design-specific measurements are kept as arbitrary Tailwind values to match Figma exactly:

- `max-w-[480px]` - Card max-width (between Tailwind's `max-w-md` 448px and `max-w-lg` 512px)
- `mb-[13px]` - Spacing between icon and title in RegHeader (between `mb-3` 12px and `mb-4` 16px)
- `w-[66px] h-[66px]` - Logo circle size (between `w-16` 64px and `w-20` 80px)
- `w-[37px] h-[37px]` - Icon size (between `w-9` 36px and `w-10` 40px)
- `tracking-[-0.225px]` - h2 letter-spacing (negative values not in Tailwind scale)
- `tracking-[-0.1px]` - h4 letter-spacing (negative values not in Tailwind scale)
- `ring-[3px]` - Focus ring width (between `ring-2` 2px and `ring-4` 4px)

## Figma File

- File Key: `tMDx0V7W82hU9kNlUnmmMy`
- Design tokens can be retrieved using the Figma MCP server with `get_variable_defs`

