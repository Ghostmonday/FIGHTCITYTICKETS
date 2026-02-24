import OcrHelper from './ocr-helper';
import { createWorker } from 'tesseract.js';

// Mock tesseract.js
jest.mock('tesseract.js', () => ({
  createWorker: jest.fn(),
}));

describe('OcrHelper', () => {
  let helper: OcrHelper;
  const mockCreateWorker = createWorker as jest.Mock;

  // Mock Worker instance methods
  const mockWorker = {
    setParameters: jest.fn().mockResolvedValue(undefined),
    recognize: jest.fn().mockResolvedValue({ data: { text: 'test' } }),
    terminate: jest.fn().mockResolvedValue(undefined),
  };

  // Canvas mocks
  let mockContext: any;
  let mockCanvas: any;

  // Save originals
  const originalImage = global.Image;
  const originalCreateElement = document.createElement.bind(document);

  beforeAll(() => {
    // Mock Image
    // @ts-ignore
    global.Image = class {
      onload: () => void = () => {};
      onerror: (err: any) => void = () => {};
      src: string = '';
      width: number = 100;
      height: number = 100;

      constructor() {
        setTimeout(() => this.onload(), 10); // Simulate async load
      }
    };
  });

  afterAll(() => {
    global.Image = originalImage;
  });

  beforeEach(() => {
    jest.clearAllMocks();
    helper = new OcrHelper();

    // Reset worker mock
    mockCreateWorker.mockResolvedValue(mockWorker);

    // Mock Canvas and Context
    mockContext = {
      drawImage: jest.fn(),
      getImageData: jest.fn().mockReturnValue({
        data: new Uint8ClampedArray(400), // 10x10 image * 4 channels
        width: 10,
        height: 10,
      }),
      putImageData: jest.fn(),
    };

    mockCanvas = {
      getContext: jest.fn().mockReturnValue(mockContext),
      toDataURL: jest.fn().mockReturnValue('data:image/png;base64,processed'),
      width: 0,
      height: 0,
    };

    jest.spyOn(document, 'createElement').mockImplementation((tagName: string, options?: ElementCreationOptions) => {
      if (tagName === 'canvas') {
        return mockCanvas;
      }
      return originalCreateElement(tagName, options);
    });
  });

  describe('extractCitationNumber', () => {
    it('should extract SF citation number (format: A12345678)', () => {
      const result = helper.extractCitationNumber('Ticket # A12345678');
      expect(result.number).toBe('A12345678');
      expect(result.confidence).toBe(0.7);
    });

    it('should extract SF citation number (format: AB12345678)', () => {
      const result = helper.extractCitationNumber('Ref: AB12345678');
      expect(result.number).toBe('AB12345678');
      expect(result.confidence).toBe(0.7);
    });

    it('should extract LA citation number (format: A1234567)', () => {
      const result = helper.extractCitationNumber('Citation A1234567');
      expect(result.number).toBe('A1234567');
      expect(result.confidence).toBe(0.7);
    });

    it('should extract NYC citation number (format: 1234567890)', () => {
      const result = helper.extractCitationNumber('1234567890');
      expect(result.number).toBe('1234567890');
      expect(result.confidence).toBe(0.7);
    });

    it('should fallback to generic numeric match if pattern not found', () => {
      const result = helper.extractCitationNumber('Ticket # 9876543');
      expect(result.number).toBe('9876543');
      expect(result.confidence).toBe(0.5);
    });

    it('should return null if no citation number found', () => {
      const result = helper.extractCitationNumber('Just some text without numbers');
      expect(result.number).toBeNull();
      expect(result.confidence).toBe(0);
    });

    it('should handle noisy text', () => {
      const result = helper.extractCitationNumber('... !! A 12345678 ...');
      expect(result.number).toBe('A12345678');
    });
  });

  describe('initialize', () => {
    it('should initialize worker with correct parameters', async () => {
      await helper.initialize();

      expect(mockCreateWorker).toHaveBeenCalledWith('eng', 1, expect.any(Object));
      expect(mockWorker.setParameters).toHaveBeenCalledWith({
        tessedit_char_whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -',
      });
    });

    it('should only initialize once', async () => {
      await helper.initialize();
      await helper.initialize();

      expect(mockCreateWorker).toHaveBeenCalledTimes(1);
    });

    it('should handle race conditions during initialization', async () => {
      mockCreateWorker.mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 50));
        return mockWorker;
      });

      const p1 = helper.initialize();
      const p2 = helper.initialize();

      await Promise.all([p1, p2]);

      expect(mockCreateWorker).toHaveBeenCalledTimes(1);
    });
  });

  describe('extractTextFromImage', () => {
    it('should process image and return extraction result', async () => {
      mockWorker.recognize.mockResolvedValue({
        data: { text: 'Citation # A12345678' }
      });

      const result = await helper.extractTextFromImage('data:image/jpeg;base64,raw');

      // Verify preprocessing
      expect(mockCanvas.getContext).toHaveBeenCalledWith('2d');
      expect(mockContext.drawImage).toHaveBeenCalled();
      expect(mockContext.getImageData).toHaveBeenCalled();
      expect(mockContext.putImageData).toHaveBeenCalled();

      // Verify recognition
      expect(mockWorker.recognize).toHaveBeenCalledWith('data:image/png;base64,processed');

      // Verify result
      expect(result.citationNumber).toBe('A12345678');
      expect(result.rawText).toBe('Citation # A12345678');
      expect(result.confidence).toBe(0.7);
    });

    it('should use city-specific config for preprocessing', async () => {
      mockWorker.recognize.mockResolvedValue({ data: { text: 'test' } });

      // SF config: scale 2
      await helper.extractTextFromImage('img', 'sf');

      // Check if canvas was scaled (100 * 2 = 200)
      // Note: Implementation sets canvas.width/height directly
      expect(mockCanvas.width).toBe(200);
      expect(mockCanvas.height).toBe(200);
    });

    it('should use default config for unknown city', async () => {
      mockWorker.recognize.mockResolvedValue({ data: { text: 'test' } });

      // Default config: scale 1.5
      await helper.extractTextFromImage('img', 'unknown');

      // Check if canvas was scaled (100 * 1.5 = 150)
      expect(mockCanvas.width).toBe(150);
      expect(mockCanvas.height).toBe(150);
    });

    it('should handle initialization failure', async () => {
      mockCreateWorker.mockRejectedValue(new Error('Init failed'));

      const result = await helper.extractTextFromImage('img');

      expect(result.confidence).toBe(0);
      expect(result.rawText).toBe('');
    });

    it('should handle recognition failure', async () => {
      mockWorker.recognize.mockRejectedValue(new Error('OCR failed'));

      const result = await helper.extractTextFromImage('img');

      expect(result.confidence).toBe(0);
      expect(result.rawText).toBe('');
    });
  });

  describe('terminate', () => {
    it('should terminate worker and reset state', async () => {
      await helper.initialize();
      await helper.terminate();

      expect(mockWorker.terminate).toHaveBeenCalled();

      // Re-initialize should create new worker
      await helper.initialize();
      expect(mockCreateWorker).toHaveBeenCalledTimes(2);
    });

    it('should do nothing if worker is not initialized', async () => {
      await helper.terminate();
      expect(mockWorker.terminate).not.toHaveBeenCalled();
    });
  });
});
