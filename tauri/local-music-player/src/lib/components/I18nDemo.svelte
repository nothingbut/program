<script lang="ts">
  import { _ } from 'svelte-i18n';
  import LanguageSwitcher from './LanguageSwitcher.svelte';

  // Sample data for demonstration
  const sampleTrack = {
    title: "Sample Song",
    artist: "Sample Artist",
    album: "Sample Album",
    trackNumber: 1,
    duration: 180
  };

  const sampleDirectory = {
    name: "My Music"
  };
</script>

<div class="i18n-demo">
  <div class="demo-header">
    <h1>{$_('app.title', { default: 'Local MP3 Player' })}</h1>
    <LanguageSwitcher />
  </div>

  <div class="demo-sections">
    <section class="demo-section">
      <h2>{$_('directory.title', { default: 'Music Directories' })}</h2>
      <div class="demo-content">
        <button class="demo-button">
          {$_('directory.add', { default: 'Add Directory' })}
        </button>
        <p class="demo-text">
          📁 {sampleDirectory.name}
        </p>
        <p class="demo-text">
          {$_('directory.empty', { default: 'No directories added yet' })}
        </p>
      </div>
    </section>

    <section class="demo-section">
      <h2>{$_('playlist.title', { default: 'Playlist' })}</h2>
      <div class="demo-content">
        <div class="demo-table">
          <div class="demo-table-header">
            <span>{$_('playlist.columns.title', { default: 'Title' })}</span>
            <span>{$_('playlist.columns.artist', { default: 'Artist' })}</span>
            <span>{$_('playlist.columns.album', { default: 'Album' })}</span>
            <span>{$_('playlist.columns.duration', { default: 'Duration' })}</span>
          </div>
          <div class="demo-table-row">
            <span>{sampleTrack.title}</span>
            <span>{sampleTrack.artist}</span>
            <span>{sampleTrack.album}</span>
            <span>3:00</span>
          </div>
        </div>
        <p class="demo-text">
          {$_('playlist.empty', { default: 'No music files found' })}
        </p>
      </div>
    </section>

    <section class="demo-section">
      <h2>{$_('player.play', { default: 'Player Controls' })}</h2>
      <div class="demo-content">
        <div class="demo-controls">
          <button class="demo-button">{$_('player.previous', { default: 'Previous' })}</button>
          <button class="demo-button primary">{$_('player.play', { default: 'Play' })}</button>
          <button class="demo-button">{$_('player.next', { default: 'Next' })}</button>
          <button class="demo-button">{$_('player.shuffle', { default: 'Shuffle' })}</button>
        </div>
      </div>
    </section>

    <section class="demo-section">
      <h2>{$_('settings.title', { default: 'Settings' })}</h2>
      <div class="demo-content">
        <div class="demo-setting">
          <label for="language-switcher">{$_('settings.language', { default: 'Language' })}</label>
          <LanguageSwitcher />
        </div>
        <div class="demo-buttons">
          <button class="demo-button">{$_('dialog.cancel', { default: 'Cancel' })}</button>
          <button class="demo-button primary">{$_('dialog.ok', { default: 'OK' })}</button>
        </div>
      </div>
    </section>

    <section class="demo-section">
      <h2>{$_('error.unknownError', { default: 'Error Messages' })}</h2>
      <div class="demo-content">
        <div class="demo-error">
          {$_('error.fileNotFound', { default: 'File not found' })}
        </div>
        <div class="demo-error">
          {$_('error.cannotPlay', { default: 'Cannot play this file' })}
        </div>
      </div>
    </section>
  </div>
</div>

<style>
  .i18n-demo {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .demo-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e0e0e0;
  }

  .demo-header h1 {
    margin: 0;
    color: #333;
  }

  .demo-sections {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }

  .demo-section {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #e0e0e0;
  }

  .demo-section h2 {
    margin: 0 0 1rem 0;
    color: #333;
    font-size: 1.25rem;
  }

  .demo-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .demo-button {
    padding: 0.5rem 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .demo-button:hover {
    background: #f0f0f0;
    border-color: #999;
  }

  .demo-button.primary {
    background: #007acc;
    color: white;
    border-color: #007acc;
  }

  .demo-button.primary:hover {
    background: #0056b3;
    border-color: #0056b3;
  }

  .demo-text {
    margin: 0.5rem 0;
    color: #666;
  }

  .demo-table {
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
  }

  .demo-table-header {
    display: grid;
    grid-template-columns: 2fr 1.5fr 1.5fr 1fr;
    background: #e9ecef;
    padding: 0.75rem;
    font-weight: 600;
    border-bottom: 1px solid #ddd;
  }

  .demo-table-row {
    display: grid;
    grid-template-columns: 2fr 1.5fr 1.5fr 1fr;
    padding: 0.75rem;
    background: white;
  }

  .demo-controls {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .demo-setting {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
  }

  .demo-buttons {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
  }

  .demo-error {
    padding: 0.75rem;
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    color: #c33;
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .i18n-demo {
      background: #1a202c;
      color: #f7fafc;
    }

    .demo-header {
      border-bottom-color: #4a5568;
    }

    .demo-header h1 {
      color: #f7fafc;
    }

    .demo-section {
      background: #2d3748;
      border-color: #4a5568;
    }

    .demo-section h2 {
      color: #f7fafc;
    }

    .demo-button {
      background: #4a5568;
      border-color: #718096;
      color: #f7fafc;
    }

    .demo-button:hover {
      background: #718096;
    }

    .demo-table-header {
      background: #4a5568;
      border-bottom-color: #718096;
    }

    .demo-table-row {
      background: #2d3748;
    }

    .demo-table {
      border-color: #4a5568;
    }

    .demo-error {
      background: #742a2a;
      border-color: #9b2c2c;
      color: #feb2b2;
    }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .i18n-demo {
      padding: 1rem;
    }

    .demo-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .demo-sections {
      grid-template-columns: 1fr;
    }

    .demo-table-header,
    .demo-table-row {
      grid-template-columns: 1fr;
      gap: 0.25rem;
    }

    .demo-controls {
      justify-content: center;
    }

    .demo-setting {
      flex-direction: column;
      gap: 0.5rem;
      align-items: stretch;
    }
  }
</style>