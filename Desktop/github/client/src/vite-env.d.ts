/// <reference types="vite/client" />

declare global {
  interface Window {
    __vite_plugin_react_preamble_installed__?: boolean;
  }
}

export {};