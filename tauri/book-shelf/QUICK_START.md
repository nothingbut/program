# 🚀 快速启动指南

## 开发模式

### 1. 安装依赖
```bash
bun install
```

### 2. 启动开发服务器
```bash
bun run tauri dev
```

这将：
- 启动Vite开发服务器（端口1420）
- 编译并运行Rust后端
- 自动打开应用窗口

## 构建发布

### 构建当前平台
```bash
bun run tauri build
```

### 跨平台构建
```bash
# macOS
bun run tauri build --target x86_64-apple-darwin
bun run tauri build --target aarch64-apple-darwin

# Windows  
bun run tauri build --target x86_64-pc-windows-msvc

# Linux
bun run tauri build --target x86_64-unknown-linux-gnu
bun run tauri build --target aarch64-unknown-linux-gnu
```

## 数据库位置

数据库文件存储在：
- **macOS**: `~/Library/Application Support/com.bookshelf.app/bookshelf.db`
- **Linux**: `~/.local/share/com.bookshelf.app/bookshelf.db`
- **Windows**: `%APPDATA%\com.bookshelf.app\bookshelf.db`

## 常见问题

### 1. 编译错误
如果遇到编译错误，尝试：
```bash
# 清理构建缓存
cd src-tauri
cargo clean

# 重新构建
cargo build
```

### 2. 数据库初始化
首次运行时会自动创建数据库和表结构。

### 3. 权限问题
确保应用有权限访问文件系统以保存数据库。
