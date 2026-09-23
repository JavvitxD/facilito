import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { useTerminos } from '../terminologia'
import { Plus, X, Trash2, ChevronDown, ChevronUp, Package, Pencil } from 'lucide-react'

function cop(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

function PaqueteModal({
  espacioId,
  servicios,
  inicial,
  onClose,
}: {
  espacioId: string
  servicios: any[]
  inicial?: any
  onClose: () => void
}) {
  const qc = useQueryClient()
  const esEdicion = !!inicial

  const [nombre, setNombre] = useState(inicial?.nombre ?? '')
  const [descripcion, setDescripcion] = useState(inicial?.descripcion ?? '')
  const [seleccionados, setSeleccionados] = useState<string[]>(
    inicial?.servicios?.map((s: any) => s.id) ?? []
  )

  const mut = useMutation({
    mutationFn: (data: any) =>
      esEdicion
        ? api.put(`/paquetes/${inicial.id}`, data)
        : api.post(`/espacios/${espacioId}/paquetes`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['paquetes', espacioId] }); onClose() },
  })

  function toggleServicio(id: string) {
    setSeleccionados((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    )
  }

  function submit(e: React.FormEvent) {
    e.preventDefault()
    mut.mutate({
      nombre,
      descripcion: descripcion || null,
      servicios: seleccionados.map((id) => ({ servicio_id: id })),
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">{esEdicion ? 'Editar paquete' : 'Nuevo paquete'}</h2>
          <button onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <form onSubmit={submit} className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Nombre del paquete *</label>
            <input className="input" required value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Ej: Glow Reset" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Descripción</label>
            <textarea className="input h-16 resize-none" value={descripcion} onChange={(e) => setDescripcion(e.target.value)} placeholder="Descripción del paquete..." />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Servicios del paquete
              {seleccionados.length > 0 && <span className="ml-2 text-brand-600">({seleccionados.length} seleccionados)</span>}
            </label>
            <div className="space-y-1 max-h-60 overflow-y-auto border border-gray-200 rounded-lg p-2">
              {servicios.map((srv: any) => (
                <label
                  key={srv.id}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-50 ${
                    seleccionados.includes(srv.id) ? 'bg-brand-50 border border-brand-200' : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    className="accent-brand-600"
                    checked={seleccionados.includes(srv.id)}
                    onChange={() => toggleServicio(srv.id)}
                  />
                  <span className="text-sm text-gray-800 flex-1">{srv.nombre}</span>
                  <span className="text-xs text-gray-400">
                    {srv.insumos?.reduce((acc: number, si: any) => acc + (si.costo_total || 0), 0) > 0
                      ? cop(srv.insumos.reduce((acc: number, si: any) => acc + (si.costo_total || 0), 0))
                      : '—'}
                  </span>
                </label>
              ))}
              {servicios.length === 0 && <p className="text-xs text-gray-400 p-2">No hay servicios disponibles.</p>}
            </div>
          </div>

          {mut.isError && <p className="text-sm text-red-600">Error al guardar.</p>}
          <div className="flex gap-3 pt-2">
            <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
              {mut.isPending ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Guardar paquete'}
            </button>
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function PaqueteCard({ pak, espacioId, servicios }: { pak: any; espacioId: string; servicios: any[] }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const qc = useQueryClient()

  const deleteMut = useMutation({
    mutationFn: () => api.put(`/paquetes/${pak.id}`, { activo: false }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['paquetes', espacioId] }),
  })

  const precioSugerido = pak.costo_total * 1.5

  return (
    <>
      <div className="card space-y-3">
        <div
          className="flex items-start justify-between cursor-pointer"
          onClick={() => setExpanded(!expanded)}
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="w-9 h-9 rounded-lg bg-brand-100 flex items-center justify-center flex-shrink-0">
              <Package size={18} className="text-brand-600" />
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold text-gray-900">{pak.nombre}</h3>
              {pak.descripcion && <p className="text-xs text-gray-500 mt-0.5 truncate">{pak.descripcion}</p>}
            </div>
          </div>
          <div className="flex items-center gap-4 ml-4 flex-shrink-0">
            <div className="text-right hidden sm:block">
              <div className="text-xs text-gray-500">{pak.servicios.length} servicio{pak.servicios.length !== 1 ? 's' : ''}</div>
              <div className="text-xs text-gray-400">Costo: {pak.costo_total > 0 ? cop(pak.costo_total) : '—'}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Precio aprox.</div>
              <div className="font-semibold text-brand-700">{pak.costo_total > 0 ? cop(precioSugerido) : '—'}</div>
            </div>
            {expanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
          </div>
        </div>

        {expanded && (
          <div className="border-t border-gray-100 pt-3 space-y-3">
            <div>
              <div className="text-xs font-medium text-gray-600 mb-2">Servicios del paquete</div>
              <div className="space-y-1">
                {pak.servicios.map((srv: any) => (
                  <div key={srv.id} className="flex items-center justify-between text-xs bg-gray-50 rounded px-3 py-2">
                    <span className="text-gray-700 font-medium">{srv.nombre}</span>
                    <span className="text-brand-700 font-medium ml-4 flex-shrink-0">
                      {srv.costo_insumos > 0 ? cop(srv.costo_insumos) : '—'}
                    </span>
                  </div>
                ))}
                {pak.servicios.length === 0 && (
                  <p className="text-xs text-gray-400">Sin servicios asignados.</p>
                )}
              </div>
            </div>

            {pak.costo_total > 0 && (
              <div className="bg-brand-50 rounded-lg p-3 grid grid-cols-3 gap-3 text-sm">
                <div>
                  <div className="text-xs text-gray-500">Costo insumos</div>
                  <div className="font-semibold">{cop(pak.costo_total)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Margen 50%</div>
                  <div className="font-semibold">{cop(pak.costo_total * 0.5)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Precio sugerido</div>
                  <div className="font-bold text-brand-700">{cop(precioSugerido)}</div>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between">
              <button
                className="text-xs text-brand-600 hover:text-brand-800 flex items-center gap-1"
                onClick={() => setEditing(true)}
              >
                <Pencil size={13} /> Editar paquete
              </button>
              <button
                className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
                onClick={() => { if (confirm('¿Eliminar este paquete?')) deleteMut.mutate() }}
              >
                <Trash2 size={13} /> Eliminar
              </button>
            </div>
          </div>
        )}
      </div>

      {editing && (
        <PaqueteModal
          espacioId={espacioId}
          servicios={servicios}
          inicial={pak}
          onClose={() => setEditing(false)}
        />
      )}
    </>
  )
}

export default function PaquetesPage() {
  const { espacioId } = useParams()
  const t = useTerminos()
  const [showModal, setShowModal] = useState(false)

  const { data: paquetes = [], isLoading } = useQuery({
    queryKey: ['paquetes', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/paquetes`).then((r) => r.data),
  })

  const { data: servicios = [] } = useQuery({
    queryKey: ['servicios', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/servicios`).then((r) => r.data),
  })

  const costoTotal = paquetes.reduce((acc: number, p: any) => acc + (p.costo_total || 0), 0)

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Paquetes</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {paquetes.length} paquete{paquetes.length !== 1 ? 's' : ''} configurado{paquetes.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowModal(true)}>
          <Plus size={16} />
          <span className="hidden sm:inline">Nuevo paquete</span>
        </button>
      </div>

      {paquetes.length > 0 && (
        <div className="grid grid-cols-2 gap-4">
          <div className="card flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-brand-100 flex items-center justify-center">
              <Package size={20} className="text-brand-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{paquetes.length}</div>
              <div className="text-xs text-gray-500">Paquetes activos</div>
            </div>
          </div>
          <div className="card flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <span className="text-green-700 font-bold text-sm">$</span>
            </div>
            <div>
              <div className="text-xl font-bold text-gray-900">{cop(costoTotal)}</div>
              <div className="text-xs text-gray-500">Costo total en insumos</div>
            </div>
          </div>
        </div>
      )}

      {isLoading && <div className="text-center py-8 text-gray-500">Cargando...</div>}

      <div className="space-y-3">
        {paquetes.map((pak: any) => (
          <PaqueteCard key={pak.id} pak={pak} espacioId={espacioId!} servicios={servicios} />
        ))}
        {!isLoading && paquetes.length === 0 && (
          <div className="card text-center py-12 text-gray-400">
            <Package size={40} className="mx-auto mb-3 opacity-30" />
            <p className="font-medium">Sin paquetes configurados</p>
            <p className="text-sm mt-1">Agrupa servicios en paquetes para calcular costos combinados.</p>
            <button className="btn-primary mt-4" onClick={() => setShowModal(true)}>Crear primer paquete</button>
          </div>
        )}
      </div>

      {showModal && (
        <PaqueteModal espacioId={espacioId!} servicios={servicios} onClose={() => setShowModal(false)} />
      )}
    </div>
  )
}
