/**
 * Device detection utilities for WhatsApp redirection
 */

export const isMobileDevice = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
  
  // Check for mobile patterns
  const mobileRegex = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i;
  
  // Check for touch capability and screen size
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  const isSmallScreen = window.innerWidth <= 768;
  
  return mobileRegex.test(userAgent) || (isTouchDevice && isSmallScreen);
};

export const isAndroidDevice = (): boolean => {
  if (typeof window === 'undefined') return false;
  return /android/i.test(navigator.userAgent);
};

export const isIOSDevice = (): boolean => {
  if (typeof window === 'undefined') return false;
  return /iPad|iPhone|iPod/.test(navigator.userAgent);
};

export const generateWhatsAppUrl = (phone: string, message: string): string => {
  const cleanPhone = phone.replace(/\D/g, '');
  const encodedMessage = encodeURIComponent(message);
  
  // wa.me is the most universal option - works on all devices
  // It automatically chooses the best available option:
  // - Mobile with app: opens native WhatsApp
  // - Mobile without app: opens web version
  // - Desktop: opens web.whatsapp.com
  return `https://wa.me/${cleanPhone}?text=${encodedMessage}`;
};

export const openWhatsApp = (phone: string, message: string): void => {
  const cleanPhone = phone.replace(/\D/g, '');
  const encodedMessage = encodeURIComponent(message);
  
  // Detect device type for optimal URL selection
  const isMobile = isMobileDevice();
  const isIOS = isIOSDevice();
  const isAndroid = isAndroidDevice();
  
  let primaryUrl = '';
  let fallbackUrls = [];
  
  if (isIOS) {
    // iOS: Try native app first, then web
    primaryUrl = `whatsapp://send?phone=${cleanPhone}&text=${encodedMessage}`;
    fallbackUrls = [
      `https://wa.me/${cleanPhone}?text=${encodedMessage}`,
      `https://web.whatsapp.com/send?phone=${cleanPhone}&text=${encodedMessage}`
    ];
  } else if (isAndroid) {
    // Android: Try intent first, then wa.me, then web
    primaryUrl = `intent://send?phone=${cleanPhone}&text=${encodedMessage}#Intent;scheme=whatsapp;package=com.whatsapp;end`;
    fallbackUrls = [
      `https://wa.me/${cleanPhone}?text=${encodedMessage}`,
      `https://web.whatsapp.com/send?phone=${cleanPhone}&text=${encodedMessage}`
    ];
  } else {
    // Desktop: Try web.whatsapp.com first as it's more reliable on desktop
    primaryUrl = `https://web.whatsapp.com/send?phone=${cleanPhone}&text=${encodedMessage}`;
    fallbackUrls = [
      `https://wa.me/${cleanPhone}?text=${encodedMessage}`,
      `https://api.whatsapp.com/send?phone=${cleanPhone}&text=${encodedMessage}`
    ];
  }
  
  // Try primary URL first
  try {
    if (isMobile && (isIOS || isAndroid)) {
      // For mobile, open in same window to trigger app
      window.location.href = primaryUrl;
      
      // If app doesn't open in 2 seconds, try fallback
      setTimeout(() => {
        if (document.visibilityState === 'visible') {
          // App didn't open, try fallback
          window.open(fallbackUrls[0], '_blank');
        }
      }, 2000);
    } else {
      // For desktop, open in new tab
      const newWindow = window.open(primaryUrl, '_blank', 'noopener,noreferrer');
      if (!newWindow) {
        // Popup blocked, try location change
        window.location.href = primaryUrl;
      }
    }
  } catch (error) {
    console.warn('Primary WhatsApp method failed, trying fallbacks:', error);
    
    // Try fallback URLs
    for (const url of fallbackUrls) {
      try {
        const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
        if (newWindow) break;
        
        // If popup blocked, try location change for last fallback
        if (url === fallbackUrls[fallbackUrls.length - 1]) {
          window.location.href = url;
        }
      } catch (fallbackError) {
        console.warn('Fallback failed:', fallbackError);
      }
    }
  }
};