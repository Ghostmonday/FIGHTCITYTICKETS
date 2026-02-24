import OcrHelper from './ocr-helper';
import { createWorker } from 'tesseract.js';

// Mock tesseract.js
jest.mock('tesseract.js', () => ({
  createWorker: jest.fn(),
}));

describe('OcrHelper Initialization Race Condition', () => {
  let ocrHelper: OcrHelper;
  const mockCreateWorker = createWorker as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    ocrHelper = new OcrHelper();

    // Mock createWorker implementation
    mockCreateWorker.mockImplementation(async () => {
      // Simulate some async work
      await new Promise((resolve) => setTimeout(resolve, 50));
      return {
        setParameters: jest.fn().mockResolvedValue(undefined),
        terminate: jest.fn().mockResolvedValue(undefined),
        recognize: jest.fn().mockResolvedValue({ data: { text: 'test' } }),
      };
    });
  });

  it('should initialize worker only once when called concurrently', async () => {
    // Call initialize twice concurrently
    const p1 = ocrHelper.initialize();
    const p2 = ocrHelper.initialize();

    await Promise.all([p1, p2]);

    // Expect createWorker to be called exactly once
    expect(mockCreateWorker).toHaveBeenCalledTimes(1);
  });
});
