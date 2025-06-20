import { Facebook, Instagram, Linkedin, Settings } from "lucide-react";
import { Link } from "wouter";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { name: "Planos", href: "#planos" },
      { name: "Benefícios", href: "#beneficios" },
      { name: "Empresas Parceiras", href: "#parceiros" }
    ],
    support: [
      { name: "Central de Ajuda", href: "#ajuda" },
      { name: "Fale Conosco", href: "#contato" },
      { name: "WhatsApp", href: "https://wa.me/5516993247676" }
    ],
    company: [
      { name: "Sobre Nós", href: "#sobre" },
      { name: "Contato", href: "mailto:cartaomaisvidah@gmail.com" },
      { name: "Trabalhe Conosco", href: "#carreiras" }
    ]
  };

  const handleLinkClick = (href: string) => {
    if (href.startsWith('#')) {
      const elementId = href.substring(1);
      const element = document.getElementById(elementId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    } else if (href.startsWith('http') || href.startsWith('mailto')) {
      window.open(href, '_blank');
    }
  };

  return (
    <footer className="bg-[#636E72] text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand Section */}
          <div>
            <div className="mb-4 logo-container">
              <img 
                src="/logo-vidah.png" 
                alt="Cartão Vidah" 
                className="logo-vidah logo-footer h-6 sm:h-8 md:h-10 w-auto object-contain transition-all duration-300 filter brightness-110"
              />
            </div>
            <p className="text-gray-300 leading-relaxed">
              Benefícios exclusivos para você e sua família com tecnologia e praticidade. 
              Mais de 20 empresas parceiras oferecendo descontos especiais.
            </p>
            <div className="mt-4">
              <p className="text-sm text-gray-400">
                VIDAH BENEFICIOS LTDA<br />
                CNPJ: 60.926.407/0001-76
              </p>
            </div>
          </div>
          
          {/* Product Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white">Produto</h4>
            <ul className="space-y-2">
              {footerLinks.product.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => handleLinkClick(link.href)}
                    className="text-gray-300 hover:text-white transition-colors text-left"
                  >
                    {link.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Support Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white">Suporte</h4>
            <ul className="space-y-2">
              {footerLinks.support.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => handleLinkClick(link.href)}
                    className="text-gray-300 hover:text-white transition-colors text-left"
                  >
                    {link.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Company Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white">Empresa</h4>
            <ul className="space-y-2">
              {footerLinks.company.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => handleLinkClick(link.href)}
                    className="text-gray-300 hover:text-white transition-colors text-left"
                  >
                    {link.name}
                  </button>
                </li>
              ))}
            </ul>
            
            {/* Contact Info */}
            <div className="mt-6">
              <h5 className="font-medium text-white mb-2">Atendimento</h5>
              <p className="text-gray-300 text-sm">
                Segunda à Sexta: 8h às 18h<br />
                Sábado: 8h às 12h
              </p>
              <p className="text-gray-300 text-sm mt-2">
                📱 (16) 99324-7676<br />
                ✉️ cartaomaisvidah@gmail.com
              </p>
            </div>
          </div>
        </div>
        
        {/* Bottom Section */}
        <div className="border-t border-gray-600 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-300 mb-4 md:mb-0 text-center md:text-left">
            © {currentYear} Vidah Benefícios. Todos os direitos reservados.
            <div className="text-sm mt-1">
              <button className="hover:text-white transition-colors mr-4">
                Política de Privacidade
              </button>
              <button className="hover:text-white transition-colors">
                Termos de Uso
              </button>
            </div>
          </div>
          
          {/* Social Media */}
          <div className="flex space-x-4">
            <button 
              onClick={() => window.open('#', '_blank')}
              className="text-gray-300 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
              aria-label="Facebook"
            >
              <Facebook size={20} />
            </button>
            <button 
              onClick={() => window.open('#', '_blank')}
              className="text-gray-300 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
              aria-label="Instagram"
            >
              <Instagram size={20} />
            </button>
            <button 
              onClick={() => window.open('#', '_blank')}
              className="text-gray-300 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
              aria-label="LinkedIn"
            >
              <Linkedin size={20} />
            </button>
          </div>
        </div>



        {/* Additional Footer Info */}
        <div className="mt-8 pt-6 border-t border-gray-600 text-center">
          <div className="grid md:grid-cols-3 gap-6 text-sm text-gray-400">
            <div>
              <h6 className="font-medium text-white mb-2">Segurança</h6>
              <p>Certificação SSL • Dados Criptografados • PCI Compliance</p>
            </div>
            <div>
              <h6 className="font-medium text-white mb-2">Pagamentos</h6>
              <p>PIX • Cartão de Crédito • Boleto Bancário</p>
            </div>
            <div>
              <h6 className="font-medium text-white mb-2">Cobertura</h6>
              <p>Válido em todo Brasil • 20+ Parceiros • Suporte 24/7</p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
