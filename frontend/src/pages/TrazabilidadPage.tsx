import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { Clock, Package, Stethoscope, ShoppingCart, Truck, Layers, Filter, ChevronDown, ChevronUp } from 'lucide-react'

const ENTIDAD_CONFIG: Record<string, { label: string; icon: any; color: string }> = {
  insumo:     { label: 'Insumo',     icon: Package,     color: 'bg-blue-100 text-blue-700' },
  precio:     { label: 'Precio',     icon: ShoppingCart, color: 'bg-yellow-100 text-yellow-700' },
  proveedor:  { label: 'Proveedor',  icon: Truck,       color: 'bg-purple-100 text-purple-700' },
  servicio:   { label: 'Servicio',   icon: Stethoscope, color: 'bg-green-100 text-green-700' },
  paquete:    { label: 'Paquete',    icon: Layers,      color: 'bg-pink-100 text-pink-700' },
}

const ACCION_CONFIG: Record<string, { label: string; dot: string }> = {
  crear:    { label: 'Creado',     dot: 'bg-green-500' },
  editar:   { label: 'Editado',    dot: 'bg-blue-500' },
  eliminar: { label: 'Eliminado',  dot: 'bg-red-500' },
}

function formatFecha(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatHora(iso: string) {
  const d = new Date(iso)
  return d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
}

function agruparPorFecha(registros: any[]) {
  const grupos: Record<string, any[]> = {}
  for (const r of registros) {
    const fecha = formatFecha(r.created_at)
    if (!grupos[fecha]) grupos[fecha] = []
    grupos[fecha].push(r)
  }
  return grupos
}

export default function TrazabilidadPage() {
  const { espacioId } = useParams()
  const [filtroEntidad, setFiltroEntidad] = useState('')
  const [filtroAccion, setFiltroAccion] = useState('')
  const [showFiltros, setShowFiltros] = useState(false)
  const [offset, setOffset] = useState(0)
  const LIMIT = 50

  const params = new URLSearchParams()
  if (filtroEntidad) params.set('entidad', filtroEntidad)
  if (filtroAccion) params.set('accion', filtroAccion)
  params.set('limit', String(LIMIT))
  params.set('offset', String(offset))

  const { data, isLoading } = useQuery({
    queryKey: ['auditoria', espacioId, filtroEntidad, filtroAccion, offset],
    queryFn: () => api.get(`/espacios/${espacioId}/auditoria?${params.toString()}`).then((r) => r.data),
  })

  const registros: any[] = data?.registros ?? []
  const total: number = data?.total ?? 0
  const grupos = agruparPorFecha(registros)

  function limpiarFiltros() {
    setFiltroEntidad('')
    setFiltroAccion('')
    setOffset(0)
  }

  const hayFiltros = filtroEntidad || filtroAccion

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Trazabilidad</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Historial de todos los cambios en el inventario
            {total > 0 && <span className="ml-1">· {total} registro{total !== 1 ? 's' : ''}</span>}
          </p>
        </div>
        <button
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium border transition-colors ${
            hayFiltros
              ? 'bg-brand-600 text-white border-brand-600'
              : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
          }`}
          onClick={() => setShowFiltros(!showFiltros)}
        >
          <Filter size={15} />
          Filtros
          {hayFiltros && <span className="bg-white/30 text-xs px-1.5 rounded-full">activos</span>}
          {showFiltros ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* Panel de filtros */}
      {showFiltros && (
        <div className="card flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-40">
            <label className="block text-xs font-medium text-gray-600 mb-1">Tipo de elemento</label>
            <select
              className="input"
              value={filtroEntidad}
              onChange={(e) => { setFiltroEntidad(e.target.value); setOffset(0) }}
            >
              <option value="">Todos</option>
              {Object.entries(ENTIDAD_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-40">
            <label className="block text-xs font-medium text-gray-600 mb-1">Acción</label>
            <select
              className="input"
              value={filtroAccion}
              onChange={(e) => { setFiltroAccion(e.target.value); setOffset(0) }}
            >
              <option value="">Todas</option>
              {Object.entries(ACCION_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
          </div>
          {hayFiltros && (
            <button className="btn-secondary text-sm" onClick={limpiarFiltros}>
              Limpiar filtros
            </button>
          )}
        </div>
      )}

      {isLoading && (
        <div className="py-16 text-center text-gray-500">Cargando historial...</div>
      )}

      {!isLoading && registros.length === 0 && (
        <div className="card py-16 text-center">
          <Clock size={40} className="mx-auto mb-3 text-gray-300" />
          <p className="font-medium text-gray-500">Sin registros aún</p>
          <p className="text-sm text-gray-400 mt-1">
            Los cambios en inventario, servicios y paquetes aparecerán aquí.
          </p>
        </div>
      )}

      {/* Timeline agrupada por fecha */}
      {Object.entries(grupos).map(([fecha, items]) => (
        <div key={fecha}>
          <div className="flex items-center gap-3 mb-3">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">{fecha}</div>
            <div className="flex-1 h-px bg-gray-200" />
          </div>
          <div className="space-y-2">
            {items.map((reg: any) => {
              const entidadConf = ENTIDAD_CONFIG[reg.entidad] ?? { label: reg.entidad, icon: Clock, color: 'bg-gray-100 text-gray-600' }
              const accionConf = ACCION_CONFIG[reg.accion] ?? { label: reg.accion, dot: 'bg-gray-400' }
              const Icon = entidadConf.icon

              return (
                <div key={reg.id} className="flex gap-3">
                  {/* Dot + línea */}
                  <div className="flex flex-col items-center pt-1.5 flex-shrink-0">
                    <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${accionConf.dot}`} />
                  </div>

                  {/* Contenido */}
                  <div className="bg-white border border-gray-100 rounded-xl px-4 py-3 flex-1 min-w-0 shadow-sm">
                    <div className="flex items-start justify-between gap-3 flex-wrap">
                      <div className="flex items-center gap-2 flex-wrap min-w-0">
                        <span className={`badge flex items-center gap-1 ${entidadConf.color}`}>
                          <Icon size={11} />
                          {entidadConf.label}
                        </span>
                        <span className={`badge ${
                          reg.accion === 'crear' ? 'bg-green-100 text-green-700' :
                          reg.accion === 'eliminar' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {accionConf.label}
                        </span>
                        <span className="font-medium text-gray-900 text-sm truncate">{reg.entidad_nombre}</span>
                      </div>
                      <span className="text-xs text-gray-400 flex-shrink-0 flex items-center gap-1">
                        <Clock size={11} />
                        {formatHora(reg.created_at)}
                      </span>
                    </div>
                    {reg.descripcion && (
                      <p className="text-xs text-gray-600 mt-1.5 leading-relaxed">{reg.descripcion}</p>
                    )}
                    {reg.usuario_email && (
                      <p className="text-xs text-gray-400 mt-1">{reg.usuario_email}</p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ))}

      {/* Paginación */}
      {total > LIMIT && (
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            className="btn-secondary text-sm"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - LIMIT))}
          >
            ← Más recientes
          </button>
          <span className="text-xs text-gray-500">
            {offset + 1}–{Math.min(offset + LIMIT, total)} de {total}
          </span>
          <button
            className="btn-secondary text-sm"
            disabled={offset + LIMIT >= total}
            onClick={() => setOffset(offset + LIMIT)}
          >
            Más antiguos →
          </button>
        </div>
      )}
    </div>
  )
}
