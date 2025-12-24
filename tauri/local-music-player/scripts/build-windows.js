#!/usr/bin/env node

import { execSync } from 'child_process';
import { readFileSync } from 'fs';

const buildConfig = JSON.parse(readFileSync('build-config.json', 'utf8'));

function log(message) {
  console.log(`[WINDOWS BUILD] ${message}`);
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

function main() {
  log('Building for Windows...');
  
  // Set Windows-specific environment variables
  const env = {
    ...process.env,
    RUSTFLAGS: '-C target-cpu=native -C opt-level=3 -C lto=fat -C strip=symbols -C panic=abort',
    CARGO_PROFILE_RELEASE_CODEGEN_UNITS: '1',
    CARGO_PROFILE_RELEASE_LTO: 'fat',
    CARGO_PROFILE_RELEASE_PANIC: 'abort'
  };
  
  // Build frontend
  executeCommand('bun run build');
  
  // Build for Windows
  executeCommand('tauri build --target x86_64-pc-windows-msvc', { env });
  
  log('Windows build completed!');
  log('Output files:');
  log('- MSI installer: src-tauri/target/x86_64-pc-windows-msvc/release/bundle/msi/');
  log('- Executable: src-tauri/target/x86_64-pc-windows-msvc/release/local-mp3-player.exe');
}

main();