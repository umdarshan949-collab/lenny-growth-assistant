# Design System & UI/UX Specifications: The Lenny Growth Assistant

## 1. UI/UX Design Principles

### 1.1 Information Architecture & Layout Structure
The application employs a 3-column split layout designed for maximum focus and immediate feedback:
1. **Left Sidebar (280px)**: Global brand header, New Chat trigger, session list with active state indicators, and knowledge base indicator.
2. **Center Chat Panel (Flexible)**: Fixed top header with provider selector (`Ollama`, `Anthropic`, `OpenAI`), scrollable message stream with citation pills, action toolbar (Ship 30 skill, Demo HTML artifact), and persistent chat input.
3. **Right Artifact Viewer (50% Split)**: Side-by-side Claude-style panel rendering HTML/CSS artifacts in a sandboxed iframe or Markdown code preview.

```
+------------------+----------------------------------+----------------------------------+
| Sidebar (280px)  | Chat Main Panel (Flex)           | Artifact Viewer (50% Split)     |
|                  | Header: [Model Dropdown] [Badge] | Header: Title [Preview] [Code]   |
| [New Chat]       |                                  |                                  |
|                  | User: What is LNO framework?     | [ Sandboxed <iframe> Preview ]   |
| Sessions List:   |                                  |                                  |
| - Session 1      | Asst: Shreyas Doshi framework... | HTML / CSS rendered safely       |
| - Session 2      | [Citation Pill: Episode #18]     | without parent DOM access        |
|                  |                                  |                                  |
|                  | [Generate Ship 30 Essay]         |                                  |
|                  | [ Input Box ]            [Send]  |                                  |
+------------------+----------------------------------+----------------------------------+
```

---

## 2. Key Interaction States & UI Polish

### 2.1 Provider Selection & Dynamic Badges
- Selecting **Ollama** updates status badge to `OLLAMA Ready` (Green).
- Selecting **Anthropic** or **OpenAI** dynamically tests API key readiness and falls back to Ollama or local synthesis if keys are missing.

### 2.2 Grounded Citation Pills
- Assistant messages containing transcript evidence display expandable citation pills at the bottom.
- Each pill includes the **Podcast Title**, **Guest Name**, and exact **Quote Snippet**.

### 2.3 Side-by-Side Artifact Viewer
- Triggered automatically when an assistant response generates HTML (` ```html `) or Markdown (` ```markdown `).
- Features dual view tabs: **Preview** (live interactive rendering inside a sandboxed iframe) and **Code** (syntax-highlighted raw source code).

---

## 3. Visual Styling & Color Palette

- **Background Dark**: `#0f172a` (Slate 900)
- **Sidebar Background**: `#1e293b` (Slate 800)
- **Card Background**: `#334155` (Slate 700)
- **Primary Accent**: `#3b82f6` (Blue 500)
- **User Message Bubble**: `#2563eb` (Blue 600)
- **Assistant Message Bubble**: `#1e293b` (Slate 800) with `#334155` border
- **Text Main**: `#f8fafc` (Slate 50)
- **Text Muted**: `#94a3b8` (Slate 400)

---

## 4. Accessibility & Responsiveness

- **Keyboard Navigation**: Standard tab key navigation across dropdowns, buttons, and form inputs.
- **Screen Reader Labels**: Descriptive `aria-label` attributes on icon-only buttons.
- **Responsive Layout**: On mobile/tablet screens (<768px), the artifact viewer collapses into a slide-over modal drawer.
