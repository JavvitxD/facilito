import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { UserCircle, LogOut } from 'lucide-react'

export default function EspacioSelectPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const { data: empresas } = useQuery({
    queryKey: ['empresas'],
    queryFn: () => api.get('/empresas').then((r) => r.data),
  })

  const empresa = empresas?.[0]

  const { data: espacios } = useQuery({
    queryKey: ['espacios', empresa?.id],
    queryFn: () => api.get(`/empresas/${empresa.id}/espacios`).then((r) => r.data),
    enabled: !!empresa?.id,
  })

  useEffect(() => {
    if (espacios?.length === 1) {
      localStorage.setItem('espacio', JSON.stringify(espacios[0]))
      navigate(`/espacio/${espacios[0].id}`, { replace: true })
    }
  }, [espacios])

  function selectEspacio(esp: { id: string; nombre: string }) {
    localStorage.setItem('espacio', JSON.stringify(esp))
    navigate(`/espacio/${esp.id}`)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 to-brand-100 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Seleccionar Consultorio</h1>
          <p className="text-sm text-gray-500 mt-1">{empresa?.nombre}</p>
        </div>

        <div className="space-y-3">
          {!espacios && (
            <div className="text-center text-gray-500 py-8">Cargando espacios...</div>
          )}
          {espacios?.map((esp: { id: string; nombre: string; especialidad?: string }) => (
            <button
              key={esp.id}
              onClick={() => selectEspacio(esp)}
              className="w-full card shadow-sm hover:shadow-md hover:border-brand-300 transition-all text-left flex items-center gap-4 cursor-pointer"
            >
              <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
                <UserCircle size={28} className="text-brand-600" />
              </div>
              <div>
                <div className="font-semibold text-gray-900">{esp.nombre}</div>
                {esp.especialidad && <div className="text-sm text-gray-500">{esp.especialidad}</div>}
              </div>
            </button>
          ))}
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="text-sm text-gray-500 hover:text-red-600 flex items-center gap-1.5 mx-auto"
          >
            <LogOut size={14} />
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  )
}
