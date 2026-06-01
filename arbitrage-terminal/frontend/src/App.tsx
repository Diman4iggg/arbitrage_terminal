import { Navigate, Route, Routes } from "react-router-dom"

import { AppShell } from "./components/AppShell"
import { Charts } from "./pages/Charts"
import { Dashboard } from "./pages/Dashboard"
import { Exchanges } from "./pages/Exchanges"
import { Opportunities } from "./pages/Opportunities"
import { Settings } from "./pages/Settings"

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/opportunities" element={<Opportunities />} />
        <Route path="/exchanges" element={<Exchanges />} />
        <Route path="/charts" element={<Charts />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  )
}
