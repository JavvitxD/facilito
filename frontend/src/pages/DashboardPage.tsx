import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { AlertTriangle, Package, Stethoscope, TrendingUp, Layers } from 'lucide-react'

function cop(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

export default function DashboardPage() {
  const { espacioId } = useParams()

  const { data: alertas } = useQuery({
    queryKey: ['alertas', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/alertas-stock`).then((r) => r.data),
  })

  const { data: insumos } = useQuery({
    queryKey: ['insumos', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/insumos`).then((r) => r.data),
  })

  const { data: servicios } = useQuery({
    queryKey: ['servicios', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/servicios`).then((r) => r.data),
  })

  const { data: paquetes } = useQuery({
    queryKey: ['paquetes', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/paquetes`).then((r) => r.data),
  })

  const espacioNombre = (() => {
    try { return JSON.parse(localStorage.getItem('espacio') || '{}').nombre || '' } catch { return '' }
  })()

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-0.5">{espacioNombre}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-brand-100 flex items-center justify-center">
            <Package size={20} className="text-brand-600" />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{insumos?.length ?? '—'}</div>
            <div className="text-xs text-gray-500">Insumos</div>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
            <Stethoscope size={20} className="text-green-600" />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{servicios?.length ?? '—'}</div>
            <div className="text-xs text-gray-500">Servicios</div>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
            <Layers size={20} className="text-purple-600" />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{paquetes?.length ?? '—'}</div>
            <div className="text-xs text-gray-500">Paquetes</div>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
            <AlertTriangle size={20} className="text-red-500" />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{alertas?.length ?? '—'}</div>
            <div className="text-xs text-gray-500">Alertas de stock</div>
          </div>
        </div>
      </div>

      {/* Alertas */}
      {alertas && alertas.length > 0 && (
        <div>
          <h2 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-500" />
            Insumos bajo stock mínimo
          </h2>
          <div className="space-y-2">
            {alertas.map((ins: any) => (
              <div key={ins.id} className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 flex items-center justify-between">
                <div>
                  <span className="font-medium text-red-800 text-sm">{ins.nombre}</span>
                  <span className="text-red-600 text-xs ml-2">
                    Stock: {Number(ins.stock_actual).toFixed(0)} / Mín: {Number(ins.stock_minimo).toFixed(0)} {ins.unidad_medida}
                  </span>
                </div>
                <Link to={`/espacio/${espacioId}/inventario`} className="text-xs text-red-600 hover:underline">
                  Ver →
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Servicios resumen */}
      {servicios && servicios.length > 0 && (
        <div>
          <h2 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <TrendingUp size={16} className="text-brand-600" />
            Resumen de servicios
          </h2>
          <div className="card p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Servicio</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">Insumos</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-600">Costo est.</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {servicios.map((s: any) => {
                  const costo = s.insumos.reduce((acc: number, si: any) => acc + (si.costo_total || 0), 0)
                  return (
                    <tr key={s.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{s.nombre}</td>
                      <td className="px-4 py-3 text-right text-gray-500 hidden sm:table-cell">{s.insumos.length}</td>
                      <td className="px-4 py-3 text-right font-medium text-brand-700">{costo > 0 ? cop(costo) : '—'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
