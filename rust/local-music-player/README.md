# Local MP3 Player

一个基于Tauri 2.0开发的本地MP3音乐播放器，使用Svelte + TypeScript作为前端，Rust作为后端API。

## 技术栈

- **前端**: Svelte + TypeScript
- **桌面框架**: Tauri 2.0
- **后端**: Rust
- **构建工具**: Bun
- **音频处理**: rodio (Rust)
- **元数据解析**: lofty (Rust)

## 功能特性

- 双面板界面：左侧目录管理，右侧播放列表
- 支持添加和管理本地音乐目录
- 自动扫描MP3文件并读取元数据（歌名、艺术家、专辑、音轨、时长）
- 完整的播放控制（播放/暂停、上一首/下一首、进度条）
- 支持顺序播放和随机播放模式
- 应用状态持久化

## 开发环境设置

### 前置要求

- [Rust](https://rustup.rs/) (最新稳定版)
- [Bun](https://bun.sh/) (JavaScript运行时和包管理器)
- [Tauri CLI](https://tauri.app/start/prerequisites/)

### 安装依赖

```bash
# 安装前端依赖
bun install

# 检查Rust依赖
cargo check --manifest-path src-tauri/Cargo.toml
```

### 开发模式

```bash
# 启动开发服务器
bun run tauri dev
```

### 构建应用

```bash
# 构建生产版本
bun run tauri build
```

## 项目结构

```
local-mp3-player/
├── src/                    # Svelte前端源码
├── src-tauri/             # Rust后端源码
│   ├── src/
│   │   ├── main.rs        # 应用入口
│   │   └── lib.rs         # 主要逻辑
│   ├── Cargo.toml         # Rust依赖配置
│   └── tauri.conf.json    # Tauri配置
├── static/                # 静态资源
├── package.json           # 前端依赖配置
└── README.md
```

## 开发状态

项目当前处于初始化阶段，基础项目结构和依赖已配置完成。

下一步将实现：
1. 核心数据模型和类型定义
2. 文件系统和目录管理功能
3. MP3文件扫描和元数据解析
4. 前端UI组件开发
5. 音频播放引擎集成

## 许可证

MIT License