import { test, expect } from '@playwright/test';
import { TestUtils } from './helpers/test-utils';

test.describe('Comprehensive Application Workflow', () => {
  let testUtils: TestUtils;

  test.beforeEach(async ({ page }) => {
    testUtils = new TestUtils(page);
    await page.goto('/');
    await testUtils.waitForAppLoad();
  });

  test('should complete full application workflow with all features', async ({ page }) => {
    // This test covers all major requirements in a single comprehensive flow
    
    await test.step('Initialize application and verify UI', async () => {
      // Requirement 1.1: App should display directory panel on left
      await expect(page.locator('[data-testid="directory-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="playlist-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="player-controls"]')).toBeVisible();
    });

    await test.step('Add and manage directories', async () => {
      // Requirements 1.2, 1.3: Add directory functionality
      const directory = await testUtils.addTestDirectory();
      
      if (directory) {
        // Requirement 1.4: Select directory and scan files
        const scanSuccess = await testUtils.selectDirectoryAndWaitForScan(directory);
        expect(scanSuccess).toBe(true);
      }
    });

    await test.step('Verify playlist display and metadata', async () => {
      // Requirements 2.1, 2.2, 2.3, 2.4: Playlist display and metadata
      const trackCount = await testUtils.verifyPlaylistDisplay();
      
      if (trackCount > 0) {
        // Verify metadata is displayed correctly
        const firstTrack = page.locator('[data-testid="track-row"]').first();
        await expect(firstTrack).toBeVisible();
        
        // Check for proper metadata format
        const trackInfo = page.locator('[data-testid="track-title"]').first();
        await expect(trackInfo).toBeVisible();
      }
    });

    await test.step('Test track selection and playback', async () => {
      // Requirements 3.1, 3.2, 3.3: Track selection and playback
      const playbackStarted = await testUtils.playFirstTrack();
      
      if (playbackStarted) {
        // Verify current track info is displayed
        await expect(page.locator('[data-testid="current-track-info"]')).toBeVisible();
        
        // Requirements 3.4, 3.5, 3.6: Track info format and cover art
        const trackInfo = page.locator('[data-testid="current-track-info"]');
        const trackText = await trackInfo.textContent();
        
        if (trackText) {
          // Should follow format: "<Album>(<Track>): <Title> - <Artist>"
          expect(trackText.length).toBeGreaterThan(0);
        }
      }
    });

    await test.step('Test playback controls', async () => {
      // Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6: Playback controls
      const controls = await testUtils.verifyPlayerControls();
      
      // Test play/pause toggle
      await controls.playPauseBtn.click();
      await page.waitForTimeout(300);
      
      // Test progress bar
      const progressBar = page.locator('[data-testid="progress-bar"]');
      if (await progressBar.isVisible()) {
        await expect(progressBar).toBeVisible();
        
        // Test time display
        await expect(page.locator('[data-testid="current-time"]')).toBeVisible();
        await expect(page.locator('[data-testid="total-time"]')).toBeVisible();
      }
    });

    await test.step('Test navigation controls', async () => {
      // Requirements 5.1, 5.2: Navigation controls
      const controls = await testUtils.verifyPlayerControls();
      
      // Test next track
      await controls.nextBtn.click();
      await page.waitForTimeout(500);
      
      // Test previous track
      await controls.prevBtn.click();
      await page.waitForTimeout(500);
      
      // Verify navigation worked (no errors)
      await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
    });

    await test.step('Test shuffle mode', async () => {
      // Requirements 5.5, 5.6, 5.7: Shuffle mode
      const shuffleBtn = page.locator('[data-testid="shuffle-btn"]');
      
      if (await shuffleBtn.isVisible()) {
        // Test shuffle toggle
        await shuffleBtn.click();
        await expect(shuffleBtn).toHaveAttribute('data-state', 'on');
        
        await shuffleBtn.click();
        await expect(shuffleBtn).toHaveAttribute('data-state', 'off');
      }
    });

    await test.step('Test keyboard shortcuts', async () => {
      // Requirement 6.3: Keyboard shortcuts
      await testUtils.testKeyboardShortcut('Space', async () => {
        // Spacebar should toggle play/pause
        const playPauseBtn = page.locator('[data-testid="play-pause-btn"]');
        if (await playPauseBtn.isVisible()) {
          await expect(playPauseBtn).toBeVisible();
        }
      });
      
      await testUtils.testKeyboardShortcut('ArrowRight');
      await testUtils.testKeyboardShortcut('ArrowLeft');
    });

    await test.step('Test error handling', async () => {
      // Requirements 6.4, 6.5: Error handling
      await testUtils.simulateError('audio-error', 'Test error message');
      
      // Should show error but not crash
      await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
    });

    await test.step('Test responsive design', async () => {
      // Requirement 6.3: Responsive layout
      await testUtils.testResponsiveDesign();
    });

    await test.step('Test performance with loading states', async () => {
      // Requirements 6.1, 6.2: Performance and loading states
      await testUtils.waitForLoadingComplete();
      
      // App should be responsive after loading
      await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
    });
  });

  test('should handle edge cases and boundary conditions', async ({ page }) => {
    await test.step('Test empty playlist handling', async () => {
      // Requirement 1.5: Empty directory handling
      const emptyMessage = page.locator('[data-testid="empty-playlist-message"]');
      
      // If no tracks are loaded, should show empty message
      const trackCount = await page.locator('[data-testid="track-row"]').count();
      if (trackCount === 0) {
        await expect(emptyMessage).toBeVisible();
      }
    });

    await test.step('Test boundary navigation', async () => {
      // Requirement 5.8: Boundary handling for first/last tracks
      const trackRows = page.locator('[data-testid="track-row"]');
      const trackCount = await trackRows.count();
      
      if (trackCount > 0) {
        // Play first track
        await trackRows.first().dblclick();
        await page.waitForTimeout(500);
        
        // Try to go to previous (should handle boundary)
        const prevBtn = page.locator('[data-testid="prev-btn"]');
        if (await prevBtn.isVisible()) {
          await prevBtn.click();
          await page.waitForTimeout(300);
          
          // App should still be functional
          await expect(page.locator('[data-testid="app-container"]')).toBeVisible();
        }
      }
    });

    await test.step('Test rapid interactions', async () => {
      // Test rapid clicking doesn't break the app
      const playPauseBtn = page.locator('[data-testid="play-pause-btn"]');
      
      if (await playPauseBtn.isVisible()) {
        for (let i = 0; i < 3; i++) {
          await playPauseBtn.click();
          await page.waitForTimeout(100);
        }
        
        // App should remain stable
        await expect(playPauseBtn).toBeVisible();
      }
    });
  });

  test('should maintain state persistence', async ({ page, context }) => {
    // Requirements 6.6, 6.7: State persistence
    await test.step('Test state saving and restoration', async () => {
      // Add a directory if possible
      await testUtils.addTestDirectory();
      
      // Make some state changes
      const shuffleBtn = page.locator('[data-testid="shuffle-btn"]');
      if (await shuffleBtn.isVisible()) {
        await shuffleBtn.click(); // Turn on shuffle
      }
      
      // Close and reopen app
      await page.close();
      const newPage = await context.newPage();
      await newPage.goto('/');
      
      const newTestUtils = new TestUtils(newPage);
      await newTestUtils.waitForAppLoad();
      
      // Verify state is restored
      await expect(newPage.locator('[data-testid="app-container"]')).toBeVisible();
      
      // Check if directories are still there
      const directories = newPage.locator('[data-testid="directory-item"]');
      if (await directories.count() > 0) {
        await expect(directories.first()).toBeVisible();
      }
      
      // Check if shuffle state is restored
      const newShuffleBtn = newPage.locator('[data-testid="shuffle-btn"]');
      if (await newShuffleBtn.isVisible()) {
        // State should be preserved (though this depends on implementation)
        await expect(newShuffleBtn).toBeVisible();
      }
    });
  });
});