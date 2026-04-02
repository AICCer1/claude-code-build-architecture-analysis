# claude-code-build 架构深度分析

分析对象：`chenqinggang001/claude-code-build`

源码仓库：<https://github.com/chenqinggang001/claude-code-build>
本地路径：`/root/.openclaw/workspace/claude-code-build`

本仓库聚焦以下问题：

- 这个项目的整体架构是什么
- 主运行时如何组织
- Query / Tool / Hook / Memory / MCP / LSP / Agent / Team / State 等模块如何协作
- 各目录、关键文件和关键函数分别承担什么职责
- 如果要继续阅读源码，应该从哪里入手

---

## 阅读顺序

### 1. 全局架构
- [`docs/01-system-overview.md`](docs/01-system-overview.md)
- [`docs/02-runtime-control-flow.md`](docs/02-runtime-control-flow.md)
- [`docs/03-directory-and-module-map.md`](docs/03-directory-and-module-map.md)

### 2. 核心子系统
- [`docs/04-query-tool-hook-architecture.md`](docs/04-query-tool-hook-architecture.md)
- [`docs/05-memory-architecture.md`](docs/05-memory-architecture.md)
- [`docs/06-agent-task-team-architecture.md`](docs/06-agent-task-team-architecture.md)
- [`docs/07-extension-architecture.md`](docs/07-extension-architecture.md)
- [`docs/08-state-ui-session-architecture.md`](docs/08-state-ui-session-architecture.md)
- [`docs/10-dependency-views.md`](docs/10-dependency-views.md)

### 3. 文件与函数入口
- [`docs/09-file-and-function-guide.md`](docs/09-file-and-function-guide.md)
- [`docs/generated/key-file-symbols.md`](docs/generated/key-file-symbols.md)
- [`docs/generated/root-files.md`](docs/generated/root-files.md)
- [`docs/generated/directory-counts.md`](docs/generated/directory-counts.md)

---

## 一句话架构判断

这个项目不是“CLI + 几个工具”的简单组合，而是一套终端原生的 agent runtime 平台，核心由以下几个平面组成：

- Session / Query Runtime
- Tool Execution Plane
- Lifecycle / Governance Plane
- Memory / Context Plane
- Extension Plane（MCP / Skills / Plugins / LSP）
- Collaboration Plane（Agent / Task / Team）
- State / Persistence / Interaction Plane

---

## 最值得优先阅读的文件

1. `src/main.tsx`
2. `src/query.ts`
3. `src/QueryEngine.ts`
4. `src/Tool.ts`
5. `src/tools.ts`
6. `src/utils/hooks.ts`
7. `src/query/stopHooks.ts`
8. `src/memdir/memdir.ts`
9. `src/memdir/findRelevantMemories.ts`
10. `src/services/mcp/client.ts`
11. `src/services/lsp/manager.ts`
12. `src/tools/AgentTool/AgentTool.tsx`
13. `src/state/AppStateStore.ts`

---

## 自动索引

- 顶层目录文件计数：[`docs/generated/directory-counts.md`](docs/generated/directory-counts.md)
- 根层关键文件：[`docs/generated/root-files.md`](docs/generated/root-files.md)
- 关键符号索引：[`docs/generated/key-file-symbols.md`](docs/generated/key-file-symbols.md)
