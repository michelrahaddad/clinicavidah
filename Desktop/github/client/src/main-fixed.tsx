// Temporary fix for React plugin preamble issue
// This maintains all original functionality without design changes

import { createRoot } from "react-dom/client";
import "./index.css";

// Dynamic import to bypass compilation issues
async function loadApp() {
  try {
    const { default: App } = await import("./App");
    const container = document.getElementById("root");
    if (container) {
      const root = createRoot(container);
      root.render(App());
    }
  } catch (error) {
    console.error("Error loading app:", error);
    // Fallback: load components directly
    await loadComponentsDirect();
  }
}

async function loadComponentsDirect() {
  const [
    { Switch, Route },
    { queryClient },
    { QueryClientProvider },
    { Toaster },
    { TooltipProvider },
    Home,
    NotFound,
    AdminLogin,
    AdminDashboard,
    React
  ] = await Promise.all([
    import("wouter"),
    import("./lib/queryClient"),
    import("@tanstack/react-query"),
    import("@/components/ui/toaster"),
    import("@/components/ui/tooltip"),
    import("@/pages/home"),
    import("@/pages/not-found"),
    import("@/pages/admin-login"),
    import("@/pages/admin-dashboard"),
    import("react")
  ]);

  function Router() {
    return React.createElement(Switch, null,
      React.createElement(Route, { path: "/", component: Home.default }),
      React.createElement(Route, { path: "/admin/login", component: AdminLogin.default }),
      React.createElement(Route, { path: "/admin/dashboard", component: AdminDashboard.default }),
      React.createElement(Route, { component: NotFound.default })
    );
  }

  function App() {
    return React.createElement(QueryClientProvider, { client: queryClient.queryClient },
      React.createElement(TooltipProvider.TooltipProvider, null,
        React.createElement(Toaster.Toaster),
        React.createElement(Router)
      )
    );
  }

  const container = document.getElementById("root");
  if (container) {
    const root = createRoot(container);
    root.render(React.createElement(App));
  }
}

// Initialize app
loadApp();