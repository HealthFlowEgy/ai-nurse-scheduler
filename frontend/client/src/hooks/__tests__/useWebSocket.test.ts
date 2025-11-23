import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useWebSocket } from '../useWebSocket';
import { io } from 'socket.io-client';

// Mock socket.io-client
vi.mock('socket.io-client', () => ({
  io: vi.fn(() => ({
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn(),
    close: vi.fn(),
    connected: true,
  })),
}));

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize socket connection', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(io).toHaveBeenCalledWith({
      path: '/api/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    expect(result.current.socket).toBeDefined();
  });

  it('should provide emit function', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.emit).toBeDefined();
    expect(typeof result.current.emit).toBe('function');
  });

  it('should provide on function', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.on).toBeDefined();
    expect(typeof result.current.on).toBe('function');
  });

  it('should provide off function', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.off).toBeDefined();
    expect(typeof result.current.off).toBe('function');
  });

  it('should track connection status', async () => {
    const { result } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(result.current.status).toBeDefined();
      expect(typeof result.current.isConnected).toBe('boolean');
    });
  });
});
