import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { Download, TrendingUp, TrendingDown, Minus } from 'lucide-react'

function cop(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

export default function ReportesPage() {
  const { espacioId } = useParams()

  const { data: servicios = [], isLoading } = useQuery({
    queryKey: ['servicios', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/servicios`).then((r) => r.data),
  })

  const reporte = servicios.map((s: any) => {
    const costo = s.insumos.reduce((acc: number, si: any) => acc + (si.costo_total || 0), 0)
    const margen = Number(s.margen_ganancia_pct || 30)
    const precioSugerido = costo * (1 + margen / 100)
    const precioMercado = s.precio_mercado_referencia ? Number(s.precio_mercado_referencia) : null
    const margenReal = precioMercado && costo > 0 ? ((precioMercado - costo) / costo * 100) : null
    return { ...s, costo, precioSugerido, precioMercado, margenReal }
  })

  async function downloadExcel() {
    const resp = await api.get(`/espacios/${espacioId}/reporte-costos?formato=excel`, { responseType: 'blob' })
    const url = URL.createObjectURL(resp.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'reporte_costos.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reportes de Costos</h1>
          <p className="text-sm text-gray-500 mt-0.5">Análisis de rentabilidad por servicio</p>
        </div>
        <button className="btn-secondary flex items-center gap-2" onClick={downloadExcel}>
          <Download size={16} />
          Exportar Excel
        </button>
      </div>

      {isLoading && <div className="text-center py-8 text-gray-500">Cargando...</div>}

      {!isLoading && (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Servicio</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Costo insumos</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Margen</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Precio sugerido</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Precio mercado</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600 hidden lg:table-cell">Margen real</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {reporte.map((r: any) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{r.nombre}</div>
                    {r.insumos.some((si: any) => si.costo_unitario === 0) && (
                      <div className="text-xs text-yellow-600">⚠ Insumos sin precio</div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right font-medium text-gray-900">
                    {r.costo > 0 ? cop(r.costo) : '—'}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600">{Number(r.margen_ganancia_pct)}%</td>
                  <td className="px-4 py-3 text-right font-semibold text-brand-700">
                    {r.precioSugerido > 0 ? cop(r.precioSugerido) : '—'}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-700 hidden md:table-cell">
                    {r.precioMercado ? cop(r.precioMercado) : '—'}
                  </td>
                  <td className="px-4 py-3 text-right hidden lg:table-cell">
                    {r.margenReal != null ? (
                      <span className={`flex items-center justify-end gap-1 font-medium ${r.margenReal >= 30 ? 'text-green-600' : r.margenReal >= 0 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {r.margenReal >= 30 ? <TrendingUp size={14} /> : r.margenReal >= 0 ? <Minus size={14} /> : <TrendingDown size={14} />}
                        {r.margenReal.toFixed(1)}%
                      </span>
                    ) : '—'}
                  </td>
                </tr>
              ))}
              {reporte.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">Sin datos</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Comparador de proveedores por insumo — resumen */}
      <div>
        <h2 className="text-base font-semibold text-gray-900 mb-3">Nota sobre datos pendientes</h2>
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-sm text-yellow-800 space-y-1">
          <p className="font-medium">Los siguientes servicios tienen insumos sin confirmar:</p>
          <ul className="list-disc list-inside space-y-0.5 text-yellow-700 text-xs">
            <li>Lifting de Oreja — cantidades de gasas, pañitos, lidocaína y algodón</li>
            <li>Lifting de Nariz — cantidades de gasas, pañitos y lidocaína</li>
            <li>Colocación de Hilos Extensores — tipo/marca/precio de hilos y cantidad de lidocaína</li>
            <li>Aplicación de Botox — marca y dosis de toxina botulínica, pañitos, gauge de aguja</li>
          </ul>
          <p className="text-xs mt-2">Los costos de estos servicios son estimados hasta que se completen los datos.</p>
        </div>
      </div>
    </div>
  )
}
