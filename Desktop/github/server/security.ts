import rateLimit from "express-rate-limit";
import type { Request, Response, NextFunction } from "express";

// Enhanced security configurations for production

// Strict rate limiting for sensitive operations
export const strictLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 3, // 3 attempts per window
  message: { error: "Too many attempts, please try again later." },
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: true
});

// Input sanitization for production
export const sanitizeInput = (req: Request, res: Response, next: NextFunction) => {
  const sanitizeString = (str: string): string => {
    return str
      .trim()
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .replace(/data:text\/html/gi, '')
      .substring(0, 10000); // Limit input length
  };

  const sanitizeObject = (obj: any): any => {
    if (typeof obj === 'string') {
      return sanitizeString(obj);
    }
    if (typeof obj === 'object' && obj !== null && !Array.isArray(obj)) {
      const sanitized: any = {};
      for (const [key, value] of Object.entries(obj)) {
        if (key.length <= 100) { // Limit key length
          sanitized[key] = sanitizeObject(value);
        }
      }
      return sanitized;
    }
    if (Array.isArray(obj)) {
      return obj.slice(0, 1000).map(sanitizeObject); // Limit array size
    }
    return obj;
  };

  if (req.body) {
    req.body = sanitizeObject(req.body);
  }
  next();
};

// Security headers middleware
export const securityHeaders = (req: Request, res: Response, next: NextFunction) => {
  // Prevent clickjacking
  res.setHeader('X-Frame-Options', 'DENY');
  
  // Prevent MIME type sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');
  
  // Enable XSS protection
  res.setHeader('X-XSS-Protection', '1; mode=block');
  
  // Strict transport security
  if (process.env.NODE_ENV === 'production') {
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  }
  
  // Referrer policy
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  next();
};

// Request size and validation middleware
export const validateRequestSize = (req: Request, res: Response, next: NextFunction) => {
  const contentLength = parseInt(req.get('content-length') || '0', 10);
  
  if (contentLength > 10 * 1024 * 1024) { // 10MB limit
    return res.status(413).json({ error: 'Request entity too large' });
  }
  
  next();
};

// IP monitoring and blocking for suspicious activity
const suspiciousIPs = new Map<string, { attempts: number; lastAttempt: number }>();

export const monitorSuspiciousActivity = (req: Request, res: Response, next: NextFunction) => {
  // Skip monitoring in development mode
  if (process.env.NODE_ENV === 'development') {
    return next();
  }
  
  const clientIP = req.ip || req.connection.remoteAddress || 'unknown';
  const now = Date.now();
  
  // Clean old entries (older than 1 hour)
  Array.from(suspiciousIPs.entries()).forEach(([ip, data]) => {
    if (now - data.lastAttempt > 3600000) {
      suspiciousIPs.delete(ip);
    }
  });
  
  const ipData = suspiciousIPs.get(clientIP) || { attempts: 0, lastAttempt: 0 };
  
  // Reset attempts if last attempt was more than 15 minutes ago
  if (now - ipData.lastAttempt > 900000) {
    ipData.attempts = 0;
  }
  
  // Block if too many attempts (only in production)
  if (ipData.attempts > 100) {
    console.error(`[Security Alert] Blocked suspicious IP: ${clientIP}`);
    return res.status(429).json({ error: 'Access temporarily blocked due to suspicious activity' });
  }
  
  // Track this request
  ipData.attempts++;
  ipData.lastAttempt = now;
  suspiciousIPs.set(clientIP, ipData);
  
  next();
};

// Database query timeout middleware
export const queryTimeout = (timeoutMs: number = 30000) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const timeout = setTimeout(() => {
      if (!res.headersSent) {
        res.status(408).json({ error: 'Request timeout' });
      }
    }, timeoutMs);
    
    res.on('finish', () => clearTimeout(timeout));
    res.on('close', () => clearTimeout(timeout));
    
    next();
  };
};