import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { createServer } from 'http';
import { 
  initializeWebSocket, 
  getWebSocketServer,
  broadcastNurseCreated,
  broadcastNurseUpdated,
  broadcastNurseDeleted,
  broadcastScheduleCreated,
  broadcastScheduleUpdated,
  broadcastScheduleDeleted
} from '../websocket';

describe('WebSocket Server', () => {
  let httpServer: ReturnType<typeof createServer>;

  beforeEach(() => {
    httpServer = createServer();
  });

  afterEach(async () => {
    const io = getWebSocketServer();
    if (io) {
      await new Promise<void>((resolve) => {
        io.close(() => {
          httpServer.close(() => {
            resolve();
          });
        });
      });
    } else {
      await new Promise<void>((resolve) => {
        httpServer.close(() => {
          resolve();
        });
      });
    }
  });

  it('should initialize WebSocket server', () => {
    const io = initializeWebSocket(httpServer);
    
    expect(io).toBeDefined();
    expect(io.path()).toBe('/api/socket.io');
  });

  it('should return the same instance on multiple calls', () => {
    const io1 = initializeWebSocket(httpServer);
    const io2 = getWebSocketServer();
    
    expect(io1).toBe(io2);
  });

  it('should have broadcast functions defined', () => {
    expect(typeof broadcastNurseCreated).toBe('function');
    expect(typeof broadcastNurseUpdated).toBe('function');
    expect(typeof broadcastNurseDeleted).toBe('function');
    expect(typeof broadcastScheduleCreated).toBe('function');
    expect(typeof broadcastScheduleUpdated).toBe('function');
    expect(typeof broadcastScheduleDeleted).toBe('function');
  });

  it('should broadcast nurse events without errors', () => {
    initializeWebSocket(httpServer);
    
    const mockNurse = {
      id: 'N001',
      name: 'Test Nurse',
      skill_level: 'SENIOR',
      max_hours_per_week: 40
    };

    expect(() => broadcastNurseCreated(mockNurse)).not.toThrow();
    expect(() => broadcastNurseUpdated(mockNurse)).not.toThrow();
    expect(() => broadcastNurseDeleted('N001')).not.toThrow();
  });

  it('should broadcast schedule events without errors', () => {
    initializeWebSocket(httpServer);
    
    const mockSchedule = {
      id: 'S001',
      name: 'Test Schedule',
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      department: 'ICU',
      status: 'active' as const,
      created_at: new Date().toISOString()
    };

    expect(() => broadcastScheduleCreated(mockSchedule)).not.toThrow();
    expect(() => broadcastScheduleUpdated(mockSchedule)).not.toThrow();
    expect(() => broadcastScheduleDeleted('S001')).not.toThrow();
  });
});
