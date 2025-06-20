// Frontend security utilities for production

// Input sanitization for user data
export const sanitizeInput = (input: string): string => {
  return input
    .trim()
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/data:text\/html/gi, '')
    .substring(0, 1000); // Limit input length
};

// Validate email format with enhanced security
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email) && email.length <= 100;
};

// Validate phone number format
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^[\d\s\-\+\(\)]{10,20}$/;
  return phoneRegex.test(phone);
};

// Validate name format (letters and spaces only)
export const isValidName = (name: string): boolean => {
  const nameRegex = /^[a-zA-ZÀ-ÿ\s]{2,100}$/;
  return nameRegex.test(name);
};

// Rate limiting for frontend requests
class RateLimit {
  private requests: Map<string, number[]> = new Map();
  private readonly windowMs: number;
  private readonly maxRequests: number;

  constructor(windowMs: number = 60000, maxRequests: number = 10) {
    this.windowMs = windowMs;
    this.maxRequests = maxRequests;
  }

  isAllowed(key: string): boolean {
    const now = Date.now();
    const requests = this.requests.get(key) || [];
    
    // Remove old requests outside the window
    const validRequests = requests.filter(time => now - time < this.windowMs);
    
    if (validRequests.length >= this.maxRequests) {
      return false;
    }
    
    validRequests.push(now);
    this.requests.set(key, validRequests);
    return true;
  }
}

export const formSubmissionRateLimit = new RateLimit(60000, 5); // 5 submissions per minute

// Secure API request wrapper with enhanced error handling
export const secureApiRequest = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  // Rate limiting check
  const clientId = `${navigator.userAgent}_${window.location.hostname}`;
  if (!formSubmissionRateLimit.isAllowed(clientId)) {
    throw new Error('Too many requests. Please wait before trying again.');
  }

  // Add security headers
  const secureOptions: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...options.headers,
    },
  };

  // Add timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

  try {
    const response = await fetch(url, {
      ...secureOptions,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Network error' }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}`);
    }

    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout. Please try again.');
      }
      throw error;
    }
    
    throw new Error('An unexpected error occurred');
  }
};

// Content Security Policy validation
export const validateCSP = (): boolean => {
  // Check if CSP is properly implemented
  const metaCSP = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
  return metaCSP !== null;
};

// Detect and prevent basic XSS attempts
export const detectXSS = (input: string): boolean => {
  const xssPatterns = [
    /<script[^>]*>.*?<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe[^>]*>.*?<\/iframe>/gi,
    /<object[^>]*>.*?<\/object>/gi,
    /<embed[^>]*>/gi,
  ];

  return xssPatterns.some(pattern => pattern.test(input));
};

// Secure localStorage wrapper
export const secureStorage = {
  set: (key: string, value: any): void => {
    try {
      const sanitizedKey = sanitizeInput(key);
      const serializedValue = JSON.stringify(value);
      localStorage.setItem(sanitizedKey, serializedValue);
    } catch (error) {
      console.error('Failed to store data securely:', error);
    }
  },

  get: (key: string): any => {
    try {
      const sanitizedKey = sanitizeInput(key);
      const item = localStorage.getItem(sanitizedKey);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Failed to retrieve data securely:', error);
      return null;
    }
  },

  remove: (key: string): void => {
    try {
      const sanitizedKey = sanitizeInput(key);
      localStorage.removeItem(sanitizedKey);
    } catch (error) {
      console.error('Failed to remove data securely:', error);
    }
  },

  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear storage securely:', error);
    }
  }
};

// Form validation with security checks
export const validateFormData = (data: Record<string, any>): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  // Check for XSS attempts in all string fields
  Object.entries(data).forEach(([key, value]) => {
    if (typeof value === 'string') {
      if (detectXSS(value)) {
        errors.push(`Invalid content detected in ${key}`);
      }
      if (value.length > 1000) {
        errors.push(`${key} is too long`);
      }
    }
  });

  // Validate specific fields
  if (data.email && !isValidEmail(data.email)) {
    errors.push('Invalid email format');
  }

  if (data.phone && !isValidPhone(data.phone)) {
    errors.push('Invalid phone format');
  }

  if (data.name && !isValidName(data.name)) {
    errors.push('Invalid name format');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};