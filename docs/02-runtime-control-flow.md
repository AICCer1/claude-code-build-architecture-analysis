# 02. 运行时主线与控制流

## 2.1 启动路径

`main.tsx` 是整个系统的 composition root。它负责：

- 超早期 side effects（startup profiler、MDM raw read、keychain prefetch）
- 解析 CLI 参数和模式
- 初始化 settings、policy、auth、model、plugins、skills、MCP、LSP、commands、agents
- 进入 REPL、headless、SDK、remote、assistant 等路径

```mermaid
sequenceDiagram
    participant User
    participant Main as main.tsx
    participant Bootstrap as bootstrap/state
    participant Init as init/services
    participant Repl as REPL/launchRepl
    participant Engine as QueryEngine/query

    User->>Main: 启动 CLI / 输入参数
    Main->>Bootstrap: 初始化 cwd / session / flag state
    Main->>Init: settings / auth / policy / plugins / MCP / skills / agents
    Main->>Init: initializeLspServerManager()
    Main->>Repl: 交互模式
    Main->>Engine: 非交互/SDK 模式
```

---

## 2.2 REPL 路径与 SDK 路径

### REPL 路径
- 以 `launchRepl()` 为入口
- 带完整 Ink UI、footer、notifications、command mode、task panel
- 对话中的消息、工具进度和系统附件都会投射到可交互界面

### SDK / Headless 路径
- 以 `QueryEngine.submitMessage()` 为入口
- 将完整 query 生命周期封装成可嵌入会话引擎
- 适合 print / SDK / automation 场景

```mermaid
flowchart TB
    A[main.tsx] --> B{运行模式}
    B -->|interactive| C[launchRepl]
    B -->|print/sdk/headless| D[QueryEngine.submitMessage]
    C --> E[query.ts::queryLoop]
    D --> E
```

---

## 2.3 Query 主循环

`query.ts` 中的 `query()` / `queryLoop()` 是系统最关键的控制流。

### Query Loop 负责的问题
- 组装 systemPrompt、userContext、systemContext
- 归一化消息历史
- 调用模型
- 接收 assistant/tool_use 流
- 分派工具执行
- 应用 tool_result budget、compact、fallback、stop hook 等机制

```mermaid
flowchart TD
    A[输入消息/上下文] --> B[buildQueryConfig]
    B --> C[prependUserContext / appendSystemContext]
    C --> D[调用模型 API]
    D --> E{返回内容}
    E -->|assistant text only| F[handleStopHooks]
    E -->|tool_use blocks| G[runTools / StreamingToolExecutor]
    G --> H[tool_result 回填 messages]
    H --> I[继续下一轮 queryLoop]
    F --> J[结束本轮]
```

---

## 2.4 QueryEngine 的角色

`QueryEngine.ts` 不是另起一套逻辑，而是 headless / SDK 路径对 query runtime 的封装。

### 它维护的状态
- `mutableMessages`
- `readFileState`
- `permissionDenials`
- `totalUsage`
- `discoveredSkillNames`
- `loadedNestedMemoryPaths`

### `submitMessage()` 的作用
- 准备一次会话 turn
- 调 `processUserInput(...)`
- 构建 system prompt parts
- 调 `query(...)`
- 记录 transcript 与 usage
- 产出 SDKMessage 流

```mermaid
sequenceDiagram
    participant Caller
    participant QE as QueryEngine
    participant Input as processUserInput
    participant Context as fetchSystemPromptParts
    participant Query as query()
    participant Store as sessionStorage

    Caller->>QE: submitMessage(prompt)
    QE->>Input: 处理输入、附件、memory、commands
    QE->>Context: 拉 systemPrompt/userContext/systemContext
    QE->>Query: 进入主 query loop
    Query-->>QE: stream events / messages / tool results
    QE->>Store: recordTranscript / flushSessionStorage
    QE-->>Caller: SDKMessage 流
```

---

## 2.5 Tool 执行主线

工具执行由 `services/tools/*` 系列文件承接。

### 关键文件
- `toolOrchestration.ts`
- `StreamingToolExecutor.ts`
- `toolExecution.ts`
- `toolHooks.ts`

### 关键分层
1. **分批**：按并发安全性拆 batch
2. **串行/并行**：并发安全工具可并发，其余必须串行
3. **单工具执行**：真正跑 `runToolUse()`
4. **前后钩子**：PreToolUse / PostToolUse / Failure hooks

```mermaid
flowchart LR
    A[tool_use blocks] --> B[partitionToolCalls]
    B --> C[runToolsConcurrently]
    B --> D[runToolsSerially]
    C --> E[runToolUse]
    D --> E
    E --> F[toolHooks]
    F --> G[message/tool_result/contextModifier]
```

---

## 2.6 StreamingToolExecutor 的作用

当 assistant 以流式形式逐步吐出 `tool_use` 时，系统不会等所有内容结束后再执行，而是用 `StreamingToolExecutor` 边接收边调度。

### 它维护的状态
- `queued`
- `executing`
- `completed`
- `yielded`
- sibling error / user interrupted / streaming fallback 等状态

### 关键机制
- 并发安全工具可同时执行
- 非并发安全工具独占执行
- 一旦发生 sibling error，其他并行工具可能被合成错误中断

```mermaid
stateDiagram-v2
    [*] --> queued
    queued --> executing: concurrency condition met
    executing --> completed: runToolUse done
    completed --> yielded: results emitted
    executing --> completed: synthetic error
```

---

## 2.7 Stop 阶段

`query/stopHooks.ts` 把“回合结束”独立建模成一个正式阶段。

### 主要职责
- 构造 stopHookContext
- 保存 cache-safe params
- 执行 stop hooks
- 执行 prompt suggestion / extract memories / auto-dream / cleanup 等后台逻辑
- 产出 stop summary 和 blocking errors

```mermaid
flowchart TD
    A[回合结束条件触发] --> B[handleStopHooks]
    B --> C[saveCacheSafeParams]
    B --> D[executeStopHooks]
    B --> E[executePromptSuggestion]
    B --> F[executeExtractMemories]
    B --> G[executeAutoDream]
    D --> H[blocking error / preventContinuation / summary]
    H --> I[Query Runtime 收口]
```

---

## 2.8 主控制权分布

```mermaid
flowchart LR
    Q[Query Runtime] -->|决定何时调用| T[Tool Plane]
    H[Hook Plane] -->|治理执行过程| T
    H -->|治理回合结束| Q
    M[Memory Plane] -->|提供上下文与相关记忆| Q
    A[Agent/Task/Team] -->|作为高级工具和协作层| Q
    S[State/Persistence] -->|持有共享事实源| Q
```

- **Query Runtime**：拥有主流程推进权
- **Tool Plane**：拥有执行权
- **Hook Plane**：拥有治理权
- **State/Persistence**：持有共享状态，但不直接主导控制流

---

## 2.9 关键结论

1. `main.tsx` 负责装配，不负责核心业务语义
2. `query.ts` / `QueryEngine.ts` 负责会话生命周期和 turn 控制权
3. `services/tools/*` 是独立执行平面，不是 query 的小分支
4. `stopHooks.ts` 使回合结束成为正式生命周期阶段
5. REPL 与 SDK 共享同一套 runtime 核心语义，只是在承载层上不同