/**
 * Structured JSON logger for the restaurant-voice-hub frontend.
 * Replaces ad-hoc console.log calls with typed, searchable log lines.
 */

type LogLevel = 'INFO' | 'WARN' | 'ERROR';

interface LogRecord {
  ts: string;
  level: LogLevel;
  event: string;
  [key: string]: unknown;
}

function emit(level: LogLevel, event: string, fields: Record<string, unknown> = {}): void {
  const record: LogRecord = {
    ts: new Date().toISOString(),
    level,
    event,
    ...fields,
  };
  // In production, send to a logging endpoint; for now output structured JSON
  console.log(JSON.stringify(record));
}

export const log = {
  info: (event: string, fields?: Record<string, unknown>) => emit('INFO', event, fields),
  warn: (event: string, fields?: Record<string, unknown>) => emit('WARN', event, fields),
  error: (event: string, fields?: Record<string, unknown>) => emit('ERROR', event, fields),
};
