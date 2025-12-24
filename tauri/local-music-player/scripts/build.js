#!/usr/bin/env node

import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

const buildConfig = JSON.parse(readFileSync('build-config.json', 'utf8'));

function log(message) {
  console.log(`[BUILD] ${message}`);
}

function executeCommand(command, options = {}) {
  log(`Executing: ${command}`);
  try {
    return execSync(command, { stdio: 'inherit', ...options });
  } catch (error) {
    console.error(`Command failed: ${command}`);
    process.exit(1);
  }
}

function buildForPlatform(platform, target) {
  log(`Building for ${platform} (${target})`);
  
  // Set optimization flags for Rust
  const rustFlags = [
    '-C target-cpu=native',
    '-C opt-level=3',
    buildConfig.optimization.lto ? '-C lto=fat' : '',
    buildConfig.optimization.stripSymbols ? '-C strip=symbols' : '',
    buildConfig.optimization.panic === 'abort' ? '-C panic=abort' : ''
  ].filter(Boolean).join(' ');

  const env = {
    ...process.env,
    RUSTFLAGS: rustFlags,
    CARGO_PROFILE_RELEASE_CODEGEN_UNITS: buildConfig.optimization['codegen-units'].toString(),
    CARGO_PROFILE_RELEASE_LTO: buildConfig.optimization.lto ? 'fat' : 'false',
    CARGO_PROFILE_RELEASE_PANIC: buildConfig.optimization.panic
  };

  // Build frontend first
  executeCommand('bun run build');
  
  // Build Tauri app
  const tauriCommand = target ? `tauri build --target ${target}` : 'tauri build';
  executeCommand(tauriCommand, { env });
}

function main() {
  const args = process.argv.slice(2);
  const platform = args[0] || 'current';
  
  log('Starting build process...');
  log(`Target platform: ${platform}`);
  
  // Ensure frontend dependencies are installed
  if (!existsSync('node_modules')) {
    log('Installing frontend dependencies...');
    executeCommand('bun install');
  }
  
  // Ensure Rust dependencies are up to date
  log('Updating Rust dependencies...');
  executeCommand('cargo update', { cwd: 'src-tauri' });
  
  switch (platform) {
    case 'windows':
      buildForPlatform('windows', 'x86_64-pc-windows-msvc');
      break;
    case 'macos':
      buildForPlatform('macos', 'x86_64-apple-darwin');
      break;
    case 'macos-arm':
      buildForPlatform('macos-arm', 'aarch64-apple-darwin');
      break;
    case 'linux':
      buildForPlatform('linux', 'x86_64-unknown-linux-gnu');
      break;
    case 'all':
      // Build for all platforms (requires cross-compilation setup)
      log('Building for all platforms...');
      buildForPlatform('current', null);
      break;
    default:
      buildForPlatform('current', null);
  }
  
  log('Build completed successfully!');
}

main();