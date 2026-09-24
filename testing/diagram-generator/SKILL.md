---
name: diagram-generator
description: "Generate diagrams: architecture (SVG), flowchart, sequence, ER, attack-path, mind-map. Dispatcher to built-in tools."
---

# Diagram Generator (Dispatcher)

## ACTION REQUIRED

1. Determine diagram type from the user request.
2. Route to the correct built-in tool:

### Architecture / Infra / Cloud
Use `skill_view(name='architecture-diagram')` — dark-themed SVG output.

### Flowchart / Sequence / Attack-path / Mind-map / ER
Use `skill_view(name='excalidraw')` — hand-drawn style JSON, embeddable.

### Mermaid (text → rendered)
Use `npx -y @mermaid-js/mermaid-cli` if installed; fallback to Excalidraw.

## Keywords
diagram, mermaid, graphviz, plantuml, flowchart, architecture, sequence, ER,
attack-path, mind-map, data-flow, state-machine, UML, 画图, 图表, 流程图,
架构图, 时序图, 状态图, 攻击路径图
