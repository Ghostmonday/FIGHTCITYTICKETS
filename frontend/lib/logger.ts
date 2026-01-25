/**
 * Client-side logging utility for Fight City Tickets
 *
 * Replaces console.log/error/warn with structured logging that can be
 * configured based on environment.
 */

// Log levels
export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'none';

interface LogMessage {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: unknown;
}

// Get log level from environment or default to 'info' in development
const getLogLevel = (): LogLevel => {
  if (typeof window !== 'undefined') {
    // Client-side: check localStorage or default
    const stored = localStorage.getItem('LOG_LEVEL');
    if (stored && ['debug', 'info', 'warn', 'error', 'none'].includes(stored)) {
      return stored as LogLevel;
    }
    // Default to 'warn' in production, 'info' in development
    return process.env.NODE_ENV === 'production' ? 'warn' : 'info';
  }
  return 'info';
};

const currentLevel = getLogLevel();

const shouldLog = (level: LogLevel): boolean => {
  const levels: LogLevel[] = ['debug', 'info', 'warn', 'error', 'none'];
  const currentIndex = levels.indexOf(currentLevel);
  const levelIndex = levels.indexOf(level);
  return levelIndex <= currentIndex;
};

// Format log message
const formatMessage = (message: string, data?: unknown): LogMessage => ({
  level: 'info',
  message,
  timestamp: new Date().toISOString(),
  data,
});

// Log functions
export const log = {
  debug: (message: string, data?: unknown) => {
    if (shouldLog('debug')) {
      console.debug(`[DEBUG] ${message}`, data ?? '');
    }
  },
  info: (message: string, data?: unknown) => {
    if (shouldLog('info')) {
      console.info(`[INFO] ${message}`, data ?? '');
    }
  },
  warn: (message: string, data?: unknown) => {
    if (shouldLog('warn')) {
      console.warn(`[WARN] ${message}`, data ?? '');
    }
  },
  error: (message: string, data?: unknown) => {
    if (shouldLog('error')) {
      console.error(`[ERROR] ${message}`, data ?? '');
      // In production, you could send to error tracking service here
    }
  },
};

// Convenience methods
export const debug = log.debug;
export const info = log.info;
export const warn = log.warn;
export const error = log.error;

// Helper for debugging API responses
export const logApiRequest = (
  method: string,
  url: string,
  status?: number,
  duration?: number
) => {
  const message = `${method} ${url} ${status ? `(${status})` : ''} ${duration ? `[${duration}ms]` : ''}`;
  if (status && status >= 400) {
    log.error(message);
  } else if (status && status >= 200 && status < 300) {
    log.debug(message);
  } else {
    log.info(message);
  }
};

// Suppress console in tests (mock helper)
export const suppressConsole = () => {
  if (typeof jest !== 'undefined') {
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalLog = console.log;

    console.error = jest.fn();
    console.warn = jest.fn();
    console.log = jest.fn();

    return () => {
      console.error = originalError;
      console.warn = originalWarn;
      console.log = originalLog;
    };
  }
  return () => {};
};
