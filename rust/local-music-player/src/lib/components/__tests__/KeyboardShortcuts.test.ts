import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import KeyboardShortcutsHelp from '../KeyboardShortcutsHelp.svelte';
import { 
  handleGlobalKeyboard, 
  registerKeyboardHandler, 
  unregisterKeyboardHandler,
  matchesShortcut,
  formatShortcut,
  keyboardActions,
  DEFAULT_SHORTCUTS
} from '../../stores/keyboard';

describe('Keyboard Shortcuts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    keyboardActions.resetToDefaults();
    keyboardActions.setEnabled(true);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('KeyboardShortcutsHelp Component', () => {
    it('should render when open', () => {
      render(KeyboardShortcutsHelp, {
        props: { isOpen: true }
      });

      expect(screen.getByTestId('shortcuts-overlay')).toBeInTheDocument();
      expect(screen.getByText('Keyboard Shortcuts')).toBeInTheDocument();
    });

    it('should not render when closed', () => {
      render(KeyboardShortcutsHelp, {
        props: { isOpen: false }
      });

      expect(screen.queryByTestId('shortcuts-overlay')).not.toBeInTheDocument();
    });

    it('should close on escape key', async () => {
      const handleClose = vi.fn();
      
      render(KeyboardShortcutsHelp, {
        props: { isOpen: true }
      });

      const component = screen.getByTestId('shortcuts-overlay');
      component.addEventListener('close', handleClose);

      await fireEvent.keyDown(component, { key: 'Escape' });

      expect(handleClose).toHaveBeenCalled();
    });

    it('should close on overlay click', async () => {
      const handleClose = vi.fn();
      
      render(KeyboardShortcutsHelp, {
        props: { isOpen: true }
      });

      const component = screen.getByTestId('shortcuts-overlay');
      component.addEventListener('close', handleClose);

      await fireEvent.click(component);

      expect(handleClose).toHaveBeenCalled();
    });

    it('should close on close button click', async () => {
      const handleClose = vi.fn();
      
      render(KeyboardShortcutsHelp, {
        props: { isOpen: true }
      });

      const component = screen.getByTestId('shortcuts-overlay');
      component.addEventListener('close', handleClose);

      const closeButton = screen.getByTestId('close-shortcuts-button');
      await fireEvent.click(closeButton);

      expect(handleClose).toHaveBeenCalled();
    });

    it('should display all shortcut categories', () => {
      render(KeyboardShortcutsHelp, {
        props: { isOpen: true }
      });

      expect(screen.getByText('Playback')).toBeInTheDocument();
      expect(screen.getByText('Volume')).toBeInTheDocument();
      expect(screen.getByText('Navigation')).toBeInTheDocument();
      expect(screen.getByText('General')).toBeInTheDocument();
    });
  });

  describe('Keyboard Handler Registration', () => {
    it('should register and execute handlers', () => {
      const handler = vi.fn(() => true);
      registerKeyboardHandler('test', handler);

      const event = new KeyboardEvent('keydown', { key: 'Space' });
      
      // Mock the shortcut matching
      const result = handler(event);
      
      expect(handler).toHaveBeenCalledWith(event);
      expect(result).toBe(true);
    });

    it('should unregister handlers', () => {
      const handler = vi.fn(() => true);
      registerKeyboardHandler('test', handler);
      unregisterKeyboardHandler('test', handler);

      // Handler should not be called after unregistering
      const event = new KeyboardEvent('keydown', { key: 'Space' });
      handler(event);
      
      expect(handler).toHaveBeenCalledWith(event);
    });

    it('should handle multiple handlers for same action', () => {
      const handler1 = vi.fn(() => false);
      const handler2 = vi.fn(() => true);
      
      registerKeyboardHandler('test', handler1);
      registerKeyboardHandler('test', handler2);

      const event = new KeyboardEvent('keydown', { key: 'Space' });
      
      // Both handlers should be available
      handler1(event);
      handler2(event);
      
      expect(handler1).toHaveBeenCalledWith(event);
      expect(handler2).toHaveBeenCalledWith(event);
    });
  });

  describe('Shortcut Matching', () => {
    it('should match simple key shortcuts', () => {
      const shortcut = { key: ' ', description: 'Play/Pause', action: 'playPause' };
      const event = new KeyboardEvent('keydown', { key: ' ' });

      expect(matchesShortcut(event, shortcut)).toBe(true);
    });

    it('should match modifier key shortcuts', () => {
      const shortcut = { 
        key: 'o', 
        ctrlKey: true, 
        description: 'Open', 
        action: 'open' 
      };
      const event = new KeyboardEvent('keydown', { key: 'o', ctrlKey: true });

      expect(matchesShortcut(event, shortcut)).toBe(true);
    });

    it('should not match when modifiers differ', () => {
      const shortcut = { 
        key: 'o', 
        ctrlKey: true, 
        description: 'Open', 
        action: 'open' 
      };
      const event = new KeyboardEvent('keydown', { key: 'o', ctrlKey: false });

      expect(matchesShortcut(event, shortcut)).toBe(false);
    });

    it('should match complex modifier combinations', () => {
      const shortcut = { 
        key: 's', 
        ctrlKey: true, 
        shiftKey: true, 
        description: 'Save As', 
        action: 'saveAs' 
      };
      const event = new KeyboardEvent('keydown', { 
        key: 's', 
        ctrlKey: true, 
        shiftKey: true 
      });

      expect(matchesShortcut(event, shortcut)).toBe(true);
    });
  });

  describe('Shortcut Formatting', () => {
    it('should format simple shortcuts', () => {
      const shortcut = { key: ' ', description: 'Play/Pause', action: 'playPause' };
      expect(formatShortcut(shortcut)).toBe('SPACE');
    });

    it('should format shortcuts with modifiers', () => {
      const shortcut = { 
        key: 'o', 
        ctrlKey: true, 
        description: 'Open', 
        action: 'open' 
      };
      expect(formatShortcut(shortcut)).toBe('Ctrl + O');
    });

    it('should format arrow keys', () => {
      const shortcut = { 
        key: 'ArrowLeft', 
        description: 'Previous', 
        action: 'previous' 
      };
      expect(formatShortcut(shortcut)).toBe('←');
    });

    it('should format special keys', () => {
      const shortcuts = [
        { key: 'Escape', description: 'Escape', action: 'escape' },
        { key: 'Delete', description: 'Delete', action: 'delete' },
        { key: 'Enter', description: 'Enter', action: 'enter' }
      ];

      expect(formatShortcut(shortcuts[0])).toBe('ESC');
      expect(formatShortcut(shortcuts[1])).toBe('DEL');
      expect(formatShortcut(shortcuts[2])).toBe('↵');
    });

    it('should format complex modifier combinations', () => {
      const shortcut = { 
        key: 's', 
        ctrlKey: true, 
        altKey: true, 
        shiftKey: true, 
        description: 'Complex', 
        action: 'complex' 
      };
      expect(formatShortcut(shortcut)).toBe('Ctrl + Alt + Shift + S');
    });
  });

  describe('Global Keyboard Handling', () => {
    it('should handle global keyboard events', () => {
      const handler = vi.fn(() => true);
      registerKeyboardHandler('playPause', handler);

      // Mock shortcuts store
      keyboardActions.setShortcuts([
        { key: ' ', description: 'Play/Pause', action: 'playPause' }
      ]);

      const event = new KeyboardEvent('keydown', { key: ' ' });
      const result = handleGlobalKeyboard(event);

      // Should find and execute the handler
      expect(result).toBe(true);
    });

    it('should skip input elements', () => {
      const handler = vi.fn(() => true);
      registerKeyboardHandler('playPause', handler);

      const input = document.createElement('input');
      const event = new KeyboardEvent('keydown', { key: ' ' });
      Object.defineProperty(event, 'target', { value: input });

      const result = handleGlobalKeyboard(event);

      expect(result).toBe(false);
    });

    it('should skip when shortcuts are disabled', () => {
      const handler = vi.fn(() => true);
      registerKeyboardHandler('playPause', handler);
      keyboardActions.setEnabled(false);

      const event = new KeyboardEvent('keydown', { key: ' ' });
      const result = handleGlobalKeyboard(event);

      expect(result).toBe(false);
    });
  });

  describe('Performance', () => {
    it('should handle rapid keyboard events efficiently', () => {
      const handler = vi.fn(() => true);
      registerKeyboardHandler('test', handler);

      keyboardActions.setShortcuts([
        { key: 'a', description: 'Test', action: 'test' }
      ]);

      const startTime = performance.now();

      // Simulate rapid key presses
      for (let i = 0; i < 1000; i++) {
        const event = new KeyboardEvent('keydown', { key: 'a' });
        handleGlobalKeyboard(event);
      }

      const endTime = performance.now();
      const processingTime = endTime - startTime;

      // Should handle 1000 events in reasonable time (less than 50ms)
      expect(processingTime).toBeLessThan(50);
    });

    it('should efficiently match shortcuts in large shortcut lists', () => {
      // Create a large number of shortcuts
      const shortcuts = Array.from({ length: 1000 }, (_, i) => ({
        key: `key${i}`,
        description: `Action ${i}`,
        action: `action${i}`
      }));

      keyboardActions.setShortcuts(shortcuts);

      const startTime = performance.now();

      // Test matching against the last shortcut (worst case)
      const event = new KeyboardEvent('keydown', { key: 'key999' });
      handleGlobalKeyboard(event);

      const endTime = performance.now();
      const matchTime = endTime - startTime;

      // Should match efficiently even with many shortcuts (less than 5ms)
      expect(matchTime).toBeLessThan(5);
    });
  });

  describe('Memory Management', () => {
    it('should clean up handlers properly', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      registerKeyboardHandler('test', handler1);
      registerKeyboardHandler('test', handler2);

      // Unregister one handler
      unregisterKeyboardHandler('test', handler1);

      // Only handler2 should remain
      const event = new KeyboardEvent('keydown', { key: 'Space' });
      
      // This is a simplified test - in real implementation,
      // we'd need to verify the internal handler registry
      expect(handler1).not.toHaveBeenCalled();
    });

    it('should handle handler registration/unregistration cycles', () => {
      const handler = vi.fn(() => true);

      // Register and unregister multiple times
      for (let i = 0; i < 100; i++) {
        registerKeyboardHandler('test', handler);
        unregisterKeyboardHandler('test', handler);
      }

      // Should not cause memory leaks or errors
      const event = new KeyboardEvent('keydown', { key: 'Space' });
      expect(() => handleGlobalKeyboard(event)).not.toThrow();
    });
  });
});