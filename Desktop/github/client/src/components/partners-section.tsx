import { motion } from "framer-motion";
import { useState, useMemo, useCallback } from "react";
import { Stethoscope, ShoppingBag, Star, Users, MapPin, Percent, User, Building, Phone, Globe, MessageCircle, Plus } from "lucide-react";
import LeadCaptureModal from "./lead-capture-modal";
// Placeholder melhorado para logos das empresas
const placeholderLogo = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='80' viewBox='0 0 120 80'%3E%3Cdefs%3E%3ClinearGradient id='grad' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%2300B894;stop-opacity:0.1' /%3E%3Cstop offset='100%25' style='stop-color:%2300B894;stop-opacity:0.05' /%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='120' height='80' fill='url(%23grad)' rx='8'/%3E%3Ccircle cx='60' cy='30' r='12' fill='%2300B894' opacity='0.2'/%3E%3Ctext x='60' y='55' text-anchor='middle' fill='%2300B894' font-family='Arial, sans-serif' font-size='11' font-weight='600'%3ELogo Empresa%3C/text%3E%3C/svg%3E";

// Logo do Grupo Vidah
const vidahLogoUrl = "/logos/vidah-logo.png";

// Logo do Silasgás
const silasgasLogoUrl = "/logos/silagas-logo.jpeg";

// Logo do Dom Pedro
const domPedroLogoUrl = "/logos/dom-pedro-logo.jpg";

// Logo do Pronto Vet
const prontoVetLogoUrl = "/logos/pronto-vet-logo.png";

// Logo das Rações Santa Tereza
const santaTerezaLogoUrl = "/logos/santa-tereza-logo.png";

// Logo do Hospital Malzoni
const hospitalMalzoniLogoUrl = "/logos/hospital-malzoni-logo.png";

// Logo da Drogaven
const drogavenLogoUrl = "/logos/drogaven-logo.png";

// Logo das Óticas Carol
const oticasCarolLogoUrl = "/logos/oticas-carol-logo.png";

// Logo da Fiducia Eletro
const fiduciaEletroLogoUrl = "/logos/fiducia-eletro-logo.png";

// Logo da Funerária Canaã
const funerariaCanaLogoUrl = "/logos/funeraria-canaa-logo.png";

// Logo do Lab 7 (baseado na imagem real - círculo verde com Lab 7)
const lab7LogoUrl = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%2398D8C8'/%3E%3Ctext x='30' y='70' fill='white' font-family='Arial, sans-serif' font-size='18' font-weight='bold' stroke='%23333' stroke-width='0.5'%3ELab%3C/text%3E%3Ctext x='75' y='70' fill='white' font-family='Arial, sans-serif' font-size='24' font-weight='bold' stroke='%23FF4757' stroke-width='1'%3E7%3C/text%3E%3Ccircle cx='85' cy='55' r='2' fill='%23FF4757'/%3E%3Ccircle cx='90' cy='60' r='1.5' fill='%23FF4757'/%3E%3C/svg%3E";

// Logo da Magia do Sorriso (baseado na imagem real - dente roxo/laranja)
const magiaSorrisoLogoUrl = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%23f8f9fa'/%3E%3Cpath d='M25 35 Q35 25 45 35 Q45 45 35 55 Q25 45 25 35 Z' fill='%238B5CF6' opacity='0.8'/%3E%3Cpath d='M35 35 Q45 25 55 35 Q55 50 45 60 Q35 50 35 35 Z' fill='%23F97316' opacity='0.7'/%3E%3Ctext x='70' y='45' fill='%23666' font-family='Arial, sans-serif' font-size='12' font-weight='600'%3EMAGIA DO%3C/text%3E%3Ctext x='70' y='60' fill='%23666' font-family='Arial, sans-serif' font-size='12' font-weight='600'%3ESORRISO%3C/text%3E%3Cpath d='M40 70 Q50 75 60 70' stroke='%23F97316' stroke-width='2' fill='none'/%3E%3C/svg%3E";

// Logo da Reabilitar Neuroped (baseado na imagem real - texto colorido com cruz)
const reabilitarNeuropedLogoUrl = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%23f8f9fa'/%3E%3Ctext x='60' y='25' text-anchor='middle' fill='%234A90E2' font-family='Arial, sans-serif' font-size='8' font-weight='600'%3ECLÍNICA%3C/text%3E%3Ctext x='60' y='45' text-anchor='middle' fill='%234A90E2' font-family='Arial, sans-serif' font-size='6' font-weight='400'%3EREABILITAR%3C/text%3E%3Ctext x='60' y='65' text-anchor='middle' fill='%232563EB' font-family='Arial, sans-serif' font-size='14' font-weight='800'%3ENEURO PED%3C/text%3E%3Ccircle cx='85' cy='55' r='8' fill='%232563EB'/%3E%3Cpath d='M82 55 L88 55 M85 52 L85 58' stroke='white' stroke-width='2'/%3E%3Ctext x='60' y='85' text-anchor='middle' fill='%234A90E2' font-family='Arial, sans-serif' font-size='7' font-weight='400'%3EFisioterapia Pediátrica%3C/text%3E%3Cpath d='M95 60 Q105 65 100 70' stroke='%234A90E2' stroke-width='1' fill='none'/%3E%3C/svg%3E";

// Logo do Corpo em Harmonia (baseado na imagem real - figura humana com folha)
const corpoHarmoniaLogoUrl = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%23f8f9fa'/%3E%3Ccircle cx='45' cy='35' r='4' fill='%2364B5F6'/%3E%3Cpath d='M45 40 L45 65 M40 50 L50 50 M40 60 L50 60' stroke='%2364B5F6' stroke-width='2'/%3E%3Ccircle cx='60' cy='45' r='15' fill='none' stroke='%2368B984' stroke-width='2'/%3E%3Cpath d='M65 30 Q70 25 75 30 Q75 40 70 45 Q65 40 65 30 Z' fill='%2368B984'/%3E%3Ctext x='60' y='85' text-anchor='middle' fill='%2364B5F6' font-family='Arial, sans-serif' font-size='10' font-weight='600'%3ECORPO EM HARMONIA%3C/text%3E%3Ctext x='60' y='98' text-anchor='middle' fill='%2368B984' font-family='Arial, sans-serif' font-size='6' font-weight='400'%3ESintalize sua saúde. Equilibre sua vida%3C/text%3E%3C/svg%3E";

// Logo do Silasgás (SVG energia)
const silasgasLogoSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%23FF5722'/%3E%3Ccircle cx='60' cy='50' r='20' fill='none' stroke='white' stroke-width='3'/%3E%3Cpath d='M45 50 L75 50 M60 35 L60 65' stroke='white' stroke-width='2'/%3E%3Ctext x='60' y='85' text-anchor='middle' fill='white' font-family='Arial, sans-serif' font-size='10' font-weight='bold'%3ESILASGÁS%3C/text%3E%3C/svg%3E";

// Logo da Evolução Centro Multidisciplinar (baseado na imagem real - família colorida)
const evolucaoLogoUrl = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%23f8f9fa'/%3E%3Ccircle cx='25' cy='45' r='3' fill='%23FFD700'/%3E%3Ccircle cx='35' cy='40' r='4' fill='%23FF6B9D'/%3E%3Ccircle cx='45' cy='35' r='5' fill='%23E74C3C'/%3E%3Ccircle cx='55' cy='35' r='5' fill='%234CAF50'/%3E%3Ccircle cx='65' cy='40' r='4' fill='%239C27B0'/%3E%3Ccircle cx='75' cy='45' r='4' fill='%23607D8B'/%3E%3Cpath d='M25 50 L25 65 M35 45 L35 65 M45 40 L45 65 M55 40 L55 65 M65 45 L65 65 M75 50 L75 65' stroke='%23666' stroke-width='2'/%3E%3Ctext x='60' y='80' text-anchor='middle' fill='%232196F3' font-family='Arial, sans-serif' font-size='10' font-weight='700'%3Eevolução%3C/text%3E%3Ctext x='60' y='95' text-anchor='middle' fill='%234CAF50' font-family='Arial, sans-serif' font-size='6' font-weight='400'%3ECentro de Integração Multidisciplinar%3C/text%3E%3C/svg%3E";

// Silasgás já declarado acima

const prontoVetLogo = placeholderLogo;
const domPedroLogo = placeholderLogo;
const santaTerezaLogo = placeholderLogo;
const hospitalMalzoniLogo = placeholderLogo;
const sosEnfermagemLogo = placeholderLogo;
const funerariaCanaaLogo = placeholderLogo;
const fiduciaEletroLogo = placeholderLogo;
const drogavenLogo = placeholderLogo;
const oticasCarolLogo = placeholderLogo;
const silagasLogo = placeholderLogo;

// Logos adicionais das empresas parceiras - aguardando upload
const evolucaoLogo = placeholderLogo;
const reabilitarNeuropedLogo = placeholderLogo;
const corpoHarmoniaLogo = placeholderLogo;
const inerpLogo = placeholderLogo;
const ipcLogo = placeholderLogo;
const magiaDoSorrisoLogo = placeholderLogo;
const lab7Logo = placeholderLogo;

// Doctor photos
import drWilliamTeixeiraHaddadFoto from "@/assets/doctors/dr-william-teixeira-haddad.jpg";
import drMichelRaineriHaddadFoto from "@/assets/doctors/dr-michel-raineri-haddad.jpg";
import drWilliamTeixeiraHaddadJrFoto from "@/assets/doctors/dr-william-teixeira-haddad-jr.jpg";
import drAlexTelesVasconcelosFoto from "@/assets/doctors/dr-alex-teles-vasconcelos.jpg";
import drDiegoFoto from "@/assets/doctors/dr-diego.jpg";
import draIsabelaCardosoFoto from "@/assets/doctors/dra-isabela-cardoso.jpg";
import draAnaSollerFoto from "@/assets/doctors/dra-ana-soller.jpg";
import draBrunaDeRosaFoto from "@/assets/doctors/dra-bruna-de-rosa.jpg";
import draGabrielaPedrolimFoto from "@/assets/doctors/dra-gabriela-pedrolim.jpg";
import drFabioMalaraFoto from "@/assets/doctors/dr-fabio-malara.jpg";
import draClaudiaArrudaFoto from "@/assets/doctors/dra-claudia-arruda.jpg";
import draMaysaQuarteiroFoto from "@/assets/doctors/dra-maysa-quarteiro.jpg";
import draVanessaYucraFoto from "@/assets/doctors/dra-vanessa-yucra.jpg";
import draBrunaMargadonaFoto from "@/assets/doctors/dra-bruna-margadona.jpg";

const medicos = [
  { nome: "Dr. William Teixeira Haddad", especialidade: "Cardiologia e Clínica Médica", foto: drWilliamTeixeiraHaddadFoto },
  { nome: "Dr. Michel Raineri Haddad", especialidade: "Cardiologia e Clínica Médica", foto: drMichelRaineriHaddadFoto },
  { nome: "Dr. William Teixeira Haddad Jr.", especialidade: "Radiologia", foto: drWilliamTeixeiraHaddadJrFoto },
  { nome: "Dr. Alex Teles Vasconcelos", especialidade: "Oftalmologia", foto: drAlexTelesVasconcelosFoto },
  { nome: "Dr Diego Rodrigues Charamitara", especialidade: "Clínico Geral", foto: drDiegoFoto },
  { nome: "Dra Isabela Cardoso", especialidade: "Ginecologia e Obstetrícia", foto: draIsabelaCardosoFoto },
  { nome: "Dra Ana Soler", especialidade: "Dermatologista", foto: draAnaSollerFoto },
  { nome: "Dra Bruna de Rosa", especialidade: "Psiquiatra", foto: draBrunaDeRosaFoto },
  { nome: "Dra Gabriela Pedrolim", especialidade: "Endocrinologista", foto: draGabrielaPedrolimFoto },
  { nome: "Dr Fabio Malara", especialidade: "Cardiologista", foto: drFabioMalaraFoto },
  { nome: "Dra Claudia Arruda", especialidade: "Psiquiatra", foto: draClaudiaArrudaFoto },
  { nome: "Dra Maysa Quarteiro", especialidade: "Ginecologia e Obstetrícia", foto: draMaysaQuarteiroFoto },
  { nome: "Dra Vanessa Yucra", especialidade: "Psicóloga", foto: draVanessaYucraFoto },
  { nome: "Dra Bruna Margadona", especialidade: "Ginecologia e Obstetrícia", foto: draBrunaMargadonaFoto },
  { nome: "Pedro Betini", especialidade: "Psicólogo", foto: null },
  { nome: "Erika Aravechia", especialidade: "Psicopedagoga", foto: null },
  { nome: "Bruna Margadona", especialidade: "Fisioterapeuta", foto: null },
  { nome: "Sofia Mella", especialidade: "Psicóloga Infantil", foto: null }
];

const parceiroDestaque = {
  nome: "Grupo Vidah",
  desconto: "10 a 40% OFF",
  categoria: "Parceiro Principal",
  logo: vidahLogoUrl,
  endereco: "R. XV de Novembro, 594 - Centro, Ibitinga - SP, 14940-000",
  telefone: "(16) 3342-4768",
  site: "https://www.grupovidah.com.br/",
  destaque: true
};

// Nova estrutura moderna para empresas parceiras
const parceiros = [
  { nome: "Grupo Vidah", desconto: "10-40%", categoria: "Parceiro Principal", icon: "🏥" },
  { nome: "Silasgás", desconto: "10-40%", categoria: "Energia & Gás", icon: "🔥" },
  { nome: "Óticas Carol", desconto: "10-40%", categoria: "Saúde Visual", icon: "👁️" },
  { nome: "Fiducia Eletro", desconto: "10-40%", categoria: "Tecnologia", icon: "⚡" },
  { nome: "Evolução Centro Multidisciplinar", desconto: "10-40%", categoria: "Bem-estar", icon: "🏥" },
  { nome: "Pronto Vet", desconto: "10-40%", categoria: "Pet Care", icon: "🐾" },
  { nome: "Rações Santa Tereza", desconto: "10-40%", categoria: "Pet Shop", icon: "🐕" },
  { nome: "Reabilitar Neuroped", desconto: "10-40%", categoria: "Fisioterapia", icon: "🏃‍♂️" },
  { nome: "Corpo em Harmonia", desconto: "10-40%", categoria: "Fitness", icon: "🧘‍♀️" },
  { nome: "Drogaven", desconto: "10-40%", categoria: "Farmácia", icon: "💊" },
  { nome: "Hospital Malzoni", desconto: "10-40%", categoria: "Saúde", icon: "🏥" },
  { nome: "Dom Pedro", desconto: "10-40%", categoria: "Alimentação", icon: "🥬" },
  { nome: "Funerária Canaã", desconto: "10-40%", categoria: "Serviços", icon: "🕊️" },
  { nome: "Magia do Sorriso", desconto: "10-40%", categoria: "Odontologia", icon: "😁" },
  { nome: "Lab 7", desconto: "10-40%", categoria: "Diagnósticos", icon: "🔬" }
];

export default function PartnersSection() {
  const [showAllPartners, setShowAllPartners] = useState(false);
  const [showAllSegments, setShowAllSegments] = useState(false);
  
  console.log('PartnersSection renderizando:', { showAllPartners, showAllSegments });
  const [modalData, setModalData] = useState<{
    isOpen: boolean;
    buttonType: 'plan_subscription' | 'doctor_appointment' | 'enterprise_quote';
    planName?: string;
    doctorName?: string;
    whatsappPhone: string;
    whatsappMessage: string;
  }>({
    isOpen: false,
    buttonType: 'doctor_appointment',
    whatsappPhone: '5516993247676',
    whatsappMessage: ''
  });

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  // Memoize calculated data for better performance
  const { displayedPartners, displayedMedicos } = useMemo(() => {
    const topPartners = parceiros.slice(0, 8);
    const topMedicos = medicos.slice(0, 4);
    
    return {
      displayedPartners: showAllPartners ? parceiros : topPartners,
      displayedMedicos: showAllSegments ? medicos : topMedicos
    };
  }, [showAllPartners, showAllSegments]);

  const handleDoctorAppointment = useCallback((medico: any) => {
    setModalData({
      isOpen: true,
      buttonType: 'doctor_appointment',
      doctorName: medico.nome,
      whatsappPhone: '5516993247676',
      whatsappMessage: `Gostaria de agendar uma consulta com ${medico.nome} (${medico.especialidade}). Poderia me ajudar com os horários disponíveis?`
    });
  }, []);

  return (
    <section id="parceiros" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-[#00B894]/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#0984E3]/5 rounded-full blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 relative">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="text-center mb-16"
        >
          <motion.div variants={itemVariants} className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-sm px-6 py-3 rounded-full border border-[#00B894]/20 mb-6">
            <Users className="w-5 h-5 text-[#00B894]" />
            <span className="text-[#636E72] font-medium">Rede Credenciada</span>
          </motion.div>
          
          <motion.h2 variants={itemVariants} className="text-3xl md:text-4xl lg:text-5xl font-bold text-[#636E72] mb-6">
            Nossos <span className="text-[#00B894]">Parceiros</span>
          </motion.h2>
          
          <motion.p variants={itemVariants} className="text-lg md:text-xl text-[#636E72] max-w-3xl mx-auto px-4">
            Uma rede completa de profissionais de saúde e empresas parceiras para oferecer 
            os melhores benefícios e descontos exclusivos
          </motion.p>
        </motion.div>

        {/* Statistics */}
        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-16"
        >
          <motion.div variants={itemVariants} className="glass-card text-center p-4 md:p-6 rounded-2xl">
            <div className="w-10 h-10 md:w-12 md:h-12 bg-[#00B894]/10 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4">
              <Stethoscope className="w-5 h-5 md:w-6 md:h-6 text-[#00B894]" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-[#636E72] mb-1 md:mb-2">18+</div>
            <div className="text-[#636E72] font-medium text-sm md:text-base">Médicos Especialistas</div>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card text-center p-4 md:p-6 rounded-2xl">
            <div className="w-10 h-10 md:w-12 md:h-12 bg-[#0984E3]/10 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4">
              <ShoppingBag className="w-5 h-5 md:w-6 md:h-6 text-[#0984E3]" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-[#636E72] mb-1 md:mb-2">15+</div>
            <div className="text-[#636E72] font-medium text-sm md:text-base">Empresas Parceiras</div>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card text-center p-4 md:p-6 rounded-2xl">
            <div className="w-10 h-10 md:w-12 md:h-12 bg-[#00B894]/10 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4">
              <Percent className="w-5 h-5 md:w-6 md:h-6 text-[#00B894]" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-[#636E72] mb-1 md:mb-2">50%</div>
            <div className="text-[#636E72] font-medium text-sm md:text-base">Desconto Máximo</div>
          </motion.div>

          <motion.div variants={itemVariants} className="glass-card text-center p-4 md:p-6 rounded-2xl">
            <div className="w-10 h-10 md:w-12 md:h-12 bg-[#0984E3]/10 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4">
              <Star className="w-5 h-5 md:w-6 md:h-6 text-[#0984E3]" />
            </div>
            <div className="text-2xl md:text-3xl font-bold text-[#636E72] mb-1 md:mb-2">41+</div>
            <div className="text-[#636E72] font-medium text-sm md:text-base">Total de Parceiros</div>
          </motion.div>
        </motion.div>

        {/* Parceiro Principal em Destaque */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="mb-16"
        >
          <motion.h3 variants={itemVariants} className="text-2xl md:text-3xl font-bold text-[#636E72] mb-8 text-center">
            Parceiro Principal
          </motion.h3>
          <motion.div variants={itemVariants} className="max-w-md mx-auto">
            <div className="relative glass-card p-8 rounded-3xl border-2 border-[#0984E3]/30 bg-gradient-to-br from-[#0984E3]/5 to-[#74B9FF]/5 overflow-hidden group hover:shadow-2xl hover:scale-105 transition-all duration-300">
              {/* Efeito de brilho */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              
              {/* Badge de destaque */}
              <div className="absolute -top-2 -right-2 bg-gradient-to-r from-[#0984E3] to-[#74B9FF] text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg">
                PRINCIPAL
              </div>
              
              <div className="relative z-10">
                <div className="relative w-24 h-24 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg overflow-hidden">
                  <img 
                    src={vidahLogoUrl} 
                    alt="Grupo Vidah Logo"
                    className="w-full h-full object-cover rounded-xl"
                  />
                  {/* Badge de desconto flutuante */}
                  <div className="absolute -top-2 -right-2 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg animate-pulse border-2 border-white">
                    20-40%
                  </div>
                </div>
                
                <h4 className="text-2xl font-bold text-[#636E72] mb-2 text-center">{parceiroDestaque.nome}</h4>
                <p className="text-[#0984E3] font-semibold text-center mb-3">{parceiroDestaque.categoria}</p>
                
                <div className="space-y-2 mb-4 text-sm text-[#636E72]/80">
                  <div className="flex items-center justify-center">
                    <MapPin className="w-4 h-4 mr-2" />
                    <span className="text-center">{parceiroDestaque.endereco}</span>
                  </div>
                  <div className="flex items-center justify-center">
                    <Phone className="w-4 h-4 mr-2" />
                    <a href={`tel:${parceiroDestaque.telefone}`} className="hover:text-[#0984E3] transition-colors">
                      {parceiroDestaque.telefone}
                    </a>
                  </div>
                  <div className="flex items-center justify-center">
                    <Globe className="w-4 h-4 mr-2" />
                    <a 
                      href={parceiroDestaque.site} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="hover:text-[#0984E3] transition-colors"
                    >
                      grupovidah.com.br
                    </a>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-[#0984E3] to-[#74B9FF] text-white px-4 py-2 rounded-full text-center font-bold shadow-lg">
                  {parceiroDestaque.desconto}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* Medical Professionals */}
        <motion.div
          key={`medicos-container-${showAllSegments}`}
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="mb-16"
        >
          <motion.h3 variants={itemVariants} className="text-2xl md:text-3xl font-bold text-[#636E72] mb-6 md:mb-8 flex items-center justify-center md:justify-start">
            <Stethoscope className="w-6 h-6 md:w-8 md:h-8 text-[#00B894] mr-2 md:mr-3" />
            Médicos Credenciados
          </motion.h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {displayedMedicos.map((medico, index) => (
              <motion.div
                key={`medico-${medico.nome}-${index}`}
                variants={itemVariants}
                className="glass-card p-6 rounded-xl hover:shadow-lg transition-all duration-300 group hover:scale-105"
              >
                <div className="text-center">
                  {/* Photo placeholder - replace with actual doctor photos */}
                  <div className="w-16 h-16 bg-gradient-to-br from-[#00B894]/20 to-[#0984E3]/20 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                    {medico.foto ? (
                      <img 
                        src={medico.foto} 
                        alt={medico.nome}
                        className="w-full h-full rounded-full object-cover"
                        loading="lazy"
                        decoding="async"
                      />
                    ) : (
                      <User className="w-8 h-8 text-[#00B894]" />
                    )}
                  </div>
                  <h4 className="font-bold text-[#636E72] mb-2 group-hover:text-[#00B894] transition-colors">
                    {medico.nome}
                  </h4>
                  <p className="text-sm text-[#636E72]/80 font-medium mb-4">
                    {medico.especialidade}
                  </p>
                  <button
                    onClick={() => handleDoctorAppointment(medico)}
                    className="w-full bg-[#00B894] text-white py-2 px-4 rounded-lg font-medium text-sm hover:bg-[#009d7f] transition-colors flex items-center justify-center gap-2"
                  >
                    <MessageCircle size={16} />
                    Agendar Consulta
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
          
          {!showAllSegments && medicos.length > 4 && (
            <div className="text-center mt-8">
              <button
                onClick={(e) => {
                  e.preventDefault();
                  console.log('Clicando em Ver mais médicos - antes do setState');
                  setShowAllSegments(true);
                  console.log('Clicando em Ver mais médicos - depois do setState');
                }}
                className="bg-[#00B894] text-white px-6 py-3 rounded-full font-semibold hover:bg-[#009d7f] transition-all transform hover:scale-105"
              >
                Ver mais médicos ({medicos.length - 4} restantes)
              </button>
            </div>
          )}
        </motion.div>

        {/* Business Partners */}
        <motion.div
          key={`parceiros-container-${showAllPartners}`}
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          <motion.h3 variants={itemVariants} className="text-3xl md:text-4xl font-bold text-center mb-12">
            <span className="bg-gradient-to-r from-[#00B894] via-[#00d2a0] to-[#0984E3] bg-clip-text text-transparent">
              Rede de Parceiros
            </span>
          </motion.h3>
          
          {/* Design Circular Moderno */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6 md:gap-8">
            {displayedPartners.map((parceiro, index) => (
              <motion.div
                key={`parceiro-${parceiro.nome}-${index}`}
                variants={itemVariants}
                className="group relative flex flex-col items-center"
              >
                {/* Container Principal Circular */}
                <div className="relative">
                  
                  {/* Badge de desconto para todos os parceiros - fora do círculo */}
                  <div className="absolute -top-2 -right-2 bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg animate-pulse border-2 border-white z-30">
                    10-40%
                  </div>
                  
                  {/* Círculo Principal com Logo */}
                  <div className="w-32 h-32 bg-gradient-to-br from-white via-gray-50 to-gray-100 rounded-full flex items-center justify-center shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:scale-110 border-4 border-white/80 relative overflow-hidden group-hover:border-[#00B894]/30">
                    
                    {/* Efeito de brilho circular */}
                    <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-full"></div>
                    
                    {/* Espaço para Logo da Empresa */}
                    <div className="relative z-10 w-20 h-20 bg-gradient-to-br from-[#00B894]/10 to-[#0984E3]/10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300 overflow-hidden">
                      {parceiro.nome === "Grupo Vidah" ? (
                        <img 
                          src={vidahLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Silasgás Ultragaz" ? (
                        <img 
                          src={silasgasLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Dom Pedro" ? (
                        <img 
                          src={domPedroLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Pronto Vet" ? (
                        <img 
                          src={prontoVetLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Rações Santa Tereza" ? (
                        <img 
                          src={santaTerezaLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Hospital Malzoni" ? (
                        <img 
                          src={hospitalMalzoniLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Drogaven" ? (
                        <img 
                          src={drogavenLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Óticas Carol" ? (
                        <img 
                          src={oticasCarolLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Fiducia Eletro" ? (
                        <img 
                          src={fiduciaEletroLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Funerária Canaã" ? (
                        <img 
                          src={funerariaCanaLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Lab 7" ? (
                        <img 
                          src={lab7LogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Magia do Sorriso" ? (
                        <img 
                          src={magiaSorrisoLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Reabilitar Neuroped" ? (
                        <img 
                          src={reabilitarNeuropedLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Corpo em Harmonia" ? (
                        <img 
                          src={corpoHarmoniaLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Silasgás" ? (
                        <img 
                          src={silasgasLogoSvg} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : parceiro.nome === "Evolução Centro Multidisciplinar" ? (
                        <img 
                          src={evolucaoLogoUrl} 
                          alt={parceiro.nome}
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : (
                        <span className="text-4xl filter drop-shadow-sm">{parceiro.icon}</span>
                      )}
                    </div>
                    

                  </div>
                  
                  {/* Anel de Progresso Animado */}
                  <div className="absolute inset-0 w-32 h-32">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="stroke-gray-200"
                        fill="none"
                        strokeWidth="2"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="stroke-[#00B894] opacity-0 group-hover:opacity-100 transition-all duration-1000 ease-out"
                        fill="none"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeDasharray="75, 100"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                  </div>
                </div>
                
                {/* Informações da Empresa */}
                <div className="mt-6 text-center">
                  <h4 className="font-bold text-gray-800 mb-2 text-sm leading-tight group-hover:text-[#00B894] transition-colors duration-300">
                    {parceiro.nome}
                  </h4>
                  
                  <div className="inline-flex items-center px-4 py-2 bg-white/80 backdrop-blur-sm text-gray-700 rounded-full text-xs font-medium shadow-sm border border-gray-200/50 group-hover:bg-[#00B894]/10 group-hover:text-[#00B894] group-hover:border-[#00B894]/20 transition-all duration-300">
                    {parceiro.categoria}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
          
          {!showAllPartners && parceiros.length > 8 && (
            <div className="text-center mt-16">
              <button
                onClick={() => setShowAllPartners(true)}
                className="group relative bg-gradient-to-r from-[#00B894] to-[#00d2a0] text-white px-12 py-5 rounded-full font-semibold hover:from-[#009d7f] hover:to-[#00B894] transition-all duration-300 shadow-xl hover:shadow-2xl transform hover:scale-105 flex items-center gap-4 mx-auto"
              >
                <span className="text-lg">Ver Todos os Parceiros</span>
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center group-hover:rotate-180 transition-transform duration-300">
                  <Plus size={20} />
                </div>
              </button>
            </div>
          )}
        </motion.div>

        {/* Call to Action */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="mt-16 text-center"
        >
          <motion.div variants={itemVariants} className="bg-gradient-to-r from-[#00B894] to-[#0984E3] rounded-3xl p-8 text-white">
            <h3 className="text-xl md:text-2xl lg:text-3xl font-bold mb-4">
              Faça Parte da Nossa Rede
            </h3>
            <p className="text-base md:text-lg mb-6 opacity-90 px-4">
              Acesse todos esses benefícios com seu Cartão Vidah e economize em consultas, 
              exames e compras em nossa rede credenciada
            </p>
            <button 
              onClick={() => document.getElementById('planos')?.scrollIntoView({ behavior: 'smooth' })}
              className="bg-white text-[#00B894] px-8 py-4 rounded-full font-bold hover:bg-gray-100 transition-colors"
            >
              Ver Planos Disponíveis
            </button>
          </motion.div>
        </motion.div>
      </div>

      <LeadCaptureModal
        isOpen={modalData.isOpen}
        onClose={() => setModalData(prev => ({ ...prev, isOpen: false }))}
        buttonType={modalData.buttonType}
        planName={modalData.planName}
        doctorName={modalData.doctorName}
        whatsappPhone={modalData.whatsappPhone}
        whatsappMessage={modalData.whatsappMessage}
      />
    </section>
  );
}