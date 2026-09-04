# Agent Transcript 03: Claude-Style Artifact Viewer & Security Isolation

**Goal**: Implement an in-app side-by-side Artifact Viewer for generated HTML/CSS components and Markdown documents with iframe sandbox security.

## Actions Log
- Built split-screen layout in `frontend/index.html` and `frontend/style.css` with collapsible side panel.
- Implemented `detect_artifact_in_response` in `backend/routes/chat.py` to extract ````html` and ````markdown` code blocks automatically.
- Secured HTML rendering using an `<iframe>` container configured with `sandbox="allow-scripts"`.

## Security Rationale & Risk Mitigation
- **Untrusted Code Execution**: AI-generated HTML can contain malicious script tags or attempt parent DOM access.
- **Isolation Strategy**: Restricting iframe privileges via `sandbox="allow-scripts"` prevents parent DOM access, cookie theft, and cross-site scripting while allowing interactive component rendering.
