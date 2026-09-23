import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import EspacioSelectPage from './pages/EspacioSelectPage'
import DashboardPage from './pages/DashboardPage'
import InventarioPage from './pages/InventarioPage'
import ServiciosPage from './pages/ServiciosPage'
import ReportesPage from './pages/ReportesPage'
import PaquetesPage from './pages/PaquetesPage'
import TrazabilidadPage from './pages/TrazabilidadPage'
import CajaPage from './pages/CajaPage'
import VentasPage from './pages/VentasPage'
import Layout from './components/Layout'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-500">Cargando...</div>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/seleccionar-espacio" element={<PrivateRoute><EspacioSelectPage /></PrivateRoute>} />
      <Route path="/espacio/:espacioId" element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index element={<DashboardPage />} />
        <Route path="inventario" element={<InventarioPage />} />
        <Route path="servicios" element={<ServiciosPage />} />
        <Route path="reportes" element={<ReportesPage />} />
        <Route path="paquetes" element={<PaquetesPage />} />
        <Route path="ventas" element={<VentasPage />} />
        <Route path="caja" element={<CajaPage />} />
        <Route path="trazabilidad" element={<TrazabilidadPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
