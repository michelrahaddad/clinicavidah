import type { Request, Response } from "express";
import { storage } from "../storage";
import { whatsappConversionSchema } from "@shared/validation";
import { ApiResponse, WhatsAppConversion } from "@shared/types";
import { HTTP_STATUS } from "@shared/constants";
import { WhatsAppService } from "../services/whatsappService";
import { z } from "zod";

export class WhatsAppController {
  static async createConversion(req: Request, res: Response) {
    try {
      const validatedData = whatsappConversionSchema.parse(req.body);
      
      // Add request metadata
      const conversionData: WhatsAppConversion = {
        ...validatedData,
        ipAddress: req.ip || req.connection.remoteAddress,
        userAgent: req.get('User-Agent') || 'Unknown',
      };

      const conversion = await WhatsAppService.createConversion(conversionData);
      
      // Generate WhatsApp URL based on button type and device
      const userAgent = req.get('User-Agent') || '';
      const whatsappUrl = WhatsAppService.generateWhatsAppUrl(conversion, userAgent);
      
      const response: ApiResponse = {
        success: true,
        data: {
          conversion,
          whatsappUrl
        }
      };
      
      res.json(response);
    } catch (error) {
      console.error("[WhatsAppController] Error creating conversion:", error);
      
      if (error instanceof z.ZodError) {
        const response: ApiResponse = {
          success: false,
          error: "Dados inválidos fornecidos",
          message: error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')
        };
        return res.status(HTTP_STATUS.BAD_REQUEST).json(response);
      }

      const response: ApiResponse = {
        success: false,
        error: "Erro ao processar solicitação"
      };
      
      res.status(500).json(response);
    }
  }

  static async getConversions(req: Request, res: Response) {
    try {
      const { startDate, endDate, type } = req.query;
      
      let conversions;
      
      if (startDate && endDate) {
        conversions = await storage.getWhatsappConversionsByDateRange(
          new Date(startDate as string),
          new Date(endDate as string)
        );
      } else {
        conversions = await storage.getAllWhatsappConversions();
      }
      
      // Filter by type if provided
      if (type && typeof type === 'string') {
        conversions = conversions.filter(c => c.buttonType === type);
      }

      const response: ApiResponse = {
        success: true,
        data: conversions
      };
      
      res.json(response);
    } catch (error) {
      console.error("[WhatsAppController] Error fetching conversions:", error);
      
      const response: ApiResponse = {
        success: false,
        error: "Erro ao buscar conversões"
      };
      
      res.status(500).json(response);
    }
  }

  static async exportConversions(req: Request, res: Response) {
    try {
      const { format = 'csv', type = 'internal' } = req.query;
      
      const conversions = await storage.getAllWhatsappConversions();
      
      if (format === 'csv') {
        const csv = WhatsAppController.generateCSV(conversions as any[], type as string);
        
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', `attachment; filename="conversions-${Date.now()}.csv"`);
        res.send(csv);
      } else {
        const response: ApiResponse = {
          success: true,
          data: conversions
        };
        res.json(response);
      }
    } catch (error) {
      console.error("[WhatsAppController] Error exporting conversions:", error);
      
      const response: ApiResponse = {
        success: false,
        error: "Erro ao exportar conversões"
      };
      
      res.status(500).json(response);
    }
  }

  // Método removido - agora usa WhatsAppService.generateWhatsAppUrl

  private static generateCSV(conversions: WhatsAppConversion[], type: string): string {
    if (type === 'marketing') {
      // Format for marketing campaigns (Google Ads, Facebook Ads)
      const headers = 'Email,Phone,First_Name,Last_Name,Interest_Category,Campaign_Type,Date\n';
      const rows = conversions.map(c => {
        const nameParts = (c.name || '').split(' ');
        const firstName = nameParts[0] || '';
        const lastName = nameParts.slice(1).join(' ') || '';
        const phone = (c.phone || '').replace(/\D/g, '');
        const category = c.buttonType === 'plan_subscription' ? 'Health Plan' :
                        c.buttonType === 'doctor_appointment' ? 'Medical Consultation' :
                        'Enterprise Quote';
        
        return `"${c.email || ''}","${phone}","${firstName}","${lastName}","${category}","${c.buttonType}","${c.createdAt}"`;
      }).join('\n');
      
      return headers + rows;
    } else {
      // Internal management format
      const headers = 'ID,Nome,Email,Telefone,Tipo,Plano,Médico,IP,Data\n';
      const rows = conversions.map(c => 
        `${c.id},"${c.name || ''}","${c.email || ''}","${c.phone || ''}","${c.buttonType}","${c.planName || ''}","${c.doctorName || ''}","${c.ipAddress || ''}","${c.createdAt}"`
      ).join('\n');
      
      return headers + rows;
    }
  }
}