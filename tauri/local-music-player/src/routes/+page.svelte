<script lang="ts">
  import App from '../App.svelte';
</script>

<App />

<style>
  :global(html, body) {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
  }
  
  :global(#app) {
    height: 100vh;
  }
</style>
