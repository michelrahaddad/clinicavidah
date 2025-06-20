import Header from "@/components/header";
import HeroSection from "@/components/hero-section";
import BenefitsSection from "@/components/benefits-section";
import PlansSection from "@/components/plans-section";
import CheckoutModal from "@/components/checkout-modal";
import HowItWorksSection from "@/components/how-it-works-section";
import PartnersSection from "@/components/partners-section";
import FaqSection from "@/components/faq-section";
import Footer from "@/components/footer";
import WhatsAppFloat from "@/components/whatsapp-float";
import { useState } from "react";
import type { SelectedPlan } from "@shared/types";

export default function Home() {
  const [selectedPlan, setSelectedPlan] = useState<SelectedPlan | null>(null);
  const [showCheckout, setShowCheckout] = useState(false);

  const handleSelectPlan = (plan: SelectedPlan) => {
    setSelectedPlan(plan);
    setShowCheckout(true);
  };

  const handleCloseCheckout = () => {
    setShowCheckout(false);
    setSelectedPlan(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 overflow-x-hidden">
      <Header />
      <HeroSection onSelectPlan={handleSelectPlan} />
      <BenefitsSection />
      <PlansSection onSelectPlan={handleSelectPlan} />
      <HowItWorksSection />
      <PartnersSection />
      <FaqSection />
      <Footer />
      <WhatsAppFloat />
      
      {showCheckout && selectedPlan && (
        <CheckoutModal
          plan={selectedPlan}
          onClose={handleCloseCheckout}
        />
      )}
    </div>
  );
}
