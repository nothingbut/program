# 原型库 (Prototypes)

本目录存放用户确认的 UI/UX 原型文件，作为开发和验收的基准。

## 目录结构

```
prototypes/
├── README.md                 # 本文件
├── ui/                       # UI 原型
│   ├── layout-v1.html       # (示例) 初始布局原型
│   ├── layout-v2.html       # (示例) 2 栏布局原型 ✅ 用户确认
│   └── import-dialog.html   # 导入对话框原型
├── flows/                    # 交互流程
│   ├── import-flow.html     # 小说导入流程
│   └── reading-flow.html    # 阅读流程
└── wireframes/               # 线框图（如果有）
    └── main-layout.png
```

## 命名规范

### 文件命名
- 使用小写字母和连字符：`file-name.html`
- 版本号：`layout-v1.html`, `layout-v2.html`
- 明确功能：`import-dialog.html`, `category-tree.html`

### 状态标记
在关联的 ADR 文档中标记原型状态：
- ✅ 已确认：用户明确确认采纳
- ⏳ 待确认：等待用户反馈
- ❌ 已废弃：被更新版本替代

## 使用流程

### 1. 创建原型
```bash
# 创建 HTML 原型
touch docs/prototypes/ui/new-feature.html

# 或使用设计工具导出
# Figma -> Export -> HTML
# Adobe XD -> Export -> Web
```

### 2. 用户确认
- 在需求澄清阶段展示原型
- 记录用户反馈和确认
- 在 ADR 文档中引用原型

### 3. 开发参考
- 开发前必须查看关联原型
- 实现时以原型为准，而非仅凭文字描述
- 如有偏差，与用户再次确认

### 4. 验收测试
- 对照原型进行视觉验收
- 确认交互流程与原型一致
- 记录实际实现与原型的差异

## 原型类型

### HTML 原型
**用途**: 交互原型，可点击测试
**工具**: 纯 HTML/CSS, Tailwind Play, CodePen
**优势**: 可直接在浏览器中测试交互

**示例**:
```html
<!-- docs/prototypes/ui/layout-v2.html -->
<!DOCTYPE html>
<html>
<head>
  <title>2 栏布局原型</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div class="flex h-screen">
    <!-- 左侧分类树 -->
    <aside class="w-64 bg-gray-100 p-4">
      <h2>分类树</h2>
      <!-- ... -->
    </aside>

    <!-- 右侧内容区 -->
    <main class="flex-1 p-4">
      <h2>内容区</h2>
      <!-- ... -->
    </main>
  </div>
</body>
</html>
```

### 图片原型
**用途**: 静态设计稿
**格式**: PNG, JPG（高分辨率）
**工具**: Figma, Sketch, Adobe XD

### 视频原型
**用途**: 动画效果、交互演示
**格式**: MP4, GIF
**工具**: After Effects, Loom, ScreenFlow

## 原型维护

### 版本管理
- 保留所有版本（包括被废弃的）
- 明确标注当前生效版本
- 在 ADR 中记录版本变更原因

### 清理规则
❌ **不删除原型**（即使被废弃）
- 保留历史决策依据
- 避免重复讨论已废弃方案
- 标记状态即可：`layout-v1.html` (❌ 已废弃)

### 文档关联
每个原型应该：
1. 在 ADR 中引用（`docs/decisions/ADR-XXX.md`）
2. 记录确认日期和确认者
3. 说明原型的应用范围

## 当前原型状态

### UI 布局原型

| 文件 | 状态 | 确认日期 | 关联 ADR | 备注 |
|------|------|---------|---------|------|

| ui/2-column-layout.html | ✅ 回溯创建 | 2026-03-12 | ADR-001 | 2 栏布局（3 种状态） |
| ui/import-dialog.html | ✅ 回溯创建 | 2026-03-12 | ADR-005 | 导入对话框（立即解析） |
### 交互流程原型

| 文件 | 状态 | 确认日期 | 关联 ADR | 备注 |
|------|------|---------|---------|------|
| (待添加) import-flow.html | ✅ 已确认 | 2026-03-11 | ADR-005 | 导入流程 |

**注**: 如果需求澄清时有 HTML 原型，请补充到此目录。

## 原型创建指南

### 快速创建 HTML 原型

```bash
# 使用模板创建
cat > docs/prototypes/ui/new-feature.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>新功能原型</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
  <div class="container mx-auto p-8">
    <h1 class="text-3xl font-bold mb-4">新功能原型</h1>

    <!-- 在此添加原型内容 -->

    <footer class="mt-8 text-sm text-gray-500">
      创建日期: $(date +%Y-%m-%d)
      状态: ⏳ 待用户确认
    </footer>
  </div>
</body>
</html>
EOF
```

### 原型必备元素

1. **标题**: 清楚说明原型内容
2. **日期**: 创建/修改日期
3. **状态**: 待确认/已确认/已废弃
4. **版本**: 如果有多个版本
5. **说明**: 简要描述功能和交互

### 原型设计原则

- **简洁**: 只展示核心功能
- **真实**: 使用真实数据示例
- **交互**: HTML 原型应该可交互
- **响应式**: 考虑不同屏幕尺寸

## 工具推荐

### 在线工具
- **Tailwind Play**: https://play.tailwindcss.com/
- **CodePen**: https://codepen.io/
- **JSFiddle**: https://jsfiddle.net/

### 设计工具
- **Figma**: 协作设计（推荐）
- **Sketch**: macOS 原生
- **Adobe XD**: 跨平台

### 截图工具
- **CleanShot X**: macOS 截图标注
- **Snagit**: 跨平台截图
- **浏览器 DevTools**: F12 截图

## 故障排除

### 问题：原型与实现不一致

**原因**:
- 开发时未参考原型
- 原型文件未及时更新
- 技术限制无法完全复现

**解决**:
1. 开发前必须读取关联原型（写入检查清单）
2. 如果需要偏离原型，先与用户确认
3. 记录差异原因到 ADR

### 问题：找不到历史原型

**原因**:
- 原型未保存到此目录
- 只存在于聊天记录中

**解决**:
1. 回溯聊天记录，重建原型
2. 如果是 HTML，从浏览器历史或代码中恢复
3. 如果无法恢复，记录"原型丢失"到 ADR

### 问题：原型文件过大

**解决**:
- 压缩图片（使用 TinyPNG）
- 视频使用外部链接（YouTube, Loom）
- 大型 HTML 资源使用 CDN

## 参考资料

- [ADR 决策日志](../decisions/)
- [设计文档](../specs/)
- [实施计划](../plans/)

---

**创建**: 2026-03-12
**维护者**: 开发团队
**更新频率**: 每个新原型添加时更新
