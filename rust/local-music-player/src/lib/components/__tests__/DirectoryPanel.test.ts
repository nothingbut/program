import { describe, it, expect } from 'vitest';
import type { Directory } from '../../types';

describe('DirectoryPanel Component Logic', () => {
  const mockDirectories: Directory[] = [
    {
      id: '1',
      path: '/home/user/Music',
      name: 'Music',
      addedAt: '2024-01-01T00:00:00Z'
    },
    {
      id: '2',
      path: '/home/user/Downloads/Songs',
      name: 'Songs',
      addedAt: '2024-01-02T00:00:00Z'
    }
  ];

  describe('Component Props and Types', () => {
    it('should have correct directory structure', () => {
      const directory = mockDirectories[0];
      expect(directory).toHaveProperty('id');
      expect(directory).toHaveProperty('path');
      expect(directory).toHaveProperty('name');
      expect(directory).toHaveProperty('addedAt');
      expect(typeof directory.id).toBe('string');
      expect(typeof directory.path).toBe('string');
      expect(typeof directory.name).toBe('string');
      expect(typeof directory.addedAt).toBe('string');
    });

    it('should validate directory data types', () => {
      mockDirectories.forEach(directory => {
        expect(directory.id).toBeTruthy();
        expect(directory.path).toBeTruthy();
        expect(directory.name).toBeTruthy();
        expect(directory.addedAt).toBeTruthy();
      });
    });
  });

  describe('Display Name Logic', () => {
    it('should use directory name when available', () => {
      const directory = mockDirectories[0];
      const displayName = directory.name || directory.path.split('/').pop() || directory.path;
      expect(displayName).toBe('Music');
    });

    it('should fallback to last path segment when name is empty', () => {
      const directory = {
        id: '1',
        path: '/home/user/Music',
        name: '',
        addedAt: '2024-01-01T00:00:00Z'
      };
      const displayName = directory.name || directory.path.split('/').pop() || directory.path;
      expect(displayName).toBe('Music');
    });

    it('should fallback to full path when path has no segments', () => {
      const directory = {
        id: '1',
        path: '/',
        name: '',
        addedAt: '2024-01-01T00:00:00Z'
      };
      const displayName = directory.name || directory.path.split('/').pop() || directory.path;
      expect(displayName).toBe('/');
    });
  });
});