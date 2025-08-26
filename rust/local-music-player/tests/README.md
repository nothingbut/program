# End-to-End Testing for Local MP3 Player

This directory contains comprehensive end-to-end tests for the Local MP3 Player application using Playwright.

## Test Structure

### Test Files

- **`complete-user-workflow.spec.ts`** - Tests the complete user journey from adding directories to playing music
- **`comprehensive-workflow.spec.ts`** - Comprehensive test covering all major features in a single flow
- **`error-handling.spec.ts`** - Tests error scenarios and edge cases
- **`keyboard-shortcuts.spec.ts`** - Tests keyboard shortcuts and accessibility features
- **`cross-platform.spec.ts`** - Tests platform-specific functionality and compatibility

### Helper Files

- **`helpers/test-utils.ts`** - Common utility functions for tests
- **`test-assets/`** - Directory for test MP3 files (to be created)

## Requirements Coverage

The tests cover all requirements from the specification:

### Directory Management (Requirements 1.1-1.5)
- ✅ Directory panel display
- ✅ Add directory functionality
- ✅ Directory selection
- ✅ File scanning
- ✅ Empty directory handling

### Playlist Display (Requirements 2.1-2.5)
- ✅ Playlist panel display
- ✅ Metadata parsing and display
- ✅ Missing metadata handling
- ✅ Track information format
- ✅ Error handling for corrupted files

### Track Selection and Playback (Requirements 3.1-3.6)
- ✅ Track selection (single click)
- ✅ Track playback (double click)
- ✅ Current track display
- ✅ Track info formatting
- ✅ Cover art display
- ✅ Default icon for missing cover art

### Playback Controls (Requirements 4.1-4.6)
- ✅ Progress bar display and interaction
- ✅ Seek functionality
- ✅ Time display (current/total)
- ✅ Play/pause button
- ✅ Button state indicators

### Navigation Controls (Requirements 5.1-5.8)
- ✅ Previous/next track buttons
- ✅ Auto-play next track
- ✅ Random playback mode
- ✅ Shuffle mode toggle
- ✅ Mode indicators
- ✅ Boundary handling (first/last track)

### Performance and Stability (Requirements 6.1-6.7)
- ✅ Async file scanning
- ✅ Loading indicators
- ✅ Response time testing
- ✅ Error handling
- ✅ Audio playback error handling
- ✅ State persistence
- ✅ State restoration

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   bun install
   ```

2. Install Playwright browsers:
   ```bash
   bunx playwright install
   ```

### Test Commands

```bash
# Run all e2e tests
bun run test:e2e

# Run tests with UI mode
bun run test:e2e:ui

# Run tests in headed mode (see browser)
bun run test:e2e:headed

# Debug tests
bun run test:e2e:debug

# Run specific test file
bunx playwright test complete-user-workflow.spec.ts

# Run tests on specific browser
bunx playwright test --project=chromium
```

### Test Configuration

The tests are configured in `playwright.config.ts` with:

- **Multiple browsers**: Chromium, Firefox, WebKit
- **Automatic app startup**: Tests start the Tauri app automatically
- **Screenshots on failure**: Captures screenshots when tests fail
- **Video recording**: Records videos for failed tests
- **Trace collection**: Collects traces for debugging

## Test Data Setup

### Creating Test Assets

For comprehensive testing, you should create test MP3 files in the `tests/test-assets/` directory:

1. Create a few MP3 files with different metadata:
   - `test-song-1.mp3` - Complete metadata
   - `test-song-2.mp3` - Missing some metadata
   - `test-song-3.mp3` - Minimal metadata

2. Create subdirectories to test directory scanning:
   ```
   tests/test-assets/
   ├── Album1/
   │   ├── track1.mp3
   │   └── track2.mp3
   └── Album2/
       ├── track3.mp3
       └── track4.mp3
   ```

### Mocking File Dialogs

Since Playwright cannot directly interact with native file dialogs, the tests currently simulate directory selection. In a production test environment, you would:

1. Use Tauri's test mode to mock file dialogs
2. Set up predetermined test directories
3. Use environment variables to control test data paths

## Test Strategies

### Unit vs E2E Testing

- **Unit tests** (in `src/lib/components/__tests__/`) test individual components
- **E2E tests** test complete user workflows and integration between frontend and backend

### Cross-Platform Testing

The tests include platform-specific checks for:
- File path handling (Windows vs Unix paths)
- Keyboard shortcuts (Cmd vs Ctrl)
- Font rendering
- Audio codec support
- DPI scaling

### Error Testing

Error scenarios covered:
- Corrupted audio files
- Missing metadata
- File permission errors
- Network/filesystem errors
- Rapid user interactions
- Memory constraints with large playlists

## Debugging Tests

### Common Issues

1. **App startup timeout**: Increase timeout in `playwright.config.ts`
2. **Element not found**: Check data-testid attributes in components
3. **Timing issues**: Add appropriate waits for async operations
4. **File dialog mocking**: Implement proper Tauri test mocks

### Debug Tools

- Use `--debug` flag to step through tests
- Use `--ui` flag for interactive test runner
- Check screenshots and videos in `test-results/`
- Use `page.pause()` to pause test execution

## Continuous Integration

For CI/CD pipelines:

1. Use headless mode: `--project=chromium`
2. Set appropriate timeouts for slower CI environments
3. Use Docker containers for consistent environments
4. Store test artifacts (screenshots, videos) for debugging

## Contributing

When adding new features:

1. Add corresponding data-testid attributes to components
2. Update test files to cover new functionality
3. Add new test cases for edge cases
4. Update this README with new test coverage

## Test Maintenance

- Review and update tests when requirements change
- Keep test data fresh and representative
- Monitor test execution times and optimize slow tests
- Regular cleanup of test artifacts and screenshots