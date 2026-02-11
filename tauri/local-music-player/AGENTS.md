# AGENTS.md - 本地 MP3 播放器编码指南

本文档为 Tauri + Svelte 应用提供构建命令和代码风格规范。

---

## 构建命令

### 开发
```bash
bun run dev              # 前端开发服务器（端口 1420）
bun run tauri:dev        # 完整的 Tauri 应用开发模式
```

### 构建
```bash
bun run build            # Vite 构建前端
bun run tauri:build      # Tauri 生产版本
bun run build:all        # 同时构建前端和 Tauri
```

### 类型检查
```bash
bun run check            # Svelte 类型检查
bun run check:watch      # 监视模式
```

### 单元测试（Vitest）
```bash
bun run test             # 运行所有测试
bun run test:watch       # 监视模式
bun run test <路径>      # 单个文件：bun run test src/lib/stores/playlist.test.ts
```

### E2E 测试（Playwright）
```bash
bun run test:e2e         # 运行所有 E2E 测试
bun run test:e2e:ui      # 交互式 UI 模式
bun run test:e2e:headed  # 显示浏览器窗口
bun run test:e2e:debug   # 调试模式
bunx playwright test <文件>  # 单个测试：bunx playwright test tests/e2e/complete-user-workflow.spec.ts
```

---

## 代码风格规范

### TypeScript / Svelte

**文件命名：**
- 组件：`PlayerControls.svelte`（PascalCase）
- 工具模块：`stores/playlist.ts`（lowercase_with_underscore）
- 测试文件：`*.test.ts` 或 `*.spec.ts`

**导入顺序：**
1. 外部库（npm 包）
2. 内部模块（`src/lib/` 或 `$lib/`）
3. 相对导入（`./`、`../`）

```typescript
// ✅ 推荐
import { invoke } from '@tauri-apps/api/core';
import { _, locale } from 'svelte-i18n';
import { playbackApi } from '$lib/api';
import { createAppError } from './errors';
```

**Svelte 5 响应式：**
- 使用 `$state()` 声明本地响应式状态
- 使用 `$derived` 创建计算值
- 极少使用 `$effect`

```typescript
let count = $state(0);
let double = $derived(count * 2);
```

**错误处理：**
- 使用 `src/lib/errors.ts` 中的类型化错误对象
- 通过 `ErrorCategory` 分类错误（NETWORK、FILE_SYSTEM、AUDIO_PLAYBACK、METADATA、PERSISTENCE、USER_INPUT、SYSTEM）
- 指定 `ErrorSeverity`（INFO、WARNING、ERROR、CRITICAL）

```typescript
import { createAppError, ErrorCategory, ErrorSeverity } from '$lib/errors';

const error = createAppError(
  '扫描目录失败',
  '无法访问音乐文件夹',
  ErrorCategory.FILE_SYSTEM,
  ErrorSeverity.ERROR
);
```

### Rust (src-tauri/)

**模块组织：**
- 使用 `pub mod module_name;` 声明模块
- 使用 `pub use` 重新导出常用类型
- 使用 `thiserror` 创建自定义错误枚举

```rust
pub mod audio_player;
pub mod directory_manager;
pub use audio_player::{AudioPlayer, PlaybackEvent};
pub use errors::{AppError, AppResult};
```

**错误处理：**
- 使用 `#[derive(Debug, Error)]` 定义错误枚举
- 使用 `Result<T, AppError>` 作为 `AppResult<T>` 类型别名

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("文件系统错误: {0}")]
    FileSystem(#[from] std::io::Error),
    #[error("曲目未找到: {0}")]
    TrackNotFound(String),
}

pub type AppResult<T> = Result<T, AppError>;
```

**Tauri 命令：**
- 使用 `#[tauri::command]` 标记函数
- 使用 `State` 进行依赖注入
- 返回 `Result<T, String>` 以兼容 Tauri

```rust
#[tauri::command]
async fn play_track(
    track: Track,
    audio_player: State<'_, AudioPlayer>
) -> Result<(), String> {
    audio_player.play_track(track).await.map_err(|e| e.to_string())
}
```

**命名约定：**
- 函数/变量：snake_case
- 类型/结构体/枚举：PascalCase
- 常量：SCREAMING_SNAKE_CASE

### 测试

**单元测试：**
- 测试文件放在 `__tests__` 目录中，与源文件并列
- 使用 Vitest 的 `describe`、`it`、`expect`
- 测试环境中自动模拟 Tauri API

**E2E 测试：**
- 测试放在 `tests/e2e/` 目录中
- 使用 Playwright 并配合 `data-testid` 属性
- 运行单个测试：`bunx playwright test tests/e2e/complete-user-workflow.spec.ts`

---

## 项目结构

```
local-mp3-player/
├── src/                          # Svelte 前端源码
│   ├── lib/
│   │   ├── stores/               # Svelte stores（状态管理）
│   │   │   └── __tests__/        # 单元测试
│   │   ├── components/           # Svelte 组件
│   │   ├── types.ts              # TypeScript 类型定义
│   │   ├── api.ts                # Tauri API 调用封装
│   │   └── errors.ts            # 错误处理系统
│   └── routes/                   # SvelteKit 路由
├── src-tauri/                    # Rust 后端源码
│   ├── src/
│   │   ├── lib.rs                # Tauri 命令和主逻辑
│   │   ├── audio_player.rs       # 音频播放器
│   │   ├── directory_manager.rs  # 目录管理
│   │   ├── models.rs             # 数据模型
│   │   ├── errors.rs             # Rust 错误类型
│   │   ├── persistence.rs        # 状态持久化
│   │   └── mp3_analyzer.rs      # MP3 文件分析
│   └── Cargo.toml
└── tests/e2e/                    # Playwright E2E 测试
```

---

## 重要提醒

1. **严格模式**：TypeScript 配置启用了严格类型检查
2. **异步操作**：文件扫描、元数据解析等耗时操作必须使用 async/await
3. **错误恢复**：用户可见的错误必须提供友好的错误消息和恢复选项
4. **无 SSR**：应用使用静态适配器，不支持服务端渲染
5. **端口固定**：开发服务器固定使用 1420 端口
6. **包管理器**：使用 Bun 作为主要的包管理器和运行时
7. **音频格式**：支持 MP3、FLAC、OGG、M4A、WAV 格式
8. **元数据解析**：使用 id3 库解析 MP3 文件的 ID3 标签

---

## 技术栈

- **前端**：Svelte 5 + TypeScript + SvelteKit
- **后端**：Rust + Tauri 2.0
- **音频处理**：rodio (Rust)
- **元数据解析**：id3 (Rust)
- **构建工具**：Vite + Bun
- **测试**：Vitest (单元测试) + Playwright (E2E)
- **国际化**：svelte-i18n
