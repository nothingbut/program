# AGENTS.md - 本地 MP3 播放器编码指南

本文档为在这个 Tauri + Svelte 应用中进行 AI 辅助编码提供构建命令和代码风格规范。

---

## 构建、检查和测试命令

### 开发模式
```bash
bun run dev              # 前端开发服务器（端口 1420）
bun run tauri:dev        # 完整的 Tauri 应用开发模式
```

### 构建命令
```bash
bun run build            # 使用 Vite 构建前端
bun run tauri:build      # 构建 Tauri 应用（生产版本）
bun run build:all        # 同时构建前端和 Tauri
bun run tauri:build:debug  # 调试构建（包含符号）
```

### 类型检查
```bash
bun run check            # 运行 Svelte 类型检查
bun run check:watch      # 类型检查监视模式
```

### 单元测试（Vitest）
```bash
bun run test             # 运行所有单元测试
bun run test:watch       # 单元测试监视模式
bun run test <路径>      # 运行单个测试文件：bun run test src/lib/stores/playlist.test.ts
```

### 端到端测试（Playwright）
```bash
bun run test:e2e         # 运行所有 E2E 测试
bun run test:e2e:ui      # 交互式 UI 模式
bun run test:e2e:headed  # 显示浏览器窗口
bun run test:e2e:debug   # 调试模式（可步进）
bunx playwright test <文件>  # 运行单个测试：bunx playwright test tests/e2e/complete-user-workflow.spec.ts
```

---

## 代码风格规范

### TypeScript / Svelte

**文件命名：**
- 组件：PascalCase - `PlayerControls.svelte`
- 工具模块：lowercase_with_underscore - `stores/playlist.ts`、`utils/window.ts`
- 测试文件：`*.test.ts` 或 `*.spec.ts`

**导入顺序：**
1. 外部库（npm 包）
2. 内部模块（来自 `src/lib/` 或 `$lib/`）
3. 相对导入（`./`、`../`）

```typescript
// ✅ 推荐
import { invoke } from '@tauri-apps/api/core';
import { _, locale } from 'svelte-i18n';
import { playbackApi } from '$lib/api';
import { createAppError } from './errors';

// ❌ 不推荐 - 顺序混乱
import { createAppError } from './errors';
import { invoke } from '@tauri-apps/api/core';
```

**类型和接口：**
- 共享类型定义在 `src/lib/types.ts` 中
- 使用具名导出（named exports），避免默认导出
- 组件 Props 使用 TypeScript 接口定义

```typescript
export interface Directory {
  id: string;
  path: string;
  name: string;
  addedAt: string;
}

export interface Track {
  id: string;
  filePath: string;
  title: string;
  artist: string;
  album: string;
  trackNumber?: number;
  duration: number;
  coverArt?: string;
}
```

**Svelte 5 响应式：**
- 使用 `$state()` 声明本地响应式状态
- 使用 `$derived` 创建计算值
- 极少使用 `$effect` 处理副作用

```typescript
let count = $state(0);
let double = $derived(count * 2);
```

**错误处理：**
- 使用 `src/lib/errors.ts` 中的类型化错误对象
- 通过 `ErrorCategory` 枚举分类错误（NETWORK、FILE_SYSTEM、AUDIO_PLAYBACK、METADATA、PERSISTENCE、USER_INPUT、SYSTEM）
- 指定 `ErrorSeverity`（INFO、WARNING、ERROR、CRITICAL）
- 在适用场景提供恢复操作

```typescript
import { createAppError, ErrorCategory, ErrorSeverity } from '$lib/errors';

const error = createAppError(
  '扫描目录失败',
  '无法访问音乐文件夹',
  ErrorCategory.FILE_SYSTEM,
  ErrorSeverity.ERROR,
  { context: { path: '/music' } }
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
pub mod errors;
pub mod models;
pub mod persistence;

pub use audio_player::{AudioPlayer, PlaybackEvent};
pub use errors::{AppError, AppResult};
pub use models::{Directory, Track};
```

**错误处理：**
- 使用 `#[derive(Debug, Error)]` 定义错误枚举
- 使用 `Result<T, AppError>` 作为 `AppResult<T>` 类型别名
- 实现 `IntoTauriResult` trait 以兼容 Tauri

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("文件系统错误: {0}")]
    FileSystem(#[from] std::io::Error),
    
    #[error("曲目未找到: {0}")]
    TrackNotFound(String),
    
    #[error("音频元数据错误: {0}")]
    Metadata(String),
    
    #[error("音频播放错误: {0}")]
    Playback(String),
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
    audio_player
        .play_track(track)
        .await
        .map_err(|e| e.to_string())
}
```

**命名约定：**
- 函数/变量：snake_case
- 类型/结构体/枚举：PascalCase
- 常量：SCREAMING_SNAKE_CASE
- 模块名：snake_case

**异步操作：**
- 使用 `async fn` 声明异步函数
- 使用 `.await` 等待异步操作
- 使用 `tokio` 运行时处理并发

```rust
pub async fn scan_directory(&self, path: &Path) -> AppResult<Vec<Track>> {
    let entries = fs::read_dir(path).await?;
    // 处理条目...
    Ok(tracks)
}
```

### 测试

**单元测试：**
- 将测试文件放在 `__tests__` 目录中，与源文件并列
- 使用 Vitest 的 `describe`、`it`、`expect`
- 测试环境中自动模拟 Tauri API

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { playlistActions, currentPlaylist } from '../index';

describe('播放列表管理器', () => {
  beforeEach(() => {
    playlistActions.clearPlaylist();
  });

  it('应该正确添加曲目', () => {
    const tracks = [
      { id: '1', filePath: '/test.mp3', title: 'Test', artist: 'Artist', album: 'Album', duration: 180 }
    ];
    playlistActions.setPlaylist(tracks);
    expect(get(currentPlaylist)).toHaveLength(1);
  });
});
```

**端到端测试：**
- 将测试放在 `tests/e2e/` 目录中
- 使用 Playwright 并配合 `data-testid` 属性
- 运行单个测试：`bunx playwright test tests/e2e/complete-user-workflow.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('添加目录并播放音乐', async ({ page }) => {
  await page.goto('http://localhost:1420');
  await page.click('[data-testid="add-directory-button"]');
  // 更多测试步骤...
});
```

### 其他规范

**注释：**
- 公共函数使用 JSDoc 风格注释
- 保持注释简洁准确
- 避免显而易见的注释

```typescript
/**
 * 添加目录到音乐库
 * @param path 目录路径
 * @returns 添加的目录对象
 */
async function addDirectory(path: string): Promise<Directory> {
  // 实现...
}
```

**Rust 注释：**
- 使用 `///` 为公开函数添加文档注释
- 使用 `//` 为行内代码添加说明

```rust
/// 扫描目录中的音频文件并提取元数据
pub async fn scan_directory(&self, path: &Path) -> AppResult<Vec<Track>> {
    // 验证路径存在性
    if !path.exists() {
        return Err(AppError::DirectoryNotFound(path.display().to_string()));
    }
    // ...
}
```

**格式化：**
- TypeScript：2 空格缩进
- 每行最大长度约 100 字符
- 逻辑段之间保留空行
- Rust：4 空格缩进

**国际化：**
- 所有 UI 文本使用 `svelte-i18n`
- 翻译存储在语言环境文件中
- 使用 `$_()` 和 `locale` stores

```typescript
import { _ } from 'svelte-i18n';
const title = $_('player.title');
```

---

## 项目结构概览

```
local-mp3-player/
├── src/                          # Svelte 前端源码
│   ├── lib/                      # 核心库
│   │   ├── stores/               # Svelte stores（状态管理）
│   │   │   ├── playlist.ts       # 播放列表状态
│   │   │   ├── playback.ts       # 播放控制状态
│   │   │   ├── directories.ts    # 目录管理状态
│   │   │   ├── __tests__/        # 单元测试
│   │   ├── components/           # Svelte 组件
│   │   │   ├── DirectoryPanel.svelte
│   │   │   ├── PlaylistPanel.svelte
│   │   │   ├── PlayerControls.svelte
│   │   │   └── ToastNotifications.svelte
│   │   ├── types.ts              # TypeScript 类型定义
│   │   ├── api.ts                # Tauri API 调用封装
│   │   ├── errors.ts            # 错误处理系统
│   │   └── utils/               # 工具函数
│   ├── routes/                   # SvelteKit 路由
│   ├── App.svelte                # 主应用组件
│   └── app.html                  # HTML 模板
├── src-tauri/                    # Rust 后端源码
│   ├── src/
│   │   ├── lib.rs                # Tauri 命令和主逻辑
│   │   ├── audio_player.rs       # 音频播放器
│   │   ├── directory_manager.rs  # 目录管理
│   │   ├── models.rs             # 数据模型
│   │   ├── errors.rs             # Rust 错误类型
│   │   ├── persistence.rs        # 状态持久化
│   │   └── mp3_analyzer.rs      # MP3 文件分析
│   ├── Cargo.toml               # Rust 依赖配置
│   └── tauri.conf.json          # Tauri 配置
├── tests/                        # 端到端测试
│   └── e2e/                     # Playwright 测试
├── static/                       # 静态资源
├── package.json                  # 前端依赖和脚本
├── tsconfig.json                 # TypeScript 配置
├── svelte.config.js              # Svelte 配置
├── vite.config.js                # Vite 配置
└── playwright.config.ts           # Playwright 配置
```

---

## 重要提醒

1. **严格模式**：TypeScript 配置启用了严格类型检查，确保类型安全
2. **异步操作**：文件扫描、元数据解析等耗时操作必须使用 async/await
3. **错误恢复**：用户可见的错误必须提供友好的错误消息和恢复选项
4. **无 SSR**：应用使用静态适配器，不支持服务端渲染
5. **端口固定**：开发服务器固定使用 1420 端口，避免冲突
6. **包管理器**：使用 Bun 作为主要的包管理器和运行时
7. **音频格式**：支持 MP3、FLAC、OGG、M4A、WAV 格式
8. **元数据解析**：使用 id3 库解析 MP3 文件的 ID3 标签

---

## 技术栈参考

- **前端**：Svelte 5 + TypeScript + SvelteKit
- **后端**：Rust + Tauri 2.0
- **音频处理**：rodio (Rust)
- **元数据解析**：id3 (Rust)
- **构建工具**：Vite + Bun
- **测试**：Vitest (单元测试) + Playwright (E2E)
- **国际化**：svelte-i18n
