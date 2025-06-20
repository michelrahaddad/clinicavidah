import { MessageCircle } from "lucide-react";
import { trackWhatsAppConversion } from "@/lib/whatsapp-tracking";
import { openWhatsApp } from "@/lib/device-detection";

export default function WhatsAppFloat() {
  const handleWhatsAppClick = () => {
    // Track general inquiry conversion
    trackWhatsAppConversion({
      buttonType: 'plan_subscription',
      planName: 'Consulta Geral'
    });

    const message = "Olá! Gostaria de saber mais sobre o Cartão + Vidah";
    openWhatsApp('5516993247676', message);
  };

  return (
    <div className="fixed bottom-6 right-6 z-40">
      <button
        onClick={handleWhatsAppClick}
        className="bg-green-500 hover:bg-green-600 text-white w-14 h-14 rounded-full flex items-center justify-center shadow-lg hover:shadow-xl transition-all animate-float group"
        aria-label="Falar no WhatsApp"
      >
        <MessageCircle size={28} className="group-hover:scale-110 transition-transform" />
      </button>
      
      {/* Tooltip */}
      <div className="absolute bottom-16 right-0 bg-black text-white text-sm px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap pointer-events-none">
        Fale conosco no WhatsApp
        <div className="absolute top-full right-4 w-2 h-2 bg-black transform rotate-45 -mt-1"></div>
      </div>
    </div>
  );
}
