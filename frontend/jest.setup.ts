import "@testing-library/jest-dom";

// Mock fetch globally for API tests
global.fetch = jest.fn();

// Mock Response for API tests
global.Response = class Response {
  ok: boolean;
  status: number;
  headers: Headers;
  body: ReadableStream | null;
  bodyUsed: boolean;

  constructor(body?: BodyInit | null, init?: ResponseInit) {
    this.body = body as ReadableStream | null;
    this.bodyUsed = false;
    this.ok = init?.status ? init.status >= 200 && init.status < 300 : true;
    this.status = init?.status || 200;
    this.headers = new Headers(init?.headers);
  }

  async json() {
    if (!this.body) return {};
    const text = await this.text();
    return JSON.parse(text);
  }

  async text() {
    if (!this.body) return '';
    if (typeof this.body === 'string') return this.body;
    return '';
  }
} as any;
