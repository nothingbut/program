#!/usr/bin/env node

import { execSync } from 'child_process';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const buildConfig = JSON.parse(readFileSync('build-config.json', 'utf8'));

function log(message) {
  console.log(`[MULTI-PLATFORM BUILD] ${message}`);
}

function executeCommand(command, options = {}) {
  log(`Executing: ${command}`);
  try {
    return execSync(command, { stdio: 'inherit', ...options });
  } catch (error) {
    console.error(`Command failed: ${command}`);
    console.error(`Error: ${error.message}`);
    return null;
  }
}

function checkRustTarget(target) {
  try {
    execSync(`rustup target list --installed | grep ${target}`, { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

function installRustTarget(target) {
  log(`Installing Rust target: ${target}`);
  executeCommand(`rustup target add ${target}`);
}

function buildForTarget(platform, target) {
  log(`Building for ${platform} (${target})`);
  
  // Check if target is installed
  if (!checkRustTarget(target)) {
    installRustTarget(target);
  }
  
  const env = {
    ...process.env,
    RUSTFLAGS: '-C target-cpu=native -C opt-level=3 -C lto=fat -C strip=symbols -C panic=abort',
    CARGO_PROFILE_RELEASE_CODEGEN_UNITS: '1',
    CARGO_PROFILE_RELEASE_LTO: 'fat',
    CARGO_PROFILE_RELEASE_PANIC: 'abort'
  };
  
  const result = executeCommand(`tauri build --target ${target}`, { env });
  
  if (result !== null) {
    log(`✅ Successfully built for ${platform} (${target})`);
    return true;
  } else {
    log(`❌ Failed to build for ${platform} (${target})`);
    return false;
  }
}

function main() {
  log('Starting multi-platform build process...');
  
  // Ensure output directory exists
  if (!existsSync('dist')) {
    mkdirSync('dist', { recursive: true });
  }
  
  // Build frontend first
  log('Building frontend...');
  executeCommand('bun run build');
  
  const platforms = buildConfig.distribution.platforms;
  const results = {};
  
  // Build for each platform
  for (const [platform, config] of Object.entries(platforms)) {
    log(`\n=== Building for ${platform.toUpperCase()} ===`);
    results[platform] = [];
    
    for (const target of config.targets) {
      const success = buildForTarget(platform, target);
      results[platform].push({ target, success });
    }
  }
  
  // Print summary
  log('\n=== BUILD SUMMARY ===');
  for (const [platform, builds] of Object.entries(results)) {
    log(`${platform.toUpperCase()}:`);
    for (const build of builds) {
      const status = build.success ? '✅' : '❌';
      log(`  ${status} ${build.target}`);
    }
  }
  
  log('\nBuild artifacts can be found in:');
  log('- src-tauri/target/[target]/release/bundle/');
  log('- Individual executables in src-tauri/target/[target]/release/');
}

main();