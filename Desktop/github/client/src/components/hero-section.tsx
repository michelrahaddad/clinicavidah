import { CreditCard } from "lucide-react";
import { scrollToElement } from "@/lib/utils";
import type { SelectedPlan } from "@shared/types";

interface HeroSectionProps {
  onSelectPlan: (plan: SelectedPlan) => void;
}

export default function HeroSection({ onSelectPlan }: HeroSectionProps) {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-24 overflow-hidden">
      <div className="absolute inset-0 gradient-bg opacity-5"></div>
      
      {/* Floating geometric elements - hidden on mobile */}
      <div className="hidden md:block absolute top-20 left-10 w-20 h-20 bg-[#00B894]/20 rounded-full animate-float"></div>
      <div className="hidden md:block absolute bottom-20 right-10 w-32 h-32 bg-[#0984E3]/20 rounded-xl animate-float" style={{animationDelay: '-2s'}}></div>
      <div className="hidden md:block absolute top-1/2 left-1/4 w-16 h-16 bg-[#00B894]/30 rounded-lg animate-float" style={{animationDelay: '-4s'}}></div>
      
      <div className="container mx-auto px-4 text-center relative z-10">
        <div className="animate-slide-up">
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-bold mb-4 md:mb-6 leading-tight">
            <span className="gradient-text">Seu Cartão de Benefícios,</span>
            <br />
            <span className="text-[#636E72]">Seu Estilo de Vida</span>
          </h1>
          <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-[#636E72] mb-6 md:mb-8 max-w-3xl mx-auto leading-relaxed px-4">
            Descontos em saúde, bem-estar e muito mais. Um cartão para facilitar sua vida e cuidar da sua família.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <button 
              onClick={() => scrollToElement('planos')}
              className="bg-[#00B894] text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-[#009d7f] transition-all transform hover:scale-105 animate-glow"
            >
              Ver Planos
            </button>
            <button 
              onClick={() => scrollToElement('beneficios')}
              className="border-2 border-[#0984E3] text-[#0984E3] px-8 py-4 rounded-full font-semibold text-lg hover:bg-[#0984E3] hover:text-white transition-all"
            >
              Saiba Mais
            </button>
          </div>

          {/* Digital Card Preview */}
          <div className="relative max-w-sm mx-auto animate-fade-in" style={{animationDelay: '0.5s'}}>
            <div className="glass-card rounded-2xl p-6 transform rotate-3 hover:rotate-0 transition-transform duration-500">
              <div className="gradient-bg rounded-xl p-6 text-white relative overflow-hidden">
                <div className="absolute top-2 right-2 w-8 h-8 bg-white/20 rounded-full"></div>
                <div className="absolute bottom-2 left-2 w-6 h-6 bg-white/20 rounded-full"></div>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center justify-center min-w-[70px]">
                    <img 
                      src="/logo-vidah.png" 
                      alt="Cartão Vidah" 
                      className="h-6 w-auto max-w-[80px] object-contain filter brightness-0 invert"
                    />
                  </div>
                  <CreditCard className="text-2xl opacity-80" size={32} />
                </div>
                <div className="space-y-2">
                  <div className="text-sm opacity-80">CARTÃO + VIDAH</div>
                  <div className="font-bold text-lg">João Silva</div>
                  <div className="text-sm opacity-80">Válido até 12/2025</div>
                </div>
                <div className="absolute bottom-4 right-4">
                  <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                    <div className="w-8 h-8 bg-white/40 rounded grid grid-cols-3 gap-0.5">
                      {[...Array(9)].map((_, i) => (
                        <div key={i} className="bg-white/60 rounded-sm"></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
