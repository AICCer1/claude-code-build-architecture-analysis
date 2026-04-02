# 10. 依赖视图与 C4 风格视角

## 10.1 Context View

```mermaid
flowchart TB
    User[开发者 / 用户]
    Runtime[claude-code-build Runtime]
    LLM[LLM API]
    FS[Filesystem / Git / Shell]
    MCP[MCP Servers]
    LSP[LSP Servers]
    IDE[IDE / Browser / Remote Session]

    User --> Runtime
    Runtime --> LLM
    Runtime --> FS
    Runtime --> MCP
    Runtime --> LSP
    Runtime --> IDE
```

系统位于用户、模型、本地执行环境、外部服务和远程交互渠道之间，起到统一编排层的作用。

---

## 10.2 Container View

```mermaid
flowchart LR
    subgraph Runtime[Runtime Containers]
      A[CLI / main.tsx]
      B[REPL / Ink UI]
      C[Query Runtime]
      D[Tool Execution]
      E[Hook / Governance]
      F[Memory / Context]
      G[Extension]
      H[Agent / Task / Team]
      I[State / Persistence]
    end

    A --> B
    A --> C
    C --> D
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    B --> I
    G --> D
    H --> I
```

---

## 10.3 Component View：Query Runtime

```mermaid
flowchart TD
    A[processUserInput] --> B[fetchSystemPromptParts]
    B --> C[queryLoop]
    C --> D[buildQueryConfig]
    C --> E[runTools]
    C --> F[handleStopHooks]
    E --> G[runToolUse]
    E --> H[StreamingToolExecutor]
    F --> I[executeStopHooks]
    F --> J[extractMemories / autoDream / promptSuggestion]
```

---

## 10.4 Component View：Memory Plane

```mermaid
flowchart TD
    A[paths.ts] --> B[memdir.ts]
    A --> C[teamMemPaths.ts]
    B --> D[loadMemoryPrompt]
    C --> E[team memory validation]
    F[memoryScan.ts] --> G[findRelevantMemories.ts]
    G --> H[sideQuery selector]
    D --> I[Query Runtime]
    G --> I
    I --> J[stopHooks -> extract memories]
```

---

## 10.5 Component View：Extension Plane

```mermaid
flowchart TD
    A[plugins] --> B[plugin loader]
    B --> C[plugin commands]
    B --> D[plugin skills]
    B --> E[plugin LSP]
    B --> F[plugin MCP]
    G[skills] --> H[skill commands / prompt rules]
    I[MCP client] --> J[MCP tools/resources/prompts]
    K[LSP manager] --> L[LSPTool / diagnostics]
    C --> M[commands.ts]
    D --> N[query/tool context]
    J --> O[tool pool]
    L --> O
```

---

## 10.6 Dependency Direction

```mermaid
flowchart LR
    UI[UI/Interaction] --> Runtime[Query Runtime]
    Runtime --> Tools[Tool Plane]
    Runtime --> Hooks[Hook Plane]
    Runtime --> Memory[Memory Plane]
    Runtime --> Ext[Extension Plane]
    Runtime --> Collab[Collaboration Plane]
    Runtime --> State[State/Persistence]
    Ext --> Tools
    Collab --> Tools
    Hooks --> Tools
    Hooks --> Runtime
```

### 依赖方向要点
- UI 不应直接决定业务语义，主要依赖 Runtime
- Runtime 调度 Tool / Hook / Memory / Extension / Collaboration
- State 为共享事实源，被多个平面读写
- Extension 最终多半要落回 Tool Plane 或 Context Layer

---

## 10.7 稳定边界与高变边界

```mermaid
quadrantChart
    title 稳定性与变更频率
    x-axis 低变更 --> 高变更
    y-axis 核心 --> 边缘
    quadrant-1 核心且高变
    quadrant-2 核心且低变
    quadrant-3 边缘且低变
    quadrant-4 边缘且高变
    Query Runtime: [0.45, 0.9]
    Tool Protocol: [0.35, 0.82]
    Hook Plane: [0.4, 0.8]
    Memory Plane: [0.5, 0.75]
    MCP/LSP: [0.65, 0.7]
    Commands: [0.72, 0.52]
    UI Components: [0.82, 0.35]
    Buddy/Voice/Bridge Shells: [0.88, 0.2]
```

说明：
- Query Runtime、Tool Protocol、Hook Plane 是核心结构
- UI、Buddy、Voice、Bridge 等壳层更偏边缘能力
- MCP/LSP/Skills/Plugins 虽属扩展，但对平台边界影响较大

---

## 10.8 结论

从依赖视角看，这个项目最重要的不是目录多，而是它已经形成较清晰的层次：

- Runtime 作为中心
- Tool / Hook / Memory / Extension / Collaboration 作为主要执行与扩展平面
- UI 与产品壳作为外层承载
- State / Persistence 作为跨平面的共享事实源

这也是它能够容纳 REPL、SDK、MCP、LSP、subagent、team 等多种能力的原因。