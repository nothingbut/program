# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

本地书架 (Local Bookshelf) - A desktop application for managing local novels with TXT file import, chapter browsing, and search functionality. Built as a Tauri 2.0 app with Svelte 5 frontend and Rust backend.

## Development Commands

### Setup
```bash
bun install              # Install dependencies (uses Bun package manager)
```

### Development
```bash
bun run tauri dev        # Start dev server (frontend on :1420, HMR on :1421)
bun run dev             # Start Vite dev server only
bun run check           # Run Svelte type checking
bun run check:watch     # Run type checking in watch mode
```

### Building
```bash
bun run tauri build                              # Build for current platform
bun run tauri build --target x86_64-pc-windows-msvc    # Windows
bun run tauri build --target x86_64-apple-darwin       # macOS
bun run tauri build --target x86_64-unknown-linux-gnu  # Linux
```

## Architecture

### Frontend-Backend Communication Pattern

This app uses **Tauri Commands** for all frontend-backend communication via `@tauri-apps/api/core`'s `invoke()`. The frontend NEVER directly accesses the database - all data operations flow through Rust commands defined in `src-tauri/src/commands/`.

**Flow**: Svelte Component → `src/lib/services/api.ts` → `invoke('command_name')` → Rust Command Handler → SQLite Database

Example:
```typescript
// Frontend (api.ts)
export async function getBookById(id: number): Promise<Book | null> {
  return await invoke<Book | null>('get_book_by_id', { id });
}

// Backend (src-tauri/src/commands/books.rs)
#[command]
pub async fn get_book_by_id(app: AppHandle, id: i64) -> Result<Option<Book>, String> {
  // Database logic here
}
```

### Rust Backend Structure

- **`src-tauri/src/lib.rs`**: Main entry point, registers all Tauri commands and plugins
- **`src-tauri/src/commands/`**: Organized by domain (categories, books, chapters, import)
  - `categories.rs`: CRUD operations for categories
  - `books.rs`: CRUD operations for books
  - `chapters.rs`: CRUD operations for chapters
  - `import.rs`: TXT file parsing and chapter extraction logic
  - `mod.rs`: Module exports
- **`src-tauri/src/models.rs`**: Data structures (Category, Book, Chapter) with serde serialization
- **`src-tauri/src/database.rs`**: Database helper utilities
- **`src-tauri/migrations/`**: SQLite migration files (managed by tauri-plugin-sql)
  - `0001_initial.sql`: Schema definition
  - `0002_test_data.sql`: Test data

### Frontend Structure

- **Svelte 5 with Runes**: Uses new `$state` and `$derived` runes for reactivity
- **SPA Mode**: Uses `@sveltejs/adapter-static` with fallback to `index.html` (no SSR, required for Tauri)
- **State Management**: `src/lib/stores/appStore.ts` - Single global state class using Svelte 5 runes
  - Manages selected book/chapter, expanded categories, search state
  - **Important**: No Svelte store API (`writable`, `readable`) - uses plain class with `$state`

### Component Architecture

Three-column layout pattern in `src/routes/+page.svelte`:
1. **BookTree** (left): Tree view of categories and books
2. **ChapterList** (middle): Chapters for selected book
3. **ContentView** (right): Chapter content with markdown rendering

All components receive state via `appStore` and communicate through store methods (e.g., `appStore.setSelectedBook()`).

### Database Schema

The SQLite schema uses a hierarchical structure:
- **categories**: Self-referencing tree (parent_id → id) for nested categorization
- **books**: Belongs to one category, stores file metadata and word counts
- **chapters**: Belongs to one book, stores markdown content and sort order

Foreign key cascade rules:
- Delete category → SET NULL on books.category_id
- Delete book → CASCADE delete all chapters
- Delete category → CASCADE delete child categories

### Chapter Parsing Logic

Located in `src-tauri/src/commands/import.rs`:
- Tries multiple regex patterns to detect chapter titles (Chinese/English formats)
- Requires minimum 3 chapter matches to consider a pattern valid
- Falls back to treating entire file as single chapter if no pattern matches
- Supports: "第X章", "Chapter X", numbered lists, 【】brackets, etc.

## Key Configuration Files

- **`tauri.conf.json`**: Tauri app configuration
  - `beforeDevCommand`: `bun run dev` (starts Vite)
  - `beforeBuildCommand`: `bun run build`
  - `frontendDist`: `../build` (SvelteKit output)
- **`svelte.config.js`**: Uses `adapter-static` with `fallback: "index.html"` for SPA mode
- **`vite.config.js`**:
  - Fixed dev server port 1420 (required by Tauri)
  - Tailwind CSS 4.0 Vite plugin
  - HMR on port 1421
  - `clearScreen: false` to prevent obscuring Rust errors

## Important Implementation Notes

### When Adding New Commands

1. Define command in appropriate `src-tauri/src/commands/*.rs` file
2. Export in `src-tauri/src/commands/mod.rs`
3. Import in `src-tauri/src/lib.rs`
4. Add to `tauri::generate_handler![]` macro in `lib.rs`
5. Create frontend wrapper in `src/lib/services/api.ts`
6. TypeScript types should match Rust models (see `src/lib/types/index.ts`)

### Database Migrations

Migrations are embedded at compile time via `include_str!()`. To add a new migration:
1. Create `src-tauri/migrations/XXXX_description.sql`
2. Add to `get_migrations()` in `lib.rs` with incremented version number
3. Migrations run automatically on app startup via `tauri-plugin-sql`

### Chinese Text Encoding

The app handles both UTF-8 and GBK encodings (common for Chinese TXT files). The `read_with_encoding` function in `import.rs` tries UTF-8 first, then falls back to GBK using the `encoding_rs` crate.

### Key Rust Dependencies

- **tauri-plugin-sql**: SQLite integration with automatic migrations
- **sqlx**: Database query execution with runtime-tokio
- **chrono**: DateTime handling for timestamps
- **regex**: Chapter title pattern matching during import
- **encoding_rs**: Chinese text encoding detection (UTF-8/GBK)
- **dirs**: Cross-platform user directory paths

## Planned Features (Not Yet Implemented)

- EPUB export functionality
- Cover image management
- Batch import
- Dark mode support
- Full-text search across chapter content
