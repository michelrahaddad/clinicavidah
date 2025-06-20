import { useState } from "react";
import { Menu, X, Settings } from "lucide-react";
import { scrollToElement } from "@/lib/utils";
import { Link } from "wouter";

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleNavClick = (elementId: string) => {
    scrollToElement(elementId);
    setIsMenuOpen(false);
  };

  return (
    <header className="fixed top-0 w-full bg-white/90 backdrop-blur-md shadow-sm z-50 border-b border-gray-100">
      <nav className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="logo-container">
          <img 
            src="/logo-vidah.png" 
            alt="Cartão Vidah" 
            className="logo-vidah logo-header h-8 sm:h-10 md:h-12 lg:h-14 w-auto object-contain transition-all duration-300 drop-shadow-lg"
          />
        </div>
        
        <div className="hidden md:flex items-center space-x-8">
          <button 
            onClick={() => handleNavClick('beneficios')}
            className="text-[#636E72] hover:text-[#00B894] transition-colors"
          >
            Benefícios
          </button>
          <button 
            onClick={() => handleNavClick('planos')}
            className="text-[#636E72] hover:text-[#00B894] transition-colors"
          >
            Planos
          </button>
          <button 
            onClick={() => handleNavClick('como-funciona')}
            className="text-[#636E72] hover:text-[#00B894] transition-colors"
          >
            Como Funciona
          </button>
          <button 
            onClick={() => handleNavClick('parceiros')}
            className="text-[#636E72] hover:text-[#00B894] transition-colors"
          >
            Parceiros
          </button>
          <button 
            onClick={() => handleNavClick('faq')}
            className="text-[#636E72] hover:text-[#00B894] transition-colors"
          >
            FAQ
          </button>

          <button 
            onClick={() => handleNavClick('planos')}
            className="bg-[#00B894] text-white px-6 py-2 rounded-full hover:bg-[#009d7f] transition-colors font-medium"
          >
            Assinar Agora
          </button>
        </div>
        
        <button 
          className="md:hidden text-[#636E72]"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>
      
      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 shadow-lg">
          <div className="px-4 py-4 space-y-4">
            <button 
              onClick={() => handleNavClick('beneficios')}
              className="block w-full text-left text-[#636E72] hover:text-[#00B894] transition-colors py-2"
            >
              Benefícios
            </button>
            <button 
              onClick={() => handleNavClick('planos')}
              className="block w-full text-left text-[#636E72] hover:text-[#00B894] transition-colors py-2"
            >
              Planos
            </button>
            <button 
              onClick={() => handleNavClick('como-funciona')}
              className="block w-full text-left text-[#636E72] hover:text-[#00B894] transition-colors py-2"
            >
              Como Funciona
            </button>
            <button 
              onClick={() => handleNavClick('faq')}
              className="block w-full text-left text-[#636E72] hover:text-[#00B894] transition-colors py-2"
            >
              FAQ
            </button>

            <button 
              onClick={() => handleNavClick('planos')}
              className="w-full bg-[#00B894] text-white px-6 py-3 rounded-full hover:bg-[#009d7f] transition-colors font-medium"
            >
              Assinar Agora
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
