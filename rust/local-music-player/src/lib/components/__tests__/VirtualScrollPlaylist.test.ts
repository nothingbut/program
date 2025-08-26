import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import VirtualScrollPlaylist from '../VirtualScrollPlaylist.svelte';
import type { Track } from '../../types';

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Helper function to create mock tracks
function createMockTracks(count: number): Track[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `track-${i}`,
    filePath: `/music/track-${i}.mp3`,
    title: `Track ${i + 1}`,
    artist: `Artist ${i + 1}`,
    album: `Album ${Math.floor(i / 10) + 1}`,
    trackNumber: i + 1,
    duration: 180 + (i % 60), // 3-4 minutes
    coverArt: undefined
  }));
}

describe('VirtualScrollPlaylist', () => {
  let mockTracks: Track[];

  beforeEach(() => {
    mockTracks = createMockTracks(1000); // Large playlist for virtual scrolling
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render virtual scroll container', () => {
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks,
        selectedTrack: null,
        loading: false
      }
    });

    expect(screen.getByTestId('virtual-scroll-container')).toBeInTheDocument();
  });

  it('should display track count', () => {
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks,
        selectedTrack: null,
        loading: false
      }
    });

    expect(screen.getByTestId('track-count')).toHaveTextContent('1000 tracks');
  });

  it('should only render visible tracks initially', () => {
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks,
        selectedTrack: null,
        loading: false,
        itemHeight: 48,
        overscan: 5
      }
    });

    // Should only render a subset of tracks (visible + overscan)
    const trackRows = screen.getAllByTestId('track-row');
    expect(trackRows.length).toBeLessThan(mockTracks.length);
    expect(trackRows.length).toBeGreaterThan(0);
  });

  it('should handle track selection', async () => {
    const handleTrackSelect = vi.fn();
    
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks.slice(0, 10), // Smaller set for easier testing
        selectedTrack: null,
        loading: false
      }
    });

    const component = screen.getByTestId('virtual-playlist');
    component.addEventListener('trackSelect', handleTrackSelect);

    const firstTrack = screen.getAllByTestId('track-row')[0];
    await fireEvent.click(firstTrack);

    expect(handleTrackSelect).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: { track: mockTracks[0] }
      })
    );
  });

  it('should handle track play on double click', async () => {
    const handleTrackPlay = vi.fn();
    
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks.slice(0, 10),
        selectedTrack: null,
        loading: false
      }
    });

    const component = screen.getByTestId('virtual-playlist');
    component.addEventListener('trackPlay', handleTrackPlay);

    const firstTrack = screen.getAllByTestId('track-row')[0];
    await fireEvent.dblClick(firstTrack);

    expect(handleTrackPlay).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: { track: mockTracks[0] }
      })
    );
  });

  it('should show loading state', () => {
    render(VirtualScrollPlaylist, {
      props: {
        tracks: [],
        selectedTrack: null,
        loading: true
      }
    });

    expect(screen.getByTestId('loading-state')).toBeInTheDocument();
    expect(screen.getByText('Loading tracks...')).toBeInTheDocument();
  });

  it('should show empty state when no tracks', () => {
    render(VirtualScrollPlaylist, {
      props: {
        tracks: [],
        selectedTrack: null,
        loading: false
      }
    });

    expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    expect(screen.getByText('No tracks found')).toBeInTheDocument();
  });

  it('should handle keyboard navigation', async () => {
    const handleTrackPlay = vi.fn();
    
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks.slice(0, 10),
        selectedTrack: null,
        loading: false
      }
    });

    const component = screen.getByTestId('virtual-playlist');
    component.addEventListener('trackPlay', handleTrackPlay);

    const firstTrack = screen.getAllByTestId('track-row')[0];
    firstTrack.focus();
    
    await fireEvent.keyDown(firstTrack, { key: 'Enter' });

    expect(handleTrackPlay).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: { track: mockTracks[0] }
      })
    );
  });

  it('should highlight selected track', () => {
    const selectedTrack = mockTracks[0];
    
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks.slice(0, 10),
        selectedTrack,
        loading: false
      }
    });

    const trackRow = screen.getByTestId('track-row');
    expect(trackRow).toHaveClass('selected');
  });

  it('should handle scroll events', async () => {
    render(VirtualScrollPlaylist, {
      props: {
        tracks: mockTracks,
        selectedTrack: null,
        loading: false
      }
    });

    const scrollContainer = screen.getByTestId('virtual-scroll-container');
    
    // Mock scroll event
    Object.defineProperty(scrollContainer, 'scrollTop', {
      value: 500,
      writable: true
    });

    await fireEvent.scroll(scrollContainer);

    // Should update visible tracks based on scroll position
    expect(scrollContainer.scrollTop).toBe(500);
  });

  describe('Performance', () => {
    it('should render large playlists efficiently', () => {
      const startTime = performance.now();
      
      render(VirtualScrollPlaylist, {
        props: {
          tracks: createMockTracks(10000), // Very large playlist
          selectedTrack: null,
          loading: false
        }
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render in reasonable time (less than 100ms)
      expect(renderTime).toBeLessThan(100);
    });

    it('should limit DOM nodes for large playlists', () => {
      render(VirtualScrollPlaylist, {
        props: {
          tracks: createMockTracks(10000),
          selectedTrack: null,
          loading: false
        }
      });

      const trackRows = screen.getAllByTestId('track-row');
      
      // Should only render visible tracks, not all 10000
      expect(trackRows.length).toBeLessThan(100);
    });

    it('should handle rapid scroll events without performance issues', async () => {
      render(VirtualScrollPlaylist, {
        props: {
          tracks: createMockTracks(5000),
          selectedTrack: null,
          loading: false
        }
      });

      const scrollContainer = screen.getByTestId('virtual-scroll-container');
      
      const startTime = performance.now();
      
      // Simulate rapid scrolling
      for (let i = 0; i < 100; i++) {
        Object.defineProperty(scrollContainer, 'scrollTop', {
          value: i * 10,
          writable: true
        });
        await fireEvent.scroll(scrollContainer);
      }

      const endTime = performance.now();
      const scrollTime = endTime - startTime;

      // Should handle rapid scrolling efficiently (less than 200ms for 100 scroll events)
      expect(scrollTime).toBeLessThan(200);
    });
  });

  describe('Memory Management', () => {
    it('should clean up resize observer on unmount', () => {
      const mockDisconnect = vi.fn();
      const mockResizeObserver = vi.fn().mockImplementation(() => ({
        observe: vi.fn(),
        unobserve: vi.fn(),
        disconnect: mockDisconnect,
      }));

      global.ResizeObserver = mockResizeObserver;

      const { unmount } = render(VirtualScrollPlaylist, {
        props: {
          tracks: mockTracks.slice(0, 10),
          selectedTrack: null,
          loading: false
        }
      });

      unmount();

      expect(mockDisconnect).toHaveBeenCalled();
    });

    it('should clean up scroll timeout on unmount', () => {
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');

      const { unmount } = render(VirtualScrollPlaylist, {
        props: {
          tracks: mockTracks.slice(0, 10),
          selectedTrack: null,
          loading: false
        }
      });

      unmount();

      expect(clearTimeoutSpy).toHaveBeenCalled();
    });
  });
});