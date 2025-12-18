---
description: Complete brand creation system - palette, typography, logos, code assets, visual guidelines, components, and social media kit
---

# Complete Brand Design System

Execute a comprehensive brand design workflow with automatic cleanup and organization.

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: COLOR PALETTE & TYPOGRAPHY GENERATION
═══════════════════════════════════════════════════════════════════════════════

Have **both Gemini and Codex** independently create:
1. Complete color palette (primary, secondary, tertiary, neutrals with hex codes)
2. Typography system (heading font, body font, size scales with line-heights)
3. Usage guidelines and rationale

**Agent Instructions:**
- Extract brand positioning from project CLAUDE.md or ask user
- Consider target audience demographics
- Think: luxury resort brands, premium magazines, high-end clubs
- Provide specific Google Fonts names and exact hex codes
- Include mobile and desktop typography scales

Save outputs to:
- `gemini-brand-palette.txt`
- `codex-brand-palette.txt`

═══════════════════════════════════════════════════════════════════════════════
PHASE 2: REVIEW & FINALIZE CORE BRAND
═══════════════════════════════════════════════════════════════════════════════

**Your task (Claude Code):**
1. Read both agent outputs
2. Analyze and compare:
   - Color psychology and brand alignment
   - Typography readability and sophistication
   - Completeness and detail level
   - Professional execution
3. Select the superior palette OR create hybrid combining best elements
4. Create comprehensive brand guide: `[PROJECT-NAME]-brand-palette.txt`

**Required sections in final palette:**
- All colors with hex codes, names, usage guidelines
- Complete typography system with scales and line-heights
- Design principles
- Specific usage examples (headlines, CTAs, body, UI elements)

**CLEANUP:** Delete intermediate files after finalizing:
```bash
rm -f gemini-brand-palette.txt codex-brand-palette.txt
```

═══════════════════════════════════════════════════════════════════════════════
PHASE 3: LOGO PROMPT GENERATION
═══════════════════════════════════════════════════════════════════════════════

Have **both Gemini and Codex** create 5 DALLE logo prompts each.

**Agent Requirements:**
1. FIRST read `[PROJECT-NAME]-brand-palette.txt`
2. Use EXACT hex codes from finalized palette
3. Match brand positioning and sophistication
4. Create minimal, timeless, premium concepts
5. Ensure scalability (favicon to hero sizes)
6. Avoid clipart, cartoons, overly literal imagery

**CRITICAL Prompt Format Requirements:**
- MUST start with "Generate" as first word
- MUST include the brand name in the prompt
- 3-4 detailed sentences per prompt
- Include specific hex codes from brand palette
- Specify professional quality: "vector logo," "minimalist professional branding," "clean modern design"
- Include scalability requirements: "suitable for favicon and hero sizes"
- Describe composition, negative space, and premium aesthetic
- Avoid amateur descriptors - use: "sophisticated," "editorial," "luxury branding"
- Ready to paste directly into DALLE

**Example quality prompt:**
"Generate a minimalist professional logo for [Brand Name] featuring an elegant monogram combining initials in a sophisticated serif typeface, set within a refined circular frame using Deep Court Green (#0F3D2E) and Sandstone Gold (#C59D5F) with generous negative space in Porcelain (#F7F5F1). Vector logo design with clean lines, luxury resort branding aesthetic, no gradients, perfectly balanced composition suitable for both favicon and large-scale applications. Editorial sophistication with timeless appeal."

Save outputs to:
- `logo-prompts-gemini.txt` (5 prompts, blank line separated)
- `logo-prompts-codex.txt` (5 prompts, blank line separated)

**KEEP THESE FILES** - User will use for DALLE generation

═══════════════════════════════════════════════════════════════════════════════
PHASE 4: CODE-READY ASSETS
═══════════════════════════════════════════════════════════════════════════════

Have **both Gemini and Codex** generate code files from the brand palette.

**Agent task:**
Create 3 files from `[PROJECT-NAME]-brand-palette.txt`:

1. **`brand-colors.css`** - CSS custom properties
   ```css
   :root {
     /* Primary Colors */
     --color-primary: #HEX;
     --color-primary-dark: #HEX;
     /* etc... */
   }
   ```

2. **`tailwind.config.js`** - Tailwind custom theme
   ```js
   module.exports = {
     theme: {
       extend: {
         colors: {
           primary: '#HEX',
           // etc...
         },
         fontFamily: {
           heading: ['Font Name', 'serif'],
           body: ['Font Name', 'sans-serif'],
         }
       }
     }
   }
   ```

3. **`design-tokens.json`** - Platform-agnostic tokens
   ```json
   {
     "color": {
       "primary": { "value": "#HEX" }
     },
     "typography": {
       "heading": { "fontFamily": "..." }
     }
   }
   ```

Save outputs to:
- `gemini-code-assets/` directory
- `codex-code-assets/` directory

**Your task:** Review both, choose the best-structured code, save to `/brand-assets/code/`

**CLEANUP:** Delete non-chosen code assets directory

═══════════════════════════════════════════════════════════════════════════════
PHASE 5: VISUAL GUIDELINES (PHOTOGRAPHY & ICONOGRAPHY)
═══════════════════════════════════════════════════════════════════════════════

Have **both Gemini and Codex** create visual style guidelines.

**Agent task:**
Create `visual-guidelines.md` including:

1. **Photography Direction**
   - Composition style (rule of thirds, symmetry, etc.)
   - Lighting (natural, dramatic, soft, etc.)
   - Color treatment (filters, overlays, saturation)
   - Subject matter (people, environments, products)
   - Mood and emotion
   - 5 stock photo search keyword sets
   - 3 detailed Midjourney/DALL-E prompts for hero images

2. **Iconography Style**
   - Icon style (line, filled, outlined, duotone)
   - Stroke weight and corner radius
   - Recommended icon library (Heroicons, Lucide, etc.)
   - Custom icon guidelines

3. **Patterns & Textures**
   - Background patterns (if applicable)
   - Texture overlays
   - Gradient directions and stops

Save outputs to:
- `gemini-visual-guidelines.md`
- `codex-visual-guidelines.md`

**Your task:** Combine best elements into `/brand-assets/visual-guidelines.md`

**CLEANUP:** Delete intermediate files

═══════════════════════════════════════════════════════════════════════════════
PHASE 6: COMPONENT LIBRARY
═══════════════════════════════════════════════════════════════════════════════

Have **both Gemini and Codex** create component design specifications.

**Agent task:**
Create `component-library.md` with detailed specs for:

1. **Buttons**
   - Primary, secondary, ghost, disabled states
   - Sizes (sm, md, lg)
   - Hover/focus/active states
   - Border radius, padding, font size

2. **Cards**
   - Container styles
   - Border, shadow, radius
   - Header, body, footer sections
   - Hover effects

3. **Forms**
   - Input fields (text, email, textarea)
   - Labels and helper text
   - Error states
   - Focus styles

4. **Navigation**
   - Header/navbar design
   - Mobile menu
   - Footer layout
   - Breadcrumbs

Include CSS/Tailwind code examples for each component.

Save outputs to:
- `gemini-components.md`
- `codex-components.md`

**Your task:** Review both, merge best patterns into `/brand-assets/component-library.md`

**CLEANUP:** Delete intermediate files

═══════════════════════════════════════════════════════════════════════════════
PHASE 7: SOCIAL MEDIA KIT
═══════════════════════════════════════════════════════════════════════════════

**Your task (Claude Code):**

1. **Analyze brand positioning** and determine the 3 most relevant NON-VIDEO platforms
   - Content blog → Instagram, Pinterest, Twitter/X
   - B2B SaaS → LinkedIn, Twitter/X, Facebook
   - E-commerce → Instagram, Facebook, Pinterest
   - Tech/Dev → Twitter/X, GitHub, LinkedIn
   - etc.

   **EXCLUDE video platforms**: YouTube, TikTok, Vimeo, or any platform requiring video content

2. Have **both Gemini and Codex** create social media specs for YOUR chosen 3 platforms

**Agent task:**
Create `social-media-kit.md` including:

For each of the 3 platforms:
- Profile image dimensions and specs
- Cover/banner dimensions (if applicable)
- Post image dimensions
- Story dimensions (Instagram only)
- Design guidelines (safe zones, text placement)
- Bio/description template
- 10-15 relevant hashtags/keywords
- Content pillar suggestions (3-5 post types)

Save outputs to:
- `gemini-social-media.md`
- `codex-social-media.md`

**Your task:** Combine into `/brand-assets/social-media-kit.md`

**CLEANUP:** Delete intermediate files

═══════════════════════════════════════════════════════════════════════════════
PHASE 8: PREVIEW & DOCUMENTATION
═══════════════════════════════════════════════════════════════════════════════

Have **both Gemini and Codex** create HTML preview pages.

**Agent task:**
Create 2 preview files:

1. **`typography-specimen.html`**
   - Display all heading sizes (H1-H6)
   - Body text samples at various sizes
   - Font pairing demonstrations
   - Line-height and spacing examples
   - Uses actual Google Fonts imports
   - Styled with brand colors

2. **`color-palette-preview.html`**
   - Visual swatches for all colors
   - Hex codes displayed
   - Color combinations examples
   - Accessibility contrast ratios
   - Usage examples (buttons, cards, text)

Save outputs to:
- `gemini-preview/` directory
- `codex-preview/` directory

**Your task:** Choose best previews, save to `/brand-assets/preview/`

**CLEANUP:** Delete non-chosen preview directory

═══════════════════════════════════════════════════════════════════════════════
FINAL FILE STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

After completion, organize files as:

```
/brand-assets/
├── [PROJECT-NAME]-brand-palette.txt        # Master brand guide
├── logo-prompts-gemini.txt                 # 5 DALLE prompts
├── logo-prompts-codex.txt                  # 5 DALLE prompts
├── code/
│   ├── brand-colors.css                    # CSS variables
│   ├── tailwind.config.js                  # Tailwind theme
│   └── design-tokens.json                  # Design tokens
├── visual-guidelines.md                     # Photography & iconography
├── component-library.md                     # Component specs + code
├── social-media-kit.md                      # 3 platforms (chosen by Claude)
└── preview/
    ├── typography-specimen.html
    └── color-palette-preview.html
```

All intermediate files (gemini-*, codex-*) should be deleted.

═══════════════════════════════════════════════════════════════════════════════
POST-COMPLETION REMINDERS
═══════════════════════════════════════════════════════════════════════════════

**IMPORTANT - Add to your working memory:**

When website development begins:
1. Move `/brand-assets/code/*` to appropriate website directories
   - WordPress theme directory
   - `/src/styles/` for React/Next.js
   - Root for Tailwind config
2. Use preview HTML files for reference, then delete
3. Keep master brand palette and guidelines for future reference
4. Archive or delete logo prompt files after logo is finalized

When brand is fully implemented:
- Delete unused logo prompts
- Delete preview HTML files
- Keep only: brand palette, visual guidelines, component library, social media kit
- Consider creating a single comprehensive brand-book.pdf

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE AGENT PROMPT (Phase 1)
═══════════════════════════════════════════════════════════════════════════════

```
You are a professional brand designer working on [PROJECT NAME].

Brand Positioning: [from CLAUDE.md]
Target Audience: [demographics]
Brand Voice: [characteristics]

Create a COMPLETE BRAND PALETTE:

1. COLOR PALETTE
   - Primary color (main brand color) with hex code
   - Secondary color (accent/CTA) with hex code
   - Tertiary colors (2-3 supporting) with hex codes
   - Neutral palette (5+ shades: backgrounds, text, borders) with hex codes
   - Usage guidelines for each color

2. TYPOGRAPHY SYSTEM
   - Heading font (H1-H6) - specific Google Fonts name
   - Body font - specific Google Fonts name
   - Font pairing rationale
   - Complete size scale (H1-H6, body, small text)
   - Line-heights for each size
   - Desktop and mobile scales

Be specific with exact hex codes and Google Font names.
Think: [luxury comparable brands]
```

═══════════════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════════════

Simply run: `/brand-design`

I will:
1. Extract brand info from CLAUDE.md (or ask you)
2. Execute all 8 phases with both agents
3. Review, compare, and select best outputs for each phase
4. Organize into clean `/brand-assets/` structure
5. Delete all intermediate files
6. Provide complete brand system ready for implementation

**Deliverables:**
- Comprehensive brand palette
- 10 logo prompts ready for DALLE
- Production-ready code (CSS, Tailwind, tokens)
- Visual guidelines (photography, icons, patterns)
- Component library with code examples
- Social media kit (3 platforms customized to your brand)
- Interactive HTML previews
