import { describe, it, expect } from 'vitest';
import { nodes, getNodes } from '@/_lib/relayHelpers';

describe('Relay Helper Functions', () => {
  describe('nodes', () => {
    it('returns an empty array when connection is null', () => {
      const result = nodes(null);
      expect(result).toEqual([]);
    });

    it('returns an empty array when edges are undefined', () => {
      const result = nodes({ edges: undefined });
      expect(result).toEqual([]);
    });

    it('returns an array of nodes when edges are present', () => {
      const mockData = {
        edges: [
          { node: { id: '1', name: 'Node 1' } },
          { node: { id: '2', name: 'Node 2' } },
        ],
      };
      const result = nodes(mockData);
      expect(result).toEqual([
        { id: '1', name: 'Node 1' },
        { id: '2', name: 'Node 2' },
      ]);
    });

    it('handles an empty edges array gracefully', () => {
      const mockData = { edges: [] };
      const result = nodes(mockData);
      expect(result).toEqual([]);
    });
  });

  describe('getNodes', () => {
    it('returns an empty array when connection is null', () => {
      const result = getNodes(null);
      expect(result).toEqual([]);
    });

    it('returns an empty array when edges are undefined', () => {
      const result = getNodes({ edges: undefined });
      expect(result).toEqual([]);
    });

    it('filters out null or undefined nodes', () => {
      const mockData = {
        edges: [
          { node: { id: '1', name: 'Node 1' } },
          { node: null },
          { node: { id: '3', name: 'Node 3' } },
          null,
          undefined,
        ],
      };
      const result = getNodes(mockData);
      expect(result).toEqual([
        { id: '1', name: 'Node 1' },
        { id: '3', name: 'Node 3' },
      ]);
    });

    it('returns an array of nodes when edges are present', () => {
      const mockData = {
        edges: [
          { node: { id: '1', name: 'Node 1' } },
          { node: { id: '2', name: 'Node 2' } },
        ],
      };
      const result = getNodes(mockData);
      expect(result).toEqual([
        { id: '1', name: 'Node 1' },
        { id: '2', name: 'Node 2' },
      ]);
    });

    it('handles an empty edges array gracefully', () => {
      const mockData = { edges: [] };
      const result = getNodes(mockData);
      expect(result).toEqual([]);
    });

    it('handles deeply nested structures with null values', () => {
      const mockData = {
        edges: [
          { node: { id: '1', name: 'Node 1', details: { key: 'value' } } },
          { node: { id: '2', name: null, details: null } },
          { node: null },
        ],
      };
      const result = getNodes(mockData as any);
      expect(result).toEqual([
        { id: '1', name: 'Node 1', details: { key: 'value' } },
        { id: '2', name: null, details: null },
      ]);
    });
  });
});
