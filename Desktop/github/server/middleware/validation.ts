import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { HTTP_STATUS } from '@shared/constants';

/**
 * Middleware to handle validation errors from express-validator
 */
export const validateRequest = (req: Request, res: Response, next: NextFunction) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    return res.status(HTTP_STATUS.BAD_REQUEST).json({
      success: false,
      error: 'Dados de entrada inválidos',
      details: errors.array().map(error => ({
        field: 'location' in error ? error.path : 'unknown',
        message: error.msg,
        value: 'value' in error ? error.value : undefined
      }))
    });
  }
  
  next();
};

/**
 * Middleware to sanitize request body
 */
export const sanitizeRequest = (req: Request, res: Response, next: NextFunction) => {
  if (req.body && typeof req.body === 'object') {
    req.body = sanitizeObject(req.body);
  }
  next();
};

/**
 * Recursively sanitize an object
 */
function sanitizeObject(obj: any): any {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }
  
  const sanitized: any = {};
  
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key] = value
        .replace(/[<>]/g, '') // Remove potential XSS chars
        .replace(/[{}]/g, '') // Remove object injection chars
        .trim();
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeObject(value);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
}