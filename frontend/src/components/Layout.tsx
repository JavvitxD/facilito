import { Outlet, NavLink, useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LayoutDashboard, Package, Stethoscope, BarChart3, LogOut, ChevronLeft, Menu, X, Layers, History, Wallet, ShieldCheck, ShoppingCart } from 'lucide-react'
import { useState, useEffect } from 'react'
import CambiarPasswordModal from './CambiarPasswordModal'
import BotonRestaurarDemo from './BotonRestaurarDemo'

export default function Layout() {
  const { user, logout } = useAuth()
  const { espacioId } = useParams()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [espacioNombre, setEspacioNombre] = useState('')
  const [cambiandoPassword, setCambiandoPassword] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('espacio')
    if (stored) {
      try { setEspacioNombre(JSON.parse(stored).nombre) } catch {}
    }
  }, [])

  const base = `/espacio/${espacioId}`
  const nav = [
    { to: base, label: 'Dashboard', icon: LayoutDashboard, end: true },
    { to: `${base}/inventario`, label: 'Inventario', icon: Package },
    { to: `${base}/servicios`, label: 'Servicios', icon: Stethoscope },
    { to: `${base}/paquetes`, label: 'Paquetes', icon: Layers },
    { to: `${base}/ventas`, label: 'Ventas', icon: ShoppingCart },
    { to: `${base}/caja`, label: 'Caja', icon: Wallet },
    { to: `${base}/reportes`, label: 'Reportes', icon: BarChart3 },
    { to: `${base}/trazabilidad`, label: 'Trazabilidad', icon: History },
  ]

  const Sidebar = () => (
    <div className="flex flex-col h-full">
      <div className="p-5 border-b border-gray-200">
        <div className="text-xs font-semibold text-brand-600 uppercase tracking-wider mb-1">INV DOC</div>
        <div className="font-semibold text-gray-900 text-sm leading-tight">{espacioNombre || 'Espacio'}</div>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {nav.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-gray-200 space-y-1">
        {user?.email && (
          <div className="px-3 pb-1 text-xs text-gray-400 truncate" title={user.email}>
            {user.email}
          </div>
        )}
        <button
          onClick={() => { navigate('/seleccionar-espacio'); setSidebarOpen(false) }}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 w-full"
        >
          <ChevronLeft size={18} />
          Cambiar espacio
        </button>
        <button
          onClick={() => { setCambiandoPassword(true); setSidebarOpen(false) }}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 w-full"
        >
          <ShieldCheck size={18} />
          Cambiar contraseña
        </button>
        <BotonRestaurarDemo />
        <button
          onClick={() => { logout(); navigate('/login') }}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 w-full"
        >
          <LogOut size={18} />
          Cerrar sesión
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-56 flex-shrink-0 flex-col bg-white border-r border-gray-200">
        <Sidebar />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setSidebarOpen(false)} />
          <aside className="relative w-56 h-full bg-white border-r border-gray-200 flex flex-col z-50">
            <button className="absolute top-3 right-3 p-1" onClick={() => setSidebarOpen(false)}>
              <X size={20} />
            </button>
            <Sidebar />
          </aside>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile topbar */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 bg-white border-b border-gray-200">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu size={22} className="text-gray-600" />
          </button>
          <span className="font-semibold text-gray-900 text-sm">{espacioNombre}</span>
        </div>
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>

      {cambiandoPassword && (
        <CambiarPasswordModal onClose={() => setCambiandoPassword(false)} />
      )}
    </div>
  )
}
