export interface TrackingData {
  buttonType: 'plan_subscription' | 'doctor_appointment' | 'enterprise_quote';
  planName?: string;
  doctorName?: string;
  name?: string;
  phone?: string;
}

export const trackWhatsAppConversion = async (data: TrackingData) => {
  try {
    await fetch(`${import.meta.env.VITE_API_URL}/track-whatsapp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  } catch (error) {
    console.error('Error tracking WhatsApp conversion:', error);
  }
};

export const generateWhatsAppLink = (phone: string, message: string, trackingData: TrackingData) => {
  // Track the conversion before redirecting
  trackWhatsAppConversion(trackingData);
  
  // Use device detection utility for URL generation
  const { generateWhatsAppUrl } = require('@/lib/device-detection');
  return generateWhatsAppUrl(phone, message);
};