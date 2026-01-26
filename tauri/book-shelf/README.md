# 📚 本地书架

一个简洁的本地小说管理工具，支持TXT文件导入、章节浏览和搜索功能。

## ✨ 功能特性

- 📖 **书籍管理**: 导入、删除、重命名网络小说
- 📂 **分类管理**: 树形分类结构，支持多级分类
- 📑 **章节浏览**: 自动识别章节，快速导航
- 🔍 **全文搜索**: 搜索书籍标题、作者、章节内容
- 💾 **数据备份**: SQLite数据库本地存储
- 🖥️ **跨平台**: 支持 Windows、macOS、Linux
- ⌨️ **快捷键**: 支持常用快捷键操作

## 🚀 快速开始

### 环境要求

- [Bun](https://bun.sh) 1.0+
- [Rust](https://rust-lang.org) 1.77+
- [Node.js](https://nodejs.org) 18+

### 安装依赖

```bash
bun install
```

### 开发模式

```bash
bun run tauri dev
```

### 构建发布

```bash
# 构建所有平台
bun run tauri build

# 构建特定平台
bun run tauri build --target x86_64-pc-windows-msvc  # Windows
bun run tauri build --target x86_64-apple-darwin     # macOS
bun run tauri build --target x86_64-unknown-linux-gnu # Linux
```

## 📖 使用说明

### 导入书籍

1. 点击菜单栏 **文件 → 导入书籍** 或使用快捷键 `Ctrl+O`
2. 选择要导入的TXT文件
3. 系统将自动识别章节并添加到书库

### 章节导航

1. 在左侧树状视图中选择一本书籍
2. 中间列表显示该书籍的所有章节
3. 点击章节标题查看详细内容

### 搜索功能

1. 点击工具栏 **搜索** 按钮或使用快捷键 `Ctrl+F`
2. 选择搜索范围（书籍/章节）
3. 输入关键词进行搜索

### 数据备份

点击工具栏 **备份** 按钮或使用快捷键 `Ctrl+B` 创建数据库备份。

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 导入书籍 |
| `Ctrl+S` | 保存（预留） |
| `Ctrl+B` | 备份数据 |
| `Ctrl+F` | 搜索 |
| `Ctrl+E` | 生成电子书（预留） |

## 🛠️ 技术栈

- **框架**: [Tauri 2.0](https://tauri.app) - 跨平台桌面应用框架
- **前端**: [Svelte 5](https://svelte.dev) - 编译时优化前端框架
- **语言**: [TypeScript](https://typescriptlang.org) - 类型安全的JavaScript超集
- **样式**: [Tailwind CSS 4.0](https://tailwindcss.com) - 实用优先的CSS框架
- **数据库**: [SQLite](https://sqlite.org) - 轻量级嵌入式数据库
- **包管理**: [Bun](https://bun.sh) - 极速JavaScript运行时和包管理器

## 📁 项目结构

```
book-shelf/
├── src/                          # 前端源码
│   ├── lib/
│   │   ├── components/          # UI组件
│   │   │   ├── AppLayout.svelte       # 主布局
│   │   │   ├── TitleBar.svelte        # 标题栏
│   │   │   ├── MenuBar.svelte         # 菜单栏
│   │   │   ├── ToolBar.svelte         # 工具栏
│   │   │   ├── StatusBar.svelte       # 状态栏
│   │   │   ├── BookTree.svelte        # 树状视图
│   │   │   ├── ChapterList.svelte     # 章节列表
│   │   │   └── ContentView.svelte     # 内容视图
│   │   ├── stores/              # 状态管理
│   │   │   └── appStore.ts           # 应用状态
│   │   ├── services/            # API服务
│   │   │   └── api.ts                # 数据库API
│   │   ├── types/               # 类型定义
│   │   │   └── index.ts              # TypeScript类型
│   │   └── utils/               # 工具函数
│   │       └── chapterParser.ts      # TXT章节解析
│   └── routes/                  # 页面路由
│       └── +page.svelte              # 主页面
├── src-tauri/                   # Rust后端
│   ├── src/
│   │   └── lib.rs               # 应用入口
│   ├── migrations/              # 数据库迁移
│   │   └── 0001_initial.sql          # 初始数据库结构
│   ├── Cargo.toml              # Rust依赖
│   └── tauri.conf.json         # Tauri配置
├── static/                      # 静态资源
├── package.json                # Node依赖
└── README.md                   # 项目文档
```

## 🗄️ 数据库设计

### 分类表 (categories)
- `id`: 主键
- `name`: 分类名称
- `parent_id`: 父分类ID（支持多级分类）
- `sort_order`: 排序顺序
- `created_at`: 创建时间

### 书籍表 (books)
- `id`: 主键
- `title`: 书名
- `author`: 作者
- `description`: 简介
- `cover_image`: 封面图片路径
- `category_id`: 分类ID
- `file_path`: 原始文件路径
- `file_size`: 文件大小
- `word_count`: 字数统计
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 章节表 (chapters)
- `id`: 主键
- `book_id`: 书籍ID
- `title`: 章节标题
- `content`: 章节内容（Markdown格式）
- `sort_order`: 排序顺序
- `word_count`: 字数统计
- `created_at`: 创建时间

## 📝 后续开发

- [ ] 完整的Tauri命令实现（当前使用前端直接操作SQL）
- [ ] TXT文件智能章节识别
- [ ] EPUB电子书导出
- [ ] 封面图片管理
- [ ] 批量导入功能
- [ ] 数据导入/导出
- [ ] 深色模式支持

## 📝 许可证

MIT License

---

** Enjoy your reading! 📚 **
