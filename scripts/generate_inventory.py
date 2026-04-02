from pathlib import Path
import re
src = Path('/root/.openclaw/workspace/claude-code-build/src')
out = Path('/root/.openclaw/workspace/claude-code-build-architecture-analysis/docs/generated')
out.mkdir(parents=True, exist_ok=True)

# directory counts
notes = {
'assistant':'assistant mode / KAIROS 相关实现',
'bootstrap':'启动期与进程级状态',
'bridge':'远程桥接 / remote control',
'buddy':'companion / observer UI',
'cli':'CLI 子入口和非交互支持',
'commands':'命令控制面',
'components':'Ink/React 组件',
'constants':'常量与 prompt 片段',
'context':'上下文提供层',
'coordinator':'协调器模式 / team orchestration',
'entrypoints':'SDK / agent entrypoints',
'hooks':'UI hooks / React hooks',
'ink':'终端渲染层',
'jobs':'job / template 相关',
'keybindings':'按键绑定',
'memdir':'memory / MEMORY.md 体系',
'migrations':'迁移',
'outputStyles':'输出样式',
'plugins':'插件入口',
'proactive':'主动模式 / background automation',
'query':'query runtime 辅助模块',
'remote':'远程 session',
'schemas':'schema',
'screens':'页面级 UI',
'services':'服务层',
'skills':'skills 体系',
'src':'-',
'state':'共享应用状态',
'tasks':'任务系统',
'tools':'工具系统',
'types':'共享类型',
'utils':'横切基础设施',
'voice':'语音模式',
'vim':'vim 模式',
}
lines = ['# 目录文件计数', '', '| 目录 | 文件数 | 说明 |', '|---|---:|---|']
for p in sorted([x for x in src.iterdir() if x.is_dir()]):
    count = sum(1 for f in p.rglob('*') if f.is_file())
    lines.append(f'| `{p.name}` | {count} | {notes.get(p.name, "-")} |')
(out / 'directory-counts.md').write_text('\n'.join(lines), encoding='utf-8')

# root files
root_notes = {
'main.tsx':'CLI/REPL 启动总入口',
'query.ts':'query 主循环',
'QueryEngine.ts':'SDK/headless 会话引擎',
'Tool.ts':'工具协议与 ToolUseContext',
'tools.ts':'工具池装配',
'commands.ts':'命令总表装配',
'Task.ts':'任务抽象',
'tasks.ts':'任务出口',
'replLauncher.tsx':'REPL 启动',
'interactiveHelpers.tsx':'交互辅助',
'context.ts':'系统/用户上下文',
}
lines = ['# 根层关键文件', '', '| 文件 | 作用 |', '|---|---|']
for f in sorted(src.glob('*')):
    if f.is_file():
        lines.append(f'| `{f.name}` | {root_notes.get(f.name, "-")} |')
(out / 'root-files.md').write_text('\n'.join(lines), encoding='utf-8')

# key symbols
candidate_files = [
    src / 'main.tsx', src / 'query.ts', src / 'QueryEngine.ts', src / 'Tool.ts', src / 'tools.ts', src / 'commands.ts',
    src / 'query' / 'stopHooks.ts',
    src / 'utils' / 'hooks.ts',
    src / 'services' / 'mcp' / 'client.ts',
    src / 'services' / 'lsp' / 'manager.ts',
    src / 'state' / 'AppStateStore.ts',
    src / 'memdir' / 'memdir.ts',
    src / 'memdir' / 'findRelevantMemories.ts',
    src / 'tools' / 'AgentTool' / 'AgentTool.tsx',
    src / 'services' / 'tools' / 'toolOrchestration.ts',
    src / 'services' / 'tools' / 'StreamingToolExecutor.ts',
]
pat = re.compile(r'^(export\s+)?(async\s+)?(function|class)\s+([A-Za-z0-9_]+)|^(export\s+)?const\s+([A-Za-z0-9_]+)\s*=')
lines = ['# 关键文件导出/符号索引', '']
for f in candidate_files:
    if not f.exists():
        continue
    rel = f.relative_to(src)
    lines.append(f'## `{rel}`')
    lines.append('')
    lines.append('| 行号 | 符号 |')
    lines.append('|---:|---|')
    found = 0
    for i, line in enumerate(f.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
        m = pat.match(line.strip())
        if m:
            name = m.group(4) or m.group(6)
            lines.append(f'| {i} | `{name}` |')
            found += 1
    if found == 0:
        lines.append('| - | *(无简单匹配结果)* |')
    lines.append('')
(out / 'key-file-symbols.md').write_text('\n'.join(lines), encoding='utf-8')
