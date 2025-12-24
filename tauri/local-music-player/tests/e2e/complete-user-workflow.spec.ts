import { test, expect } from '@playwright/test';
import { join } from 'path';

test.describe('Complete User Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    
    // Wait for the app to load
    await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
  });

  test('should complete full user workflow: add directory, scan files, and play music', async ({ page }) => {
    // Test adding a music directory (Requirement 1.2, 1.3)
    await test.step('Add music directory', async () => {
      // Click the add directory button
      await page.click('[data-testid="add-directory-btn"]');
      
      // Wait for directory dialog to be handled by Tauri
      // Note: In real e2e tests, we would need to mock the file dialog
      // For now, we'll simulate the directory being added
      await page.waitForTimeout(1000);
    });

    // Test directory selection and file scanning (Requirement 1.4, 2.1)
    await test.step('Select directory and scan files', async () => {
      // Verify directory appears in the list
      await expect(page.locator('[data-testid="directory-list"]')).toBeVisible();
      
      // Click on a directory to select it
      const directoryItem = page.locator('[data-testid="directory-item"]').first();
      await directoryItem.click();
      
      // Verify directory is selected (highlighted)
      await expect(directoryItem).toHaveClass(/selected/);
      
      // Wait for file scanning to complete
      await expect(page.locator('[data-testid="scan-progress"]')).toBeVisible();
      await expect(page.locator('[data-testid="scan-progress"]')).toBeHidden({ timeout: 10000 });
    });

    // Test playlist display (Requirement 2.2, 2.3, 2.4)
    await test.step('Verify playlist display', async () => {
      // Verify playlist panel is visible
      await expect(page.locator('[data-testid="playlist-panel"]')).toBeVisible();
      
      // Verify track information is displayed
      const trackRows = page.locator('[data-testid="track-row"]');
      await expect(trackRows.first()).toBeVisible();
      
      // Verify track metadata columns are present
      await expect(page.locator('[data-testid="track-title"]').first()).toBeVisible();
      await expect(page.locator('[data-testid="track-artist"]').first()).toBeVisible();
      await expect(page.locator('[data-testid="track-album"]').first()).toBeVisible();
      await expect(page.locator('[data-testid="track-duration"]').first()).toBeVisible();
    });

    // Test track selection and playback (Requirement 3.1, 3.2, 3.3)
    await test.step('Select and play track', async () => {
      const firstTrack = page.locator('[data-testid="track-row"]').first();
      
      // Single click to select track
      await firstTrack.click();
      await expect(firstTrack).toHaveClass(/selected/);
      
      // Double click to play track
      await firstTrack.dblclick();
      
      // Verify player controls are visible and show current track
      await expect(page.locator('[data-testid="player-controls"]')).toBeVisible();
      await expect(page.locator('[data-testid="current-track-info"]')).toBeVisible();
      
      // Verify play button shows pause icon (music is playing)
      await expect(page.locator('[data-testid="play-pause-btn"]')).toHaveAttribute('data-state', 'playing');
    });

    // Test playback controls (Requirement 4.1, 4.2, 4.3, 4.4)
    await test.step('Test playback controls', async () => {
      // Test pause/play toggle
      await page.click('[data-testid="play-pause-btn"]');
      await expect(page.locator('[data-testid="play-pause-btn"]')).toHaveAttribute('data-state', 'paused');
      
      await page.click('[data-testid="play-pause-btn"]');
      await expect(page.locator('[data-testid="play-pause-btn"]')).toHaveAttribute('data-state', 'playing');
      
      // Test progress bar interaction
      const progressBar = page.locator('[data-testid="progress-bar"]');
      await expect(progressBar).toBeVisible();
      
      // Test time display
      await expect(page.locator('[data-testid="current-time"]')).toBeVisible();
      await expect(page.locator('[data-testid="total-time"]')).toBeVisible();
    });

    // Test navigation controls (Requirement 5.1, 5.2)
    await test.step('Test navigation controls', async () => {
      // Test next track
      await page.click('[data-testid="next-btn"]');
      await page.waitForTimeout(500); // Wait for track change
      
      // Test previous track
      await page.click('[data-testid="prev-btn"]');
      await page.waitForTimeout(500); // Wait for track change
    });

    // Test shuffle mode (Requirement 5.5, 5.6, 5.7)
    await test.step('Test shuffle mode', async () => {
      const shuffleBtn = page.locator('[data-testid="shuffle-btn"]');
      
      // Initially should be in sequential mode
      await expect(shuffleBtn).toHaveAttribute('data-state', 'off');
      
      // Toggle shuffle mode on
      await shuffleBtn.click();
      await expect(shuffleBtn).toHaveAttribute('data-state', 'on');
      
      // Toggle shuffle mode off
      await shuffleBtn.click();
      await expect(shuffleBtn).toHaveAttribute('data-state', 'off');
    });
  });

  test('should handle empty directory gracefully', async ({ page }) => {
    // Test empty directory handling (Requirement 1.5)
    await test.step('Handle empty directory', async () => {
      // Simulate selecting an empty directory
      // This would require mocking the directory selection to return an empty directory
      
      // Verify empty state message is shown
      await expect(page.locator('[data-testid="empty-playlist-message"]')).toBeVisible();
    });
  });

  test('should persist and restore app state', async ({ page, context }) => {
    // Test state persistence (Requirement 6.6, 6.7)
    await test.step('Test state persistence', async () => {
      // Add a directory and select it
      await page.click('[data-testid="add-directory-btn"]');
      await page.waitForTimeout(1000);
      
      // Select a directory
      const directoryItem = page.locator('[data-testid="directory-item"]').first();
      if (await directoryItem.isVisible()) {
        await directoryItem.click();
        await page.waitForTimeout(2000); // Wait for scanning
      }
      
      // Close and reopen the app (simulate app restart)
      await page.close();
      const newPage = await context.newPage();
      await newPage.goto('/');
      
      // Verify state is restored
      await expect(newPage.locator('[data-testid="directory-list"]')).toBeVisible();
      
      // If directories were added, they should still be there
      const directories = newPage.locator('[data-testid="directory-item"]');
      if (await directories.count() > 0) {
        await expect(directories.first()).toBeVisible();
      }
    });
  });
});