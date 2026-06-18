---
name: Institutional Transparency Framework
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#454652'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#767683'
  outline-variant: '#c6c5d4'
  surface-tint: '#4c56af'
  primary: '#000666'
  on-primary: '#ffffff'
  primary-container: '#1a237e'
  on-primary-container: '#8690ee'
  inverse-primary: '#bdc2ff'
  secondary: '#005faf'
  on-secondary: '#ffffff'
  secondary-container: '#54a0fe'
  on-secondary-container: '#003567'
  tertiary: '#1b1b1b'
  on-tertiary: '#ffffff'
  tertiary-container: '#303030'
  on-tertiary-container: '#999897'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e0e0ff'
  primary-fixed-dim: '#bdc2ff'
  on-primary-fixed: '#000767'
  on-primary-fixed-variant: '#343d96'
  secondary-fixed: '#d4e3ff'
  secondary-fixed-dim: '#a5c8ff'
  on-secondary-fixed: '#001c3a'
  on-secondary-fixed-variant: '#004786'
  tertiary-fixed: '#e4e2e1'
  tertiary-fixed-dim: '#c8c6c6'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#474747'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 57px
    fontWeight: '400'
    lineHeight: 64px
    letterSpacing: -0.25px
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  title-lg:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 28px
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0.15px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0.5px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0.25px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.1px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.5px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.5px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-margin-desktop: 24px
  container-margin-mobile: 16px
  gutter: 16px
  density-compact: 4px
  density-default: 8px
  density-comfortable: 16px
---

## Brand & Style
The design system is engineered for civic trust and administrative efficiency. It adopts a **Corporate / Modern** aesthetic, heavily influenced by Google’s Material Design 3 (MD3) principles, to provide a familiar and authoritative interface for government officials and the public. 

The focus is on **high data density** and **objective clarity**. By utilizing a minimalist white-label approach with crisp navy accents, the UI recedes to let complex budgetary data take center stage. The style is intentionally unadorned to evoke a sense of fiscal responsibility and institutional transparency, ensuring that users feel they are interacting with a stable, reliable record of public finance.

## Colors
The palette is rooted in "Institutional Navy" to project authority and stability. 

- **Primary (#1A237E):** Used for key navigational elements, headers, and primary actions.
- **Secondary (#1976D2):** A more vibrant corporate blue used for interactive states, links, and selection indicators.
- **Surface Palette:** The design system utilizes a "Pure White" (#FFFFFF) base for the main content area to maximize legibility. "Neutral Light Gray" (#F5F5F5) is used for sidebars and background panels to create subtle structural containment without visual clutter.
- **Semantic Alerts:** Soft Red (#E53935) and Amber (#FFB300) are reserved strictly for data anomalies, budget overruns, and system warnings. These colors must be used sparingly to maintain their psychological impact.

## Typography
This design system utilizes **Inter** for all typographic roles. Inter’s tall x-height and exceptional legibility make it ideal for the high-density data tables and financial spreadsheets found within the platform.

- **Headlines:** Set with slightly tighter letter spacing and medium-to-bold weights to establish a clear hierarchy.
- **Body Text:** Optimized for long-form reading of policy documents and budget descriptions.
- **Labels:** Used extensively for metadata, table headers, and status chips. The `label-sm` role is crucial for secondary data points in dense dashboards.
- **Numerical Data:** While using Inter, ensure the use of tabular (monospaced) figures where possible to ensure that columns of numbers align perfectly for easier visual auditing.

## Layout & Spacing
The design system employs a **12-column fluid grid** for desktop layouts and a **4-column fluid grid** for mobile. 

To handle enterprise-grade data density, the system uses a **4px base unit**. For financial dashboards and data grids, a "Compact" density model is preferred, utilizing 4px and 8px increments to maximize the information visible on a single screen. For public-facing informational pages, a "Comfortable" 16px rhythm is used to improve scannability.

**Breakpoints:**
- **Mobile:** 0 - 599px (Margins: 16px)
- **Tablet:** 600px - 1023px (Margins: 24px)
- **Desktop:** 1024px+ (Margins: 24px, Max-width: 1440px for content containers)

## Elevation & Depth
In alignment with Material Design 3, this design system prioritizes **Tonal Layers** over heavy shadows to define hierarchy.

- **Level 0 (Baseline):** The main canvas background, typically Pure White.
- **Level 1 (Surface):** Light Gray (#F5F5F5) panels used for side navigation or grouped content.
- **Level 2 (Cards):** White surfaces with a very subtle, diffused shadow (Blur: 4px, Y: 2px, Opacity: 4% Black) or a 1px neutral border (#E0E0E0).
- **Interactive Elevation:** Elements like buttons or active cards may use a slightly more pronounced shadow upon hover to indicate interactivity, but should never appear "floating" significantly far from the surface.

## Shapes
The shape language is disciplined and professional. 

- **Primary Components:** Buttons, input fields, and cards use a **0.5rem (8px)** corner radius. This provides a modern feel while remaining structured and institutional.
- **Small Components:** Chips, tags, and checkboxes use a slightly smaller radius or full pill-shape where appropriate (e.g., status indicators) to distinguish them from structural layout elements.
- **Data Tables:** These remain sharp or have minimal rounding (4px) to ensure that grid lines feel precise and mathematical.

## Components
Consistent component behavior is vital for a technical platform:

- **Data Tables:** The core component. Features includes fixed headers, zebra-striping using the neutral gray, and right-aligned numerical columns.
- **Buttons:** 
    - *Primary:* Solid Navy background with white text.
    - *Secondary:* Outlined blue or gray.
    - *Tertiary:* Ghost buttons for low-priority actions.
- **Input Fields:** Outlined style with floating labels (MD3 style). Use high-contrast borders (1px) for accessibility.
- **Status Chips:** High-visibility indicators for budget status (e.g., "Approved", "Pending", "Over Budget"). Use subtle background tints with bold foreground text.
- **Anomaly Alerts:** Inline banners or "toast" notifications using the Red and Amber semantic colors, always accompanied by a clear icon to ensure accessibility for color-blind users.
- **Progress Bars:** Linear indicators for budget consumption, using the primary blue for healthy spending and shifting to amber/red as limits are approached.