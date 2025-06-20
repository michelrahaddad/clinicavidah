import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { BarChart3, Download, LogOut, MessageCircle, Users, Calendar, Phone } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

interface WhatsappConversion {
  id: number;
  phone: string | null;
  name: string | null;
  email: string | null;
  buttonType: string;
  planName: string | null;
  doctorName: string | null;
  ipAddress: string | null;
  userAgent: string | null;
  createdAt: string;
}

export default function AdminDashboard() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [adminUser, setAdminUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    const user = localStorage.getItem("admin_user");
    
    if (!token || !user) {
      setLocation("/admin/login");
      return;
    }
    
    setAdminUser(JSON.parse(user));
  }, [setLocation]);

  const { data: rawConversions, isLoading, refetch } = useQuery({
    queryKey: ["/api/admin/conversions", startDate, endDate],
    queryFn: async () => {
      const token = localStorage.getItem("admin_token");
      if (!token) {
        throw new Error("Token não encontrado");
      }

      let url = "/api/admin/conversions";
      if (startDate && endDate) {
        url += `?startDate=${startDate}&endDate=${endDate}`;
      }

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem("admin_token");
          localStorage.removeItem("admin_user");
          setLocation("/admin/login");
          throw new Error("Token expirado");
        }
        throw new Error("Erro ao buscar conversões");
      }

      const result = await response.json();
      // Extrair dados da estrutura ApiResponse
      return result.data || result;
    },
    enabled: !!localStorage.getItem("admin_token"),
  });

  // Garantir que conversions seja sempre um array
  const conversions = Array.isArray(rawConversions) ? rawConversions : [];

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    setLocation("/admin/login");
  };

  const handleExportMarketing = async () => {
    try {
      const token = localStorage.getItem("admin_token");
      if (!token) {
        toast({
          title: "Erro",
          description: "Token de acesso não encontrado",
          variant: "destructive",
        });
        return;
      }

      let url = "/api/admin/conversions/export";
      if (startDate && endDate) {
        url += `?startDate=${startDate}&endDate=${endDate}`;
      }

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao exportar dados");
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = "leads-marketing-digital.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      toast({
        title: "Sucesso",
        description: "Lista para anúncios exportada! Compatível com Google e Facebook Ads.",
      });
    } catch (error) {
      console.error("Export error:", error);
      toast({
        title: "Erro",
        description: "Erro ao exportar dados",
        variant: "destructive",
      });
    }
  };



  const getButtonTypeLabel = (type: string) => {
    switch (type) {
      case "plan_subscription":
        return "Assinatura de Plano";
      case "doctor_appointment":
        return "Consulta Médica";
      case "enterprise_quote":
        return "Cotação Empresarial";
      default:
        return type;
    }
  };

  const getButtonTypeColor = (type: string) => {
    switch (type) {
      case "plan_subscription":
        return "bg-green-100 text-green-800";
      case "doctor_appointment":
        return "bg-blue-100 text-blue-800";
      case "enterprise_quote":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const stats = {
    total: conversions.length,
    planSubscriptions: conversions.filter((c: any) => c.buttonType === "plan_subscription").length,
    doctorAppointments: conversions.filter((c: any) => c.buttonType === "doctor_appointment").length,
    enterpriseQuotes: conversions.filter((c: any) => c.buttonType === "enterprise_quote").length,
  };

  if (!adminUser) {
    return <div>Carregando...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-[#00B894] to-[#0984E3] rounded-full flex items-center justify-center">
                <BarChart3 className="text-white text-sm sm:text-lg" />
              </div>
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-[#636E72]">Dashboard Administrativo</h1>
                <p className="text-xs sm:text-sm text-gray-600">Bem-vindo, {adminUser.username}</p>
              </div>
            </div>
            <Button
              onClick={handleLogout}
              variant="outline"
              className="flex items-center gap-2 text-sm"
              size="sm"
            >
              <LogOut size={14} />
              Sair
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Conversões</CardTitle>
              <MessageCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Assinaturas de Planos</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.planSubscriptions}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Consultas Médicas</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.doctorAppointments}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cotações Empresariais</CardTitle>
              <Phone className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{stats.enterpriseQuotes}</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Export */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Filtros e Exportação</CardTitle>
            <CardDescription>
              Filtre as conversões por período e exporte os dados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Data Inicial</label>
                  <Input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Data Final</label>
                  <Input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full"
                  />
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-2">
                <Button 
                  onClick={() => refetch()} 
                  variant="outline" 
                  className="w-full sm:w-auto"
                >
                  Filtrar
                </Button>
                <Button 
                  onClick={handleExportMarketing} 
                  className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 w-full sm:w-auto"
                >
                  <Download size={16} />
                  <span className="hidden sm:inline">Exportar para Anúncios</span>
                  <span className="sm:hidden">Anúncios</span>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Conversions Table */}
        <Card>
          <CardHeader>
            <CardTitle>Conversões do WhatsApp</CardTitle>
            <CardDescription>
              Lista de todas as conversões registradas através dos botões do site
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">Carregando...</div>
            ) : conversions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Nenhuma conversão encontrada
              </div>
            ) : (
              <>
                {/* Desktop Table */}
                <div className="hidden lg:block overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Nome</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Telefone</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Plano/Médico</TableHead>
                        <TableHead>IP</TableHead>
                        <TableHead>Data</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {conversions.map((conversion: any) => (
                        <TableRow key={conversion.id}>
                          <TableCell className="font-medium">#{conversion.id}</TableCell>
                          <TableCell>{conversion.name || "-"}</TableCell>
                          <TableCell>{conversion.email || "-"}</TableCell>
                          <TableCell>{conversion.phone || "-"}</TableCell>
                          <TableCell>
                            <Badge className={getButtonTypeColor(conversion.buttonType)}>
                              {getButtonTypeLabel(conversion.buttonType)}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {conversion.planName || conversion.doctorName || "-"}
                          </TableCell>
                          <TableCell className="text-xs text-gray-500">
                            {conversion.ipAddress || "-"}
                          </TableCell>
                          <TableCell>
                            {new Date(conversion.createdAt).toLocaleString("pt-BR")}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* Mobile Cards */}
                <div className="lg:hidden space-y-4">
                  {conversions.map((conversion: any) => (
                    <div key={conversion.id} className="bg-gray-50 rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">#{conversion.id}</span>
                        <Badge className={getButtonTypeColor(conversion.buttonType)}>
                          {getButtonTypeLabel(conversion.buttonType)}
                        </Badge>
                      </div>
                      
                      {conversion.name && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Nome:</span>
                          <span className="text-sm font-medium">{conversion.name}</span>
                        </div>
                      )}
                      
                      {conversion.email && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Email:</span>
                          <span className="text-sm font-medium break-all">{conversion.email}</span>
                        </div>
                      )}
                      
                      {conversion.phone && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Telefone:</span>
                          <span className="text-sm font-medium">{conversion.phone}</span>
                        </div>
                      )}
                      
                      {(conversion.planName || conversion.doctorName) && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">
                            {conversion.planName ? 'Plano:' : 'Médico:'}
                          </span>
                          <span className="text-sm font-medium">
                            {conversion.planName || conversion.doctorName}
                          </span>
                        </div>
                      )}
                      
                      <div className="flex justify-between pt-2 border-t border-gray-200">
                        <span className="text-xs text-gray-500">
                          {new Date(conversion.createdAt).toLocaleDateString("pt-BR")}
                        </span>
                        <span className="text-xs text-gray-500">
                          {conversion.ipAddress || "-"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}