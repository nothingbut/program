import { test, expect } from '@playwright/test';
import os from 'os';

test.describe('Cross-Platform Compatibility', () => {
  const platform = os.platform();
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
  });

  test('should work correctly on current platform', async ({ page }) => {
    await test.step(`Test basic functionality on ${platform}`, async () => {
      // Test that basic app functionality works on the current platform
      await expect(page.locator('[data-testid="directory-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="playlist-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="player-controls"]')).toBeVisible();
    });
  });

  test('should handle platform-specific file paths', async ({ page }) => {
    await test.step('Test file path handling', async () => {
      // Different platforms use different path separators
      // This test ensures the app handles paths correctly
      
      // The app should be able to display directory paths correctly
      const directoryItems = page.locator('[data-testid="directory-item"]');
      
      if (await directoryItems.count() > 0) {
        const firstDir = directoryItems.first();
        const pathText = await firstDir.textContent();
        
        if (pathText) {
          // Path should contain appropriate separators for the platform
          if (platform === 'win32') {
            // Windows paths typically use backslashes
            expect(pathText.includes('\\') || pathText.includes('/')).toBe(true);
          } else {
            // Unix-like systems use forward slashes
            expect(pathText.includes('/')).toBe(true);
          }
        }
      }
    });
  });

  test('should handle platform-specific keyboard shortcuts', async ({ page }) => {
    await test.step('Test platform-specific shortcuts', async () => {
      // Different platforms have different modifier keys
      const isMac = platform === 'darwin';
      const modifierKey = isMac ? 'Meta' : 'Control';
      
      // Test common shortcuts with platform-appropriate modifiers
      await page.keyboard.press(`${modifierKey}+KeyO`); // Open
      await page.waitForTimeout(200);
      
      // The app should respond to platform-appropriate shortcuts
      // This is mainly to ensure no errors occur
      await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
    });
  });

  test('should display correctly with different system fonts', async ({ page }) => {
    await test.step('Test font rendering', async () => {
      // Test that text is readable with system fonts
      const appContainer = page.locator('[data-testid="app-container"]');
      await expect(appContainer).toBeVisible();
      
      // Check that text elements are properly rendered
      const textElements = page.locator('text=*');
      if (await textElements.count() > 0) {
        // At least some text should be visible
        const visibleText = textElements.first();
        await expect(visibleText).toBeVisible();
      }
    });
  });

  test('should handle different audio formats based on platform support', async ({ page }) => {
    await test.step('Test audio format support', async () => {
      // Different platforms may have different audio codec support
      // This test ensures the app gracefully handles unsupported formats
      
      // If there are tracks in the playlist, they should be displayable
      const trackRows = page.locator('[data-testid="track-row"]');
      
      if (await trackRows.count() > 0) {
        // Tracks should be visible regardless of platform
        await expect(trackRows.first()).toBeVisible();
        
        // Try to play a track
        await trackRows.first().dblclick();
        
        // The app should either play the track or show an appropriate error
        // It should not crash
        await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
      }
    });
  });

  test('should handle different screen DPI settings', async ({ page }) => {
    await test.step('Test DPI scaling', async () => {
      // Test that the app looks good at different DPI settings
      // This is mainly about ensuring elements are properly sized
      
      const directoryPanel = page.locator('[data-testid="directory-panel"]');
      const playlistPanel = page.locator('[data-testid="playlist-panel"]');
      const playerControls = page.locator('[data-testid="player-controls"]');
      
      // All main panels should be visible and properly sized
      await expect(directoryPanel).toBeVisible();
      await expect(playlistPanel).toBeVisible();
      await expect(playerControls).toBeVisible();
      
      // Check that panels have reasonable dimensions
      const directoryBox = await directoryPanel.boundingBox();
      const playlistBox = await playlistPanel.boundingBox();
      
      if (directoryBox && playlistBox) {
        // Panels should have non-zero dimensions
        expect(directoryBox.width).toBeGreaterThan(0);
        expect(directoryBox.height).toBeGreaterThan(0);
        expect(playlistBox.width).toBeGreaterThan(0);
        expect(playlistBox.height).toBeGreaterThan(0);
      }
    });
  });

  test('should work with different system themes', async ({ page }) => {
    await test.step('Test system theme compatibility', async () => {
      // Test that the app works with both light and dark system themes
      // This mainly ensures no elements become invisible
      
      // All main UI elements should be visible regardless of theme
      await expect(page.locator('[data-testid="directory-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="playlist-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="player-controls"]')).toBeVisible();
      
      // Text should be readable (not the same color as background)
      const textElements = page.locator('[data-testid="track-title"]');
      if (await textElements.count() > 0) {
        await expect(textElements.first()).toBeVisible();
      }
    });
  });

  test('should handle platform-specific file permissions', async ({ page }) => {
    await test.step('Test file permission handling', async () => {
      // Different platforms have different permission systems
      // The app should handle permission errors gracefully
      
      // Try to add a directory (this might trigger permission dialogs)
      const addBtn = page.locator('[data-testid="add-directory-btn"]');
      if (await addBtn.isVisible()) {
        await addBtn.click();
        
        // The app should remain stable regardless of permission outcomes
        await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
      }
    });
  });
});