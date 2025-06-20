import React from "react";
import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Home from "@/pages/home";
import NotFound from "@/pages/not-found";
import AdminLogin from "@/pages/admin-login";
import AdminDashboard from "@/pages/admin-dashboard";

function Router() {
  return React.createElement(Switch, null,
    React.createElement(Route, { path: "/", component: Home }),
    React.createElement(Route, { path: "/admin/login", component: AdminLogin }),
    React.createElement(Route, { path: "/admin/dashboard", component: AdminDashboard }),
    React.createElement(Route, { component: NotFound })
  );
}

function OriginalApp() {
  return React.createElement(QueryClientProvider, { client: queryClient },
    React.createElement(TooltipProvider, null,
      React.createElement(Toaster),
      React.createElement(Router)
    )
  );
}

export default OriginalApp;