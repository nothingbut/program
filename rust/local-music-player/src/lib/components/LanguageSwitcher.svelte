<script lang="ts">
  import { locale } from 'svelte-i18n';
  import { setLanguage, availableLanguages } from '$lib/i18n';

  let currentLocale: string;
  
  locale.subscribe(value => {
    currentLocale = value || 'en';
  });

  function handleLanguageChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    setLanguage(target.value);
  }
</script>

<div class="language-switcher">
  <select 
    bind:value={currentLocale} 
    on:change={handleLanguageChange}
    class="language-select"
    aria-label="Select Language"
  >
    {#each availableLanguages as lang}
      <option value={lang.code}>{lang.name}</option>
    {/each}
  </select>
</div>

<style>
  .language-switcher {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .language-select {
    padding: 0.25rem 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: white;
    font-size: 0.875rem;
    cursor: pointer;
    transition: border-color 0.2s ease;
  }

  .language-select:hover {
    border-color: #999;
  }

  .language-select:focus {
    outline: none;
    border-color: #007acc;
    box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
  }

  /* Dark theme support */
  @media (prefers-color-scheme: dark) {
    .language-select {
      background: #2a2a2a;
      border-color: #555;
      color: white;
    }

    .language-select:hover {
      border-color: #777;
    }
  }
</style>