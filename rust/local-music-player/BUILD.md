# Build and Deployment Guide

This document provides comprehensive instructions for building and deploying the Local MP3 Player application across different platforms.

## Prerequisites

### Development Environment
- **Node.js**: Version 18 or higher
- **Bun**: Latest version (for package management and build scripts)
- **Rust**: Latest stable version with `rustup`
- **Tauri CLI**: Version 2.x

### Platform-Specific Requirements

#### Windows
- **Visual Studio Build Tools** or **Visual Studio Community** with C++ build tools
- **Windows SDK** (latest version)

#### macOS
- **Xcode Command Line Tools**: `xcode-select --install`
- **macOS SDK**: Included with Xcode

#### Linux
- **Build essentials**: `sudo apt-get install build-essential`
- **Audio libraries**: `sudo apt-get install libasound2-dev`
- **Additional dependencies**: `sudo apt-get install libwebkit2gtk-4.0-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev`

## Quick Start

### Development Build
```bash
# Install dependencies
bun install

# Run in development mode
bun run tauri:dev
```

### Production Build
```bash
# Build for current platform
bun run build:all

# Or use the custom build script
node scripts/build.js
```

## Build Scripts

### Available Scripts

| Script | Description |
|--------|-------------|
| `bun run build:all` | Build frontend and Tauri app for current platform |
| `bun run build:windows` | Build for Windows (x86_64) |
| `bun run build:macos` | Build for macOS Intel |
| `bun run build:macos-arm` | Build for macOS Apple Silicon |
| `bun run build:linux` | Build for Linux (x86_64) |
| `bun run build:universal-macos` | Build universal macOS binary |

### Custom Build Scripts

#### Single Platform Build
```bash
# Build for specific platform
node scripts/build.js windows
node scripts/build.js macos
node scripts/build.js linux
```

#### Multi-Platform Build
```bash
# Build for all supported platforms
node scripts/build-all-platforms.js
```

## Build Configuration

### Build Optimization

The application uses several optimization techniques:

#### Rust Optimizations
- **LTO (Link Time Optimization)**: Enabled for smaller binaries
- **Code Generation Units**: Set to 1 for maximum optimization
- **Panic Strategy**: Set to `abort` for smaller binaries
- **Symbol Stripping**: Enabled to reduce binary size

#### Frontend Optimizations
- **ESBuild Minification**: Fast and efficient minification
- **CSS Minification**: Reduces stylesheet size
- **Code Splitting**: Separates vendor and UI code
- **Dependency Optimization**: Pre-bundles common dependencies

### Configuration Files

#### `build-config.json`
Contains build settings for signing, distribution, and optimization:

```json
{
  "signing": {
    "windows": { "certificateThumbprint": null },
    "macos": { "signingIdentity": null }
  },
  "distribution": {
    "platforms": { ... }
  },
  "optimization": {
    "stripSymbols": true,
    "lto": true
  }
}
```

#### `src-tauri/tauri.conf.json`
Main Tauri configuration with bundle settings, permissions, and app metadata.

## Platform-Specific Instructions

### Windows

#### Building
```bash
# Ensure Windows build tools are installed
# Build for Windows
bun run build:windows
```

#### Output Files
- **MSI Installer**: `src-tauri/target/x86_64-pc-windows-msvc/release/bundle/msi/`
- **Executable**: `src-tauri/target/x86_64-pc-windows-msvc/release/local-mp3-player.exe`

#### Code Signing (Optional)
1. Obtain a code signing certificate
2. Update `build-config.json` with certificate thumbprint
3. Set `WINDOWS_CERTIFICATE_THUMBPRINT` environment variable

### macOS

#### Building
```bash
# For Intel Macs
bun run build:macos

# For Apple Silicon
bun run build:macos-arm

# Universal binary (both architectures)
bun run build:universal-macos
```

#### Output Files
- **DMG Installer**: `src-tauri/target/[arch]-apple-darwin/release/bundle/dmg/`
- **App Bundle**: `src-tauri/target/[arch]-apple-darwin/release/bundle/macos/`

#### Code Signing and Notarization
1. Obtain Apple Developer certificates
2. Update `build-config.json` with signing identity
3. Set environment variables:
   ```bash
   export APPLE_CERTIFICATE="Developer ID Application: Your Name"
   export APPLE_ID="your-apple-id@example.com"
   export APPLE_PASSWORD="app-specific-password"
   ```

### Linux

#### Building
```bash
# Install dependencies first
sudo apt-get update
sudo apt-get install libasound2-dev libwebkit2gtk-4.0-dev libgtk-3-dev

# Build for Linux
bun run build:linux
```

#### Output Files
- **DEB Package**: `src-tauri/target/x86_64-unknown-linux-gnu/release/bundle/deb/`
- **AppImage**: `src-tauri/target/x86_64-unknown-linux-gnu/release/bundle/appimage/`
- **Executable**: `src-tauri/target/x86_64-unknown-linux-gnu/release/local-mp3-player`

## Cross-Compilation

### Setting Up Cross-Compilation

#### For Windows (from macOS/Linux)
```bash
# Install Windows target
rustup target add x86_64-pc-windows-msvc

# Install cross-compilation tools (Linux)
sudo apt-get install gcc-mingw-w64-x86-64
```

#### For macOS (from Linux)
```bash
# Install macOS target
rustup target add x86_64-apple-darwin
rustup target add aarch64-apple-darwin

# Note: Requires macOS SDK and additional setup
```

### Cross-Compilation Limitations
- **Windows to macOS**: Not supported without additional tools
- **macOS to Windows**: Requires Windows SDK
- **Linux to macOS**: Requires macOS SDK and osxcross

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build and Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        platform: [ubuntu-latest, windows-latest, macos-latest]
    
    runs-on: ${{ matrix.platform }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        
      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        
      - name: Install dependencies
        run: bun install
        
      - name: Build application
        run: bun run build:all
        
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: app-${{ matrix.platform }}
          path: src-tauri/target/*/release/bundle/
```

## Troubleshooting

### Common Issues

#### Build Failures
1. **Missing dependencies**: Ensure all platform-specific dependencies are installed
2. **Rust target not found**: Install required targets with `rustup target add <target>`
3. **Frontend build fails**: Check Node.js version and run `bun install`

#### Performance Issues
1. **Large binary size**: Ensure optimization flags are enabled
2. **Slow startup**: Check for unnecessary dependencies in frontend
3. **High memory usage**: Review Rust code for memory leaks

#### Platform-Specific Issues

**Windows:**
- Visual Studio Build Tools not found
- Windows SDK version mismatch

**macOS:**
- Xcode Command Line Tools not installed
- Code signing certificate issues

**Linux:**
- Missing system libraries
- GTK/WebKit dependencies not found

### Debug Builds

For debugging purposes, you can create debug builds:

```bash
# Debug build with symbols
bun run tauri:build:debug

# Or with custom script
RUST_LOG=debug node scripts/build.js
```

## Distribution

### Release Checklist

1. **Version Bump**: Update version in `package.json` and `src-tauri/Cargo.toml`
2. **Build All Platforms**: Run multi-platform build
3. **Test Installers**: Verify installers work on target platforms
4. **Code Signing**: Sign binaries for Windows and macOS
5. **Create Release**: Upload to GitHub Releases or distribution platform

### Installer Verification

#### Windows
```bash
# Verify MSI installer
msiexec /i "Local MP3 Player_0.1.0_x64_en-US.msi" /quiet
```

#### macOS
```bash
# Verify DMG and app bundle
hdiutil verify "Local MP3 Player_0.1.0_x64.dmg"
spctl --assess --verbose "Local MP3 Player.app"
```

#### Linux
```bash
# Verify DEB package
dpkg -I local-mp3-player_0.1.0_amd64.deb
lintian local-mp3-player_0.1.0_amd64.deb
```

## Performance Optimization

### Binary Size Optimization
- Strip debug symbols in release builds
- Enable LTO (Link Time Optimization)
- Use `panic = "abort"` strategy
- Minimize dependencies

### Runtime Performance
- Optimize Rust code with `opt-level = 3`
- Use efficient data structures
- Minimize memory allocations
- Profile with `cargo flamegraph`

### Startup Time
- Lazy load non-critical components
- Optimize frontend bundle size
- Use code splitting
- Minimize initial JavaScript execution

## Security Considerations

### Code Signing
- Always sign releases for Windows and macOS
- Use timestamping for long-term validity
- Store certificates securely

### Dependency Security
- Regularly audit dependencies with `cargo audit`
- Keep dependencies updated
- Use minimal dependency sets

### Sandboxing
- Follow Tauri security best practices
- Minimize filesystem permissions
- Validate all user inputs

---

For additional help or questions, please refer to the [Tauri documentation](https://tauri.app/v1/guides/) or create an issue in the project repository.