# Internationalization (i18n) Implementation

This document describes the internationalization implementation for the Local MP3 Player application.

## Overview

The application supports multiple languages using the `svelte-i18n` library. Currently supported languages:

- **English (en)** - Default language
- **Chinese (zh)** - 中文支持

## Implementation Details

### Libraries Used

- `svelte-i18n` - Main internationalization library for Svelte
- Automatic locale detection from browser/localStorage
- Fallback to English if translation is missing

### File Structure

```
src/lib/i18n/
├── index.ts              # i18n configuration and setup
├── locales/
│   ├── en.json          # English translations
│   └── zh.json          # Chinese translations
└── components/
    └── LanguageSwitcher.svelte  # Language selection component
```

### Key Features

1. **Automatic Language Detection**
   - Detects browser language on first visit
   - Persists language choice in localStorage
   - Falls back to English if language not supported

2. **Dynamic Language Switching**
   - Language switcher component in the status bar
   - Instant language switching without page reload
   - Window title updates based on selected language

3. **Comprehensive Translation Coverage**
   - App title and loading messages
   - Directory panel (titles, buttons, messages)
   - Playlist panel (headers, empty states, loading)
   - Player controls (buttons, tooltips)
   - Settings and dialogs
   - Error messages

4. **Fallback System**
   - All translation calls include default English text
   - Graceful degradation if translation is missing
   - No broken UI if translation files are incomplete

## Usage

### Adding New Translations

1. **Add to language files:**
   ```json
   // en.json
   {
     "section": {
       "key": "English text"
     }
   }
   
   // zh.json
   {
     "section": {
       "key": "中文文本"
     }
   }
   ```

2. **Use in components:**
   ```svelte
   <script>
     import { _ } from 'svelte-i18n';
   </script>
   
   <h1>{$_('section.key', { default: 'English text' })}</h1>
   ```

### Language Switcher Component

```svelte
<script>
  import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
</script>

<LanguageSwitcher />
```

### Programmatic Language Change

```typescript
import { setLanguage } from '$lib/i18n';

// Change to Chinese
setLanguage('zh');

// Change to English
setLanguage('en');
```

## Translation Keys Structure

### App Level
- `app.title` - Application title
- `app.loading` - Loading message
- `app.ready` - Ready status

### Directory Management
- `directory.title` - "Music Directories"
- `directory.add` - "Add Directory"
- `directory.empty` - Empty state message
- `directory.select` - Selection instruction
- `directory.remove` - "Remove Directory"
- `directory.scan` - "Scanning..."
- `directory.error` - Error message

### Playlist
- `playlist.title` - "Playlist"
- `playlist.empty` - Empty state message
- `playlist.loading` - Loading message
- `playlist.columns.*` - Column headers (title, artist, album, track, duration)
- `playlist.unknown` - "Unknown" for missing metadata

### Player Controls
- `player.play` - "Play"
- `player.pause` - "Pause"
- `player.previous` - "Previous"
- `player.next` - "Next"
- `player.shuffle` - "Shuffle"
- `player.repeat` - "Repeat"
- `player.volume` - "Volume"
- `player.mute` - "Mute"

### Settings & Dialogs
- `settings.title` - "Settings"
- `settings.language` - "Language"
- `dialog.confirm` - "Confirm"
- `dialog.cancel` - "Cancel"
- `dialog.ok` - "OK"
- `dialog.yes` - "Yes"
- `dialog.no` - "No"

### Error Messages
- `error.fileNotFound` - "File not found"
- `error.cannotPlay` - "Cannot play this file"
- `error.networkError` - "Network error"
- `error.unknownError` - "An unknown error occurred"

## Demo Page

Visit `/demo` to see all translations in action. The demo page showcases:

- Language switcher functionality
- All major UI text translations
- Real-time language switching
- Responsive design with i18n support

## Browser Support

- Modern browsers with ES6+ support
- Automatic language detection works in all major browsers
- localStorage persistence supported in all modern browsers

## Performance

- Lazy loading of translation files
- Only loads the selected language
- Minimal bundle size impact
- Fast language switching with no page reload

## Future Enhancements

Potential improvements for the i18n system:

1. **Additional Languages**
   - Japanese (ja)
   - Korean (ko)
   - Spanish (es)
   - French (fr)
   - German (de)

2. **Advanced Features**
   - Pluralization support
   - Date/time formatting
   - Number formatting
   - RTL language support

3. **Developer Tools**
   - Translation key extraction
   - Missing translation detection
   - Translation validation

## Testing

The i18n implementation includes:

- Language switching functionality
- Translation fallback system
- Persistent language selection
- Dynamic window title updates

Test the implementation by:
1. Opening the app
2. Using the language switcher in the status bar
3. Visiting the `/demo` page
4. Refreshing the page to verify persistence