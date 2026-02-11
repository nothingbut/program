# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A local MP3 music player built with Tauri 2.0, featuring a dual-panel interface (directory management + playlist) with full playback controls. The application uses Svelte 5 with TypeScript for the frontend and Rust for the backend audio processing and file system operations.

## Technology Stack

**Frontend:**
- Svelte 5 (with runes: `$state`, `$derived`)
- TypeScript
- SvelteKit with static adapter
- svelte-i18n for internationalization (English + Chinese)
- Vite for bundling

**Backend:**
- Rust with Tauri 2.0 framework
- rodio + symphonia for audio playback
- id3 for MP3 metadata extraction
- tokio for async operations

**Package Management:** Bun (preferred over npm/pnpm)

## Development Commands

### Frontend Development
```bash
# Install dependencies
bun install

# Run development server (frontend only)
bun run dev

# Build frontend
bun run build

# Type checking
bun run check
bun run check:watch

# Run frontend unit tests
bun run test
bun run test:watch

# Run E2E tests
bun run test:e2e
bun run test:e2e:ui
bun run test:e2e:debug
```

### Tauri Development
```bash
# Run Tauri dev mode (includes frontend hot reload)
bun run tauri:dev

# Build Tauri app for current platform
bun run tauri:build

# Build debug version (with symbols)
bun run tauri:build:debug

# Build for all platforms (frontend + backend)
bun run build:all
```

### Rust Testing
```bash
# Run all Rust tests
cargo test --manifest-path src-tauri/Cargo.toml

# Run specific test
cargo test --manifest-path src-tauri/Cargo.toml test_name

# Run tests with output
cargo test --manifest-path src-tauri/Cargo.toml -- --nocapture

# Check Rust compilation without building
cargo check --manifest-path src-tauri/Cargo.toml
```

### Platform-Specific Builds
```bash
# Windows (x86_64)
bun run build:windows

# macOS Intel
bun run build:macos

# macOS Apple Silicon
bun run build:macos-arm

# Universal macOS binary
bun run build:universal-macos

# Linux (x86_64)
bun run build:linux
```

## Architecture

### Backend Architecture (Rust)

**Core Modules:**
- `lib.rs` - Main library entry point, exports all public APIs
- `models.rs` - Core data models (Directory, Track, PlaybackState, AppState)
- `audio_player.rs` - Audio engine using rodio, runs in separate thread with command/event pattern
- `directory_manager.rs` - File system operations and directory tracking
- `mp3_analyzer.rs` - MP3 file scanning and metadata extraction
- `persistence.rs` - Application state serialization/deserialization
- `errors.rs` - Centralized error handling with thiserror

**Key Design Patterns:**
- **Command Pattern**: Audio player receives commands via mpsc channel, executes in dedicated thread
- **Event-Driven**: Playback events emitted via mpsc channel to frontend
- **Type-Safe State**: All state serialized with serde, camelCase for JS interop
- **Thread Safety**: AudioPlayer state wrapped in Arc<Mutex<>> for safe concurrent access

**Tauri Commands**: All backend functions exposed via `#[tauri::command]` are defined in `lib.rs`

### Frontend Architecture (Svelte 5)

**Store Organization (src/lib/stores/):**
- `directories.ts` - Directory list and selection state
- `playlist.ts` - Current playlist and selected track
- `playback.ts` - Playback state (isPlaying, currentTime, volume)
- `playlistManager.ts` - Advanced playlist logic (sequential/shuffle modes, navigation)
- `ui.ts` - UI state (loading, errors, toasts, confirmation dialogs)
- `keyboard.ts` - Keyboard shortcut handling
- `persistence.ts` - State persistence coordination

**Key Patterns:**
- **Svelte 5 Runes**: Uses `$state`, `$derived` for reactive state
- **Derived Stores**: Navigation state computed from multiple stores
- **Separation of Concerns**: Actions separated from state, UI logic separated from API calls
- **Type Safety**: All stores strongly typed, mirrors Rust models

**Component Structure:**
- `App.svelte` - Root component, orchestrates initialization and state
- `DirectoryPanel.svelte` - Left panel for directory management
- `PlaylistPanel.svelte` - Right panel showing current playlist
- `PlayerControls.svelte` - Bottom bar with play/pause/seek/volume controls
- `LanguageSwitcher.svelte` - i18n language selection
- `ToastNotifications.svelte` - Toast notification system
- `ConfirmationDialog.svelte` - Modal confirmation dialogs

### State Management

**State Flow:**
1. User interacts with UI component
2. Component calls action from store (e.g., `playlistActions.selectTrack()`)
3. Store action calls Tauri backend API via `api.ts`
4. Backend processes request, updates internal state
5. Backend emits events or returns result
6. Frontend store updates, triggers reactive re-renders

**Persistence:**
- Application state saved to disk via Tauri's file system plugin
- State includes: directories, selected directory, playlist, playback state, shuffle mode, window geometry
- Auto-save triggered on significant state changes
- Loaded on app initialization

### API Layer (src/lib/api.ts)

Wraps Tauri invoke commands with proper error handling:
- `directoryApi` - Directory operations (add, remove, scan)
- `playbackApi` - Playback controls (play, pause, seek, volume)
- `stateApi` - State persistence (load, save)

All API functions return `Promise<T>` and throw typed errors on failure.

## Important Conventions

### Rust Code
- Use `AppResult<T>` for all functions that can fail (alias for `Result<T, AppError>`)
- All public models use `#[serde(rename_all = "camelCase")]` for JS interop
- Audio operations must be async-aware but rodio calls happen in dedicated thread
- Test files live in `src-tauri/src/` with `#[cfg(test)]` or in `src-tauri/tests/`

### TypeScript/Svelte Code
- Use Svelte 5 runes (`$state`, `$derived`) instead of old reactive syntax
- Mirror Rust type names exactly (Directory, Track, PlaybackState)
- Use camelCase for all properties to match Rust serialization
- Store actions should be prefixed with action type (e.g., `playlistActions.selectTrack`)
- API calls should use `handleApiError()` wrapper for consistent error handling

### Internationalization
- All user-facing text must support i18n via svelte-i18n
- Translation keys in `src/lib/i18n/locales/{en,zh}.json`
- Use `$_('key', { default: 'fallback' })` pattern in components
- Supported languages: English (en), Chinese (zh)

## Testing

### Frontend Tests
- Unit tests: Vitest with @testing-library/svelte
- E2E tests: Playwright
- Test files in `src/lib/components/__tests__/` and `tests/`

### Backend Tests
- Unit tests inline with `#[cfg(test)]` modules
- Integration tests in `src-tauri/tests/`
- Use `tempfile` crate for file system tests

## Build Optimization

The project uses aggressive optimization for release builds:
- **LTO**: Enabled for smaller binaries
- **codegen-units**: Set to 1 for maximum optimization
- **panic**: Abort strategy to reduce binary size
- **strip**: Debug symbols removed in release
- **Frontend**: ESBuild minification, code splitting, CSS optimization

See BUILD.md for detailed build configuration and platform-specific instructions.

## Common Pitfalls

1. **Tauri API Calls**: Always use `invoke` from `@tauri-apps/api/core`, not window.__TAURI__
2. **Audio Thread**: Never call rodio Sink methods directly; use command pattern via AudioPlayer
3. **Svelte 5 Syntax**: Don't mix old `$:` reactive syntax with new runes
4. **Type Sync**: Keep TypeScript types in `types.ts` synchronized with Rust models in `models.rs`
5. **State Persistence**: Large state changes should trigger auto-save via persistence store
6. **Error Handling**: Backend errors must be serializable; use AppError enum, not generic errors

## File Locations

- Rust backend: `src-tauri/src/`
- Frontend source: `src/`
- Frontend components: `src/lib/components/`
- Frontend stores: `src/lib/stores/`
- Frontend types: `src/lib/types.ts`
- i18n translations: `src/lib/i18n/locales/`
- Tauri config: `src-tauri/tauri.conf.json`
- Build config: `build-config.json`
