import { Page, expect } from '@playwright/test';

/**
 * Helper functions for end-to-end tests
 */

export class TestUtils {
  constructor(private page: Page) {}

  /**
   * Wait for the app to fully load
   */
  async waitForAppLoad() {
    await expect(this.page.locator('[data-testid="app-container"]')).toBeVisible();
    // Wait for any initial loading to complete
    await this.page.waitForTimeout(1000);
  }

  /**
   * Add a test directory (mocked)
   */
  async addTestDirectory(directoryName: string = 'Test Music') {
    await this.page.click('[data-testid="add-directory-btn"]');
    
    // In a real test, we would need to handle the file dialog
    // For now, we simulate the directory being added
    await this.page.waitForTimeout(1000);
    
    // Check if directory was added
    const directoryItems = this.page.locator('[data-testid="directory-item"]');
    if (await directoryItems.count() > 0) {
      return directoryItems.first();
    }
    return null;
  }

  /**
   * Select a directory and wait for scanning to complete
   */
  async selectDirectoryAndWaitForScan(directoryLocator?: any) {
    const directory = directoryLocator || this.page.locator('[data-testid="directory-item"]').first();
    
    if (await directory.isVisible()) {
      await directory.click();
      
      // Wait for scanning to start and complete
      const scanProgress = this.page.locator('[data-testid="scan-progress"]');
      if (await scanProgress.isVisible()) {
        await expect(scanProgress).toBeHidden({ timeout: 15000 });
      }
      
      return true;
    }
    return false;
  }

  /**
   * Play the first available track
   */
  async playFirstTrack() {
    const firstTrack = this.page.locator('[data-testid="track-row"]').first();
    
    if (await firstTrack.isVisible()) {
      await firstTrack.dblclick();
      
      // Wait for playback to start
      await this.page.waitForTimeout(500);
      
      return true;
    }
    return false;
  }

  /**
   * Check if player controls are visible and functional
   */
  async verifyPlayerControls() {
    const playerControls = this.page.locator('[data-testid="player-controls"]');
    await expect(playerControls).toBeVisible();
    
    const playPauseBtn = this.page.locator('[data-testid="play-pause-btn"]');
    const nextBtn = this.page.locator('[data-testid="next-btn"]');
    const prevBtn = this.page.locator('[data-testid="prev-btn"]');
    
    await expect(playPauseBtn).toBeVisible();
    await expect(nextBtn).toBeVisible();
    await expect(prevBtn).toBeVisible();
    
    return {
      playPauseBtn,
      nextBtn,
      prevBtn
    };
  }

  /**
   * Verify playlist is displayed with tracks
   */
  async verifyPlaylistDisplay() {
    const playlistPanel = this.page.locator('[data-testid="playlist-panel"]');
    await expect(playlistPanel).toBeVisible();
    
    const trackRows = this.page.locator('[data-testid="track-row"]');
    const trackCount = await trackRows.count();
    
    if (trackCount > 0) {
      // Verify track metadata columns
      await expect(this.page.locator('[data-testid="track-title"]').first()).toBeVisible();
      await expect(this.page.locator('[data-testid="track-artist"]').first()).toBeVisible();
      await expect(this.page.locator('[data-testid="track-album"]').first()).toBeVisible();
      await expect(this.page.locator('[data-testid="track-duration"]').first()).toBeVisible();
    }
    
    return trackCount;
  }

  /**
   * Test keyboard shortcut
   */
  async testKeyboardShortcut(key: string, expectedResult?: () => Promise<void>) {
    await this.page.locator('[data-testid="app-container"]').focus();
    await this.page.keyboard.press(key);
    await this.page.waitForTimeout(200);
    
    if (expectedResult) {
      await expectedResult();
    }
  }

  /**
   * Simulate an error condition
   */
  async simulateError(errorType: string, message: string) {
    await this.page.evaluate(({ errorType, message }) => {
      window.dispatchEvent(new CustomEvent(errorType, { 
        detail: { message }
      }));
    }, { errorType, message });
  }

  /**
   * Check for error display
   */
  async verifyErrorDisplay(expectedMessage?: string) {
    const errorDisplay = this.page.locator('[data-testid="error-display"], [data-testid="error-message"]');
    await expect(errorDisplay).toBeVisible();
    
    if (expectedMessage) {
      await expect(errorDisplay).toContainText(expectedMessage);
    }
  }

  /**
   * Test responsive design at different viewport sizes
   */
  async testResponsiveDesign() {
    const viewports = [
      { width: 800, height: 600 },   // Minimum size
      { width: 1200, height: 800 },  // Default size
      { width: 1600, height: 1200 }  // Large size
    ];

    for (const viewport of viewports) {
      await this.page.setViewportSize(viewport);
      await this.page.waitForTimeout(300);
      
      // Verify main components are still visible
      await expect(this.page.locator('[data-testid="app-container"]')).toBeVisible();
      await expect(this.page.locator('[data-testid="directory-panel"]')).toBeVisible();
      await expect(this.page.locator('[data-testid="playlist-panel"]')).toBeVisible();
      await expect(this.page.locator('[data-testid="player-controls"]')).toBeVisible();
    }
  }

  /**
   * Wait for loading to complete
   */
  async waitForLoadingComplete() {
    const loadingIndicators = this.page.locator('[data-testid="loading"], [data-testid="scan-progress"]');
    
    // Wait for any loading indicators to disappear
    if (await loadingIndicators.count() > 0) {
      await expect(loadingIndicators.first()).toBeHidden({ timeout: 10000 });
    }
  }

  /**
   * Take a screenshot for debugging
   */
  async takeDebugScreenshot(name: string) {
    await this.page.screenshot({ 
      path: `tests/screenshots/${name}-${Date.now()}.png`,
      fullPage: true 
    });
  }
}

/**
 * Create test MP3 files for testing (mock implementation)
 */
export async function createTestAssets() {
  // In a real implementation, this would create actual test MP3 files
  // For now, this is a placeholder for the test setup
  return {
    testDirectory: 'tests/test-assets',
    testFiles: [
      'test-song-1.mp3',
      'test-song-2.mp3',
      'test-song-3.mp3'
    ]
  };
}

/**
 * Clean up test assets
 */
export async function cleanupTestAssets() {
  // Clean up any test files created during testing
  // This would be implemented based on the actual test setup
}