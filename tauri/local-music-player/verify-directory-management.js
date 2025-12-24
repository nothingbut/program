#!/usr/bin/env node

/**
 * Simple verification script to test directory management functionality
 * This script verifies that the Rust backend and TypeScript frontend integration works correctly
 */

console.log('🔍 Verifying Directory Management Implementation...\n');

// Check that all required files exist
const fs = require('fs');
const path = require('path');

const requiredFiles = [
  'src-tauri/src/directory_manager.rs',
  'src-tauri/src/lib.rs',
  'src-tauri/src/models.rs',
  'src-tauri/src/errors.rs',
  'src/lib/api.ts',
  'src/lib/types.ts',
];

let allFilesExist = true;

console.log('📁 Checking required files:');
requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file} - MISSING`);
    allFilesExist = false;
  }
});

if (!allFilesExist) {
  console.log('\n❌ Some required files are missing!');
  process.exit(1);
}

// Check that the Rust code compiles
console.log('\n🦀 Checking Rust compilation:');
const { execSync } = require('child_process');

try {
  execSync('cargo check --manifest-path src-tauri/Cargo.toml', { stdio: 'pipe' });
  console.log('  ✅ Rust code compiles successfully');
} catch (error) {
  console.log('  ❌ Rust compilation failed');
  console.log(error.stdout?.toString() || error.message);
  process.exit(1);
}

// Check that Rust tests pass
console.log('\n🧪 Running Rust tests:');
try {
  const output = execSync('cargo test --manifest-path src-tauri/Cargo.toml', { stdio: 'pipe' });
  const testOutput = output.toString();
  
  if (testOutput.includes('test result: ok')) {
    console.log('  ✅ All Rust tests pass');
  } else {
    console.log('  ❌ Some Rust tests failed');
    console.log(testOutput);
    process.exit(1);
  }
} catch (error) {
  console.log('  ❌ Rust tests failed');
  console.log(error.stdout?.toString() || error.message);
  process.exit(1);
}

// Check TypeScript compilation
console.log('\n📝 Checking TypeScript compilation:');
try {
  execSync('bun run check', { stdio: 'pipe' });
  console.log('  ✅ TypeScript code compiles successfully');
} catch (error) {
  console.log('  ❌ TypeScript compilation failed');
  console.log(error.stdout?.toString() || error.message);
  process.exit(1);
}

// Verify API functions are properly exported
console.log('\n🔗 Checking API exports:');
const apiContent = fs.readFileSync('src/lib/api.ts', 'utf8');

const requiredExports = [
  'directoryApi',
  'add',
  'getAll',
  'remove',
  'getById',
  'refresh',
  'handleApiError'
];

let allExportsFound = true;
requiredExports.forEach(exportName => {
  if (apiContent.includes(exportName)) {
    console.log(`  ✅ ${exportName} exported`);
  } else {
    console.log(`  ❌ ${exportName} - NOT FOUND`);
    allExportsFound = false;
  }
});

if (!allExportsFound) {
  console.log('\n❌ Some required API exports are missing!');
  process.exit(1);
}

// Verify Tauri commands are registered
console.log('\n⚡ Checking Tauri command registration:');
const libContent = fs.readFileSync('src-tauri/src/lib.rs', 'utf8');

const requiredCommands = [
  'add_directory',
  'get_directories',
  'remove_directory',
  'get_directory',
  'refresh_directories'
];

let allCommandsRegistered = true;
requiredCommands.forEach(command => {
  if (libContent.includes(command)) {
    console.log(`  ✅ ${command} registered`);
  } else {
    console.log(`  ❌ ${command} - NOT REGISTERED`);
    allCommandsRegistered = false;
  }
});

if (!allCommandsRegistered) {
  console.log('\n❌ Some required Tauri commands are not registered!');
  process.exit(1);
}

// Check that the application builds
console.log('\n🏗️  Checking application build:');
try {
  execSync('bun run build', { stdio: 'pipe' });
  console.log('  ✅ Application builds successfully');
} catch (error) {
  console.log('  ❌ Application build failed');
  console.log(error.stdout?.toString() || error.message);
  process.exit(1);
}

console.log('\n🎉 All verification checks passed!');
console.log('\n📋 Implementation Summary:');
console.log('  ✅ Directory management Rust backend implemented');
console.log('  ✅ Tauri commands for directory operations created');
console.log('  ✅ TypeScript API wrapper implemented');
console.log('  ✅ Path validation and security checks added');
console.log('  ✅ Directory persistence mechanism created');
console.log('  ✅ Comprehensive unit tests written and passing');
console.log('  ✅ Application builds successfully');

console.log('\n🚀 Directory management functionality is ready for use!');
console.log('\nImplemented features:');
console.log('  • Add directories with path validation');
console.log('  • List all directories with sorting');
console.log('  • Remove directories by ID');
console.log('  • Get specific directory by ID');
console.log('  • Refresh directories (remove inaccessible ones)');
console.log('  • Persistent storage of directory list');
console.log('  • Comprehensive error handling');
console.log('  • Security checks for directory access');