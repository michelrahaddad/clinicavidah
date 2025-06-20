import { WhatsAppConversion } from "@shared/types";
import { InsertWhatsappConversion } from "@shared/schema";
import { WHATSAPP_CONFIG } from "@shared/constants";
import { storage } from "../storage";

/**
 * Service class for handling WhatsApp conversion logic
 */
export class WhatsAppService {
  
  /**
   * Creates a new WhatsApp conversion record
   */
  static async createConversion(data: InsertWhatsappConversion) {
    return await storage.createWhatsappConversion(data);
  }

  /**
   * Generates WhatsApp URL with appropriate message template and device detection
   */
  static generateWhatsAppUrl(conversion: any, userAgent?: string): string {
    const { name = '', phone = '', email = '', planName = '', doctorName = '' } = conversion;
    
    let message = '';
    
    switch (conversion.buttonType) {
      case 'plan_subscription':
        message = WHATSAPP_CONFIG.MESSAGE_TEMPLATES.PLAN_SUBSCRIPTION(name, phone, email, planName);
        break;
      case 'doctor_appointment':
        message = WHATSAPP_CONFIG.MESSAGE_TEMPLATES.DOCTOR_APPOINTMENT(name, phone, email, doctorName);
        break;
      case 'enterprise_quote':
        message = WHATSAPP_CONFIG.MESSAGE_TEMPLATES.ENTERPRISE_QUOTE(name, phone, email);
        break;
      default:
        throw new Error(`Invalid button type: ${conversion.buttonType}`);
    }
    
    const encodedMessage = encodeURIComponent(message);
    
    // Detect device type from user agent for optimal URL
    const isMobile = userAgent ? 
      /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile|phone/i.test(userAgent) : false;
    
    if (isMobile) {
      // For mobile: use wa.me (more reliable than web version)
      return `https://wa.me/${WHATSAPP_CONFIG.DEFAULT_PHONE}?text=${encodedMessage}`;
    } else {
      // For desktop: use web.whatsapp.com (more reliable on desktop)
      return `https://web.whatsapp.com/send?phone=${WHATSAPP_CONFIG.DEFAULT_PHONE}&text=${encodedMessage}`;
    }
  }

  /**
   * Gets conversions by date range
   */
  static async getConversionsByDateRange(startDate: Date, endDate: Date) {
    return await storage.getWhatsappConversionsByDateRange(startDate, endDate);
  }

  /**
   * Gets all conversions
   */
  static async getAllConversions() {
    return await storage.getAllWhatsappConversions();
  }
}