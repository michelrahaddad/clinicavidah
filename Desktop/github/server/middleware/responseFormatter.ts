import type { Request, Response, NextFunction } from "express";

/**
 * Middleware to ensure consistent response format for admin login
 */
export const formatAdminResponse = (req: Request, res: Response, next: NextFunction) => {
  if (req.path === '/api/admin/login' && req.method === 'POST') {
    const originalJson = res.json;
    
    res.json = function (data: any) {
      // If response is already in the nested format, extract the data
      if (data && data.success === true && data.data && data.data.token) {
        const { token, admin } = data.data;
        return originalJson.call(this, {
          token,
          user: {
            id: admin.id,
            username: admin.username,
            email: admin.email
          }
        });
      }
      
      // Otherwise return as is
      return originalJson.call(this, data);
    };
  }
  
  next();
};