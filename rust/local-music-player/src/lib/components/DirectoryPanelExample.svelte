<script lang="ts">
  import DirectoryPanel from './DirectoryPanel.svelte';
  import { directories, selectedDirectory, directoryActions } from '../stores/directories';
  import type { Directory } from '../types';

  // Example usage of DirectoryPanel component
  let errorMessage = $state<string | null>(null);
  let loading = $state(false);

  function handleDirectoryAdd(event: CustomEvent<{ directory: Directory }>) {
    console.log('Directory added:', event.detail.directory);
    directoryActions.addDirectory(event.detail.directory);
  }

  function handleDirectorySelect(event: CustomEvent<{ directory: Directory }>) {
    console.log('Directory selected:', event.detail.directory);
    directoryActions.selectDirectory(event.detail.directory);
  }

  function handleDirectoryRemove(event: CustomEvent<{ directory: Directory }>) {
    console.log('Directory removed:', event.detail.directory);
    directoryActions.removeDirectory(event.detail.directory.id);
  }

  function handleError(event: CustomEvent<{ message: string }>) {
    console.error('Directory panel error:', event.detail.message);
    errorMessage = event.detail.message;
    
    // Clear error after 5 seconds
    setTimeout(() => {
      errorMessage = null;
    }, 5000);
  }
</script>

<div class="example-container">
  <h1>DirectoryPanel Component Example</h1>
  
  {#if errorMessage}
    <div class="global-error">
      <strong>Error:</strong> {errorMessage}
    </div>
  {/if}

  <div class="panel-container">
    <DirectoryPanel
      directories={$directories}
      selectedDirectory={$selectedDirectory}
      {loading}
      on:directoryAdd={handleDirectoryAdd}
      on:directorySelect={handleDirectorySelect}
      on:directoryRemove={handleDirectoryRemove}
      on:error={handleError}
    />
  </div>

  <div class="debug-info">
    <h3>Debug Information</h3>
    <p><strong>Total directories:</strong> {$directories.length}</p>
    <p><strong>Selected directory:</strong> {$selectedDirectory?.name || 'None'}</p>
    <p><strong>Loading:</strong> {loading}</p>
    
    <details>
      <summary>All directories</summary>
      <pre>{JSON.stringify($directories, null, 2)}</pre>
    </details>
  </div>
</div>

<style>
  .example-container {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .global-error {
    background-color: #fee;
    color: #c33;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    border: 1px solid #fcc;
  }

  .panel-container {
    height: 500px;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 2rem;
  }

  .debug-info {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }

  .debug-info h3 {
    margin-top: 0;
  }

  .debug-info details {
    margin-top: 1rem;
  }

  .debug-info pre {
    background-color: #fff;
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #ddd;
    overflow-x: auto;
    font-size: 0.8rem;
  }
</style>