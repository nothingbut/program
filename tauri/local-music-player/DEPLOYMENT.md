# Deployment Guide

This document covers deployment strategies, distribution methods, and release management for the Local MP3 Player application.

## Distribution Channels

### Direct Distribution
- **GitHub Releases**: Primary distribution method
- **Website Download**: Direct download links
- **Manual Installation**: Standalone installers

### Platform Stores (Future)
- **Microsoft Store**: Windows Store distribution
- **Mac App Store**: macOS App Store distribution
- **Snap Store**: Linux Snap packages
- **Flathub**: Linux Flatpak packages

## Release Process

### 1. Pre-Release Preparation

#### Version Management
```bash
# Update version in package.json
npm version patch|minor|major

# Update Cargo.toml version
# Edit src-tauri/Cargo.toml manually

# Update tauri.conf.json version
# Edit src-tauri/tauri.conf.json manually
```

#### Quality Assurance
```bash
# Run all tests
bun run test
bun run test:e2e

# Build and test on all platforms
node scripts/build-all-platforms.js

# Manual testing checklist
# - Install and run on each platform
# - Test core functionality
# - Verify UI responsiveness
# - Check audio playback
# - Test file system operations
```

### 2. Build Process

#### Automated Build
```bash
# Build for all platforms
node scripts/build-all-platforms.js

# Or build individually
bun run build:windows
bun run build:macos
bun run build:macos-arm
bun run build:linux
```

#### Build Verification
```bash
# Verify build outputs
ls -la src-tauri/target/*/release/bundle/

# Test installers
# Windows: Install MSI and verify functionality
# macOS: Mount DMG and test app bundle
# Linux: Install DEB/AppImage and verify
```

### 3. Code Signing

#### Windows Code Signing
```bash
# Set certificate thumbprint
export WINDOWS_CERTIFICATE_THUMBPRINT="your-cert-thumbprint"

# Sign the executable
signtool sign /sha1 $WINDOWS_CERTIFICATE_THUMBPRINT /t http://timestamp.sectigo.com /fd sha256 "local-mp3-player.exe"
```

#### macOS Code Signing
```bash
# Set signing identity
export APPLE_CERTIFICATE="Developer ID Application: Your Name (TEAM_ID)"

# Sign the app bundle
codesign --force --options runtime --sign "$APPLE_CERTIFICATE" "Local MP3 Player.app"

# Create signed DMG
create-dmg --identity "$APPLE_CERTIFICATE" "Local MP3 Player.dmg" "Local MP3 Player.app"
```

#### macOS Notarization
```bash
# Submit for notarization
xcrun notarytool submit "Local MP3 Player.dmg" \
  --apple-id "your-apple-id@example.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# Staple the notarization
xcrun stapler staple "Local MP3 Player.dmg"
```

### 4. Release Creation

#### GitHub Release
```bash
# Create release with GitHub CLI
gh release create v0.1.0 \
  --title "Local MP3 Player v0.1.0" \
  --notes-file CHANGELOG.md \
  src-tauri/target/*/release/bundle/**/*
```

#### Release Assets
Include the following files in releases:
- **Windows**: `Local_MP3_Player_0.1.0_x64_en-US.msi`
- **macOS Intel**: `Local_MP3_Player_0.1.0_x64.dmg`
- **macOS ARM**: `Local_MP3_Player_0.1.0_aarch64.dmg`
- **Linux DEB**: `local-mp3-player_0.1.0_amd64.deb`
- **Linux AppImage**: `local-mp3-player_0.1.0_amd64.AppImage`

## Continuous Deployment

### GitHub Actions Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  build-and-release:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: 'macos-latest'
            args: '--target x86_64-apple-darwin'
          - platform: 'macos-latest'
            args: '--target aarch64-apple-darwin'
          - platform: 'ubuntu-22.04'
            args: '--target x86_64-unknown-linux-gnu'
          - platform: 'windows-latest'
            args: '--target x86_64-pc-windows-msvc'

    runs-on: ${{ matrix.platform }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install dependencies (ubuntu only)
        if: matrix.platform == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y libasound2-dev libwebkit2gtk-4.0-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev

      - name: Rust setup
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.platform == 'macos-latest' && 'aarch64-apple-darwin,x86_64-apple-darwin' || '' }}

      - name: Rust cache
        uses: swatinem/rust-cache@v2
        with:
          workspaces: './src-tauri -> target'

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Install frontend dependencies
        run: bun install

      - name: Build the app
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: 'Local MP3 Player ${{ github.ref_name }}'
          releaseBody: 'See the assets to download this version and install.'
          releaseDraft: true
          prerelease: false
          args: ${{ matrix.args }}
```

### Environment Variables

Set the following secrets in GitHub repository settings:

#### Code Signing Secrets
- `APPLE_CERTIFICATE`: Base64 encoded P12 certificate
- `APPLE_CERTIFICATE_PASSWORD`: Certificate password
- `APPLE_SIGNING_IDENTITY`: Developer ID Application identity
- `APPLE_ID`: Apple ID email
- `APPLE_PASSWORD`: App-specific password
- `APPLE_TEAM_ID`: Apple Developer Team ID

## Distribution Strategies

### 1. GitHub Releases (Primary)

**Advantages:**
- Free hosting
- Automatic changelog generation
- Version management
- Download statistics

**Setup:**
```bash
# Tag and push release
git tag v0.1.0
git push origin v0.1.0

# GitHub Actions will automatically create release
```

### 2. Direct Website Distribution

**Setup:**
- Host installers on CDN or web server
- Create download page with platform detection
- Implement download analytics

**Example download page structure:**
```
downloads/
├── windows/
│   └── Local_MP3_Player_0.1.0_x64_en-US.msi
├── macos/
│   ├── Local_MP3_Player_0.1.0_x64.dmg
│   └── Local_MP3_Player_0.1.0_aarch64.dmg
└── linux/
    ├── local-mp3-player_0.1.0_amd64.deb
    └── local-mp3-player_0.1.0_amd64.AppImage
```

### 3. Package Managers

#### Windows Package Managers
```bash
# Chocolatey (community maintained)
choco install local-mp3-player

# Winget (requires Microsoft Store submission)
winget install LocalMP3Player
```

#### macOS Package Managers
```bash
# Homebrew Cask
brew install --cask local-mp3-player

# MacPorts
sudo port install local-mp3-player
```

#### Linux Package Managers
```bash
# Snap Store
sudo snap install local-mp3-player

# Flatpak (Flathub)
flatpak install flathub com.shichang.LocalMP3Player

# AUR (Arch Linux)
yay -S local-mp3-player
```

## Update Mechanism

### Auto-Update Implementation (Future)

#### Tauri Updater Plugin
```rust
// In src-tauri/src/main.rs
use tauri_plugin_updater::UpdaterExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .setup(|app| {
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                update(handle).await.unwrap();
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

async fn update(app: tauri::AppHandle) -> tauri_plugin_updater::Result<()> {
    if let Some(update) = app.updater()?.check().await? {
        let mut downloaded = 0;
        
        update
            .download(
                |chunk_length, content_length| {
                    downloaded += chunk_length;
                    println!("downloaded {downloaded} from {content_length:?}");
                },
                || {
                    println!("download finished");
                },
            )
            .await?;
        
        println!("update installed");
        update.install().await?;
        println!("app is going to restart");
        app.restart();
    }
    
    Ok(())
}
```

#### Update Server Configuration
```json
{
  "version": "0.1.1",
  "notes": "Bug fixes and performance improvements",
  "pub_date": "2024-01-15T12:00:00Z",
  "platforms": {
    "windows-x86_64": {
      "signature": "signature-here",
      "url": "https://releases.example.com/Local_MP3_Player_0.1.1_x64_en-US.msi.zip"
    },
    "darwin-x86_64": {
      "signature": "signature-here", 
      "url": "https://releases.example.com/Local_MP3_Player_0.1.1_x64.app.tar.gz"
    },
    "linux-x86_64": {
      "signature": "signature-here",
      "url": "https://releases.example.com/local-mp3-player_0.1.1_amd64.AppImage.tar.gz"
    }
  }
}
```

## Monitoring and Analytics

### Download Analytics
- Track download counts by platform
- Monitor geographic distribution
- Analyze version adoption rates

### Error Reporting
- Implement crash reporting (e.g., Sentry)
- Collect performance metrics
- Monitor user feedback

### Usage Analytics (Optional)
- Anonymous usage statistics
- Feature usage tracking
- Performance metrics

## Security Considerations

### Code Signing Best Practices
- Store certificates securely
- Use hardware security modules (HSM) for production
- Implement certificate rotation
- Monitor certificate expiration

### Distribution Security
- Use HTTPS for all downloads
- Implement checksum verification
- Sign all release artifacts
- Maintain secure build environment

### Update Security
- Sign update packages
- Use secure update channels
- Implement rollback mechanisms
- Verify update integrity

## Rollback Strategy

### Version Rollback
```bash
# Revert to previous version
git checkout v0.1.0
node scripts/build-all-platforms.js

# Create hotfix release
git tag v0.1.1-hotfix
git push origin v0.1.1-hotfix
```

### Emergency Response
1. **Identify Issue**: Monitor crash reports and user feedback
2. **Assess Impact**: Determine severity and affected users
3. **Create Fix**: Develop and test hotfix
4. **Emergency Release**: Fast-track release process
5. **Communication**: Notify users of the issue and fix

## Documentation Updates

### Release Notes Template
```markdown
## Version 0.1.0 - 2024-01-15

### New Features
- Feature 1 description
- Feature 2 description

### Bug Fixes
- Fix 1 description
- Fix 2 description

### Performance Improvements
- Improvement 1 description
- Improvement 2 description

### Breaking Changes
- Change 1 description (if any)

### Known Issues
- Issue 1 description (if any)
```

### User Documentation
- Update installation instructions
- Revise user manual
- Update FAQ
- Create migration guides (if needed)

---

This deployment guide should be updated with each release to reflect current best practices and lessons learned from the deployment process.