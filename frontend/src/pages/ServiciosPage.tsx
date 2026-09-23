import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { useTerminos } from '../terminologia'
import { Plus, X, Trash2, ChevronDown, ChevronUp, Pencil, Check, AlertCircle } from 'lucide-react'

function cop(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

type ItemEdit = { insumo_id: string; cantidad: string; notas: string }

function ServicioCard({ srv, espacioId, insumos }: { srv: any; espacioId: string; insumos: any[] }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const qc = useQueryClient()

  // --- estado del formulario ---
  const costoBase = srv.insumos.reduce((acc: number, si: any) => acc + (si.costo_total || 0), 0)
  const [items, setItems] = useState<ItemEdit[]>([])
  const [margen, setMargen] = useState('')
  const [precioSugerido, setPrecioSugerido] = useState('')
  const [precioMercado, setPrecioMercado] = useState('')
  const [lastEditado, setLastEditado] = useState<'margen' | 'precio'>('margen')

  // costo recalculado según insumos editados
  const costoEditado = items.reduce((acc, it) => {
    const ins = insumos.find((i: any) => i.id === it.insumo_id)
    if (!ins) return acc
    const precio = ins.precio_minimo ?? 0
    return acc + precio * (parseFloat(it.cantidad) || 0)
  }, 0)

  function abrirEdicion() {
    setSaveError(null)
    setItems(srv.insumos.map((si: any) => ({
      insumo_id: si.insumo_id,
      cantidad: String(si.cantidad),
      notas: si.notas ?? '',
    })))
    const m = Number(srv.margen_ganancia_pct || 40)
    setMargen(String(m))
    setPrecioSugerido(String(Math.round(costoBase * (1 + m / 100))))
    setPrecioMercado(srv.precio_mercado_referencia ? String(Math.round(Number(srv.precio_mercado_referencia))) : '')
    setLastEditado('margen')
    setEditing(true)
    setExpanded(true)
  }

  function cancelar() {
    setEditing(false)
  }

  // Cuando cambia el margen → recalcula precio
  function handleMargenChange(val: string) {
    setMargen(val)
    setLastEditado('margen')
    const m = parseFloat(val) || 0
    setPrecioSugerido(String(Math.round(costoEditado * (1 + m / 100))))
  }

  // Cuando cambia el precio → recalcula margen
  function handlePrecioChange(val: string) {
    setPrecioSugerido(val)
    setLastEditado('precio')
    const p = parseFloat(val) || 0
    if (costoEditado > 0) {
      setMargen(String(((p / costoEditado - 1) * 100).toFixed(1)))
    }
  }

  // Cuando cambian los insumos → recalcula según lastEditado
  useEffect(() => {
    if (!editing) return
    if (lastEditado === 'margen') {
      const m = parseFloat(margen) || 0
      setPrecioSugerido(String(Math.round(costoEditado * (1 + m / 100))))
    } else {
      const p = parseFloat(precioSugerido) || 0
      if (costoEditado > 0) {
        setMargen(String(((p / costoEditado - 1) * 100).toFixed(1)))
      }
    }
  }, [costoEditado])

  const [saveError, setSaveError] = useState<string | null>(null)
  const updateMut = useMutation({
    mutationFn: (data: any) => api.put(`/servicios/${srv.id}`, data),
    onSuccess: () => {
      setSaveError(null)
      qc.invalidateQueries({ queryKey: ['servicios', espacioId] })
      setEditing(false)
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        setSaveError(detail.map((d: any) => `${d.loc?.join('.')} — ${d.msg}`).join('; '))
      } else if (typeof detail === 'string') {
        setSaveError(detail)
      } else {
        setSaveError('Error al guardar. Verifica los datos e intenta de nuevo.')
      }
    },
  })

  const deleteMut = useMutation({
    mutationFn: () => api.put(`/servicios/${srv.id}`, { activo: false }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['servicios', espacioId] }),
  })

  function guardar() {
    updateMut.mutate({
      margen_ganancia_pct: parseFloat(margen) || 0,
      precio_mercado_referencia: precioMercado ? parseFloat(precioMercado) : null,
      insumos: items
        .filter(it => it.insumo_id && parseFloat(it.cantidad) > 0)
        .map(it => ({
          insumo_id: it.insumo_id,
          cantidad: parseFloat(it.cantidad),
          notas: it.notas || null,
        })),
    })
  }

  function addItem() {
    setItems([...items, { insumo_id: '', cantidad: '1', notas: '' }])
  }

  function removeItem(i: number) {
    setItems(items.filter((_, idx) => idx !== i))
  }

  function setItemField(i: number, field: string, val: string) {
    const updated = [...items]
    updated[i] = { ...updated[i], [field]: val }
    setItems(updated)
  }

  // --- vista normal ---
  const costoVista = costoBase
  const margenVista = Number(srv.margen_ganancia_pct || 40)
  const precioVista = costoVista * (1 + margenVista / 100)
  const hasIncomplete = srv.insumos.some((si: any) => si.costo_unitario === 0)

  return (
    <div className={`card space-y-3 ${editing ? 'ring-2 ring-brand-400' : ''}`}>
      {/* Cabecera */}
      <div className="flex items-start justify-between">
        <div
          className="flex-1 min-w-0 cursor-pointer"
          onClick={() => { if (!editing) setExpanded(!expanded) }}
        >
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-gray-900">{srv.nombre}</h3>
            {hasIncomplete && !editing && (
              <span className="badge bg-yellow-100 text-yellow-700 flex items-center gap-1">
                <AlertCircle size={11} /> Sin precio
              </span>
            )}
          </div>
          {srv.descripcion && <p className="text-xs text-gray-500 mt-0.5">{srv.descripcion}</p>}
        </div>

        <div className="flex items-center gap-3 ml-4 flex-shrink-0">
          {!editing && (
            <>
              <div className="text-right hidden sm:block">
                <div className="text-xs text-gray-500">Costo insumos</div>
                <div className="font-semibold text-gray-900 text-sm">{costoVista > 0 ? cop(costoVista) : '—'}</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Precio sugerido</div>
                <div className="font-semibold text-brand-700">{precioVista > 0 ? cop(precioVista) : '—'}</div>
              </div>
              <button
                className="p-1.5 rounded-lg text-gray-400 hover:text-brand-600 hover:bg-brand-50 transition-colors"
                onClick={() => abrirEdicion()}
                title="Editar servicio"
              >
                <Pencil size={16} />
              </button>
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-gray-400"
              >
                {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
            </>
          )}
          {editing && (
            <span className="text-xs font-medium text-brand-600 bg-brand-50 px-2 py-1 rounded-lg">Editando</span>
          )}
        </div>
      </div>

      {/* Vista expandida normal */}
      {expanded && !editing && (
        <div className="border-t border-gray-100 pt-3 space-y-3">
          <div>
            <div className="text-xs font-medium text-gray-600 mb-2">Insumos del procedimiento</div>
            <div className="space-y-1">
              {srv.insumos.map((si: any) => (
                <div key={si.id} className="flex items-center gap-2 text-xs bg-gray-50 rounded px-3 py-1.5">
                  <span className="flex-1 text-gray-700">{si.insumo_nombre}</span>
                  <span className="text-gray-500">x{Number(si.cantidad).toFixed(2)}</span>
                  <span className="text-gray-500 hidden sm:inline">@ {si.costo_unitario > 0 ? cop(si.costo_unitario) : '?'}/u</span>
                  <span className={`font-medium w-24 text-right ${si.costo_total > 0 ? 'text-brand-700' : 'text-yellow-600'}`}>
                    {si.costo_total > 0 ? cop(si.costo_total) : '— sin precio'}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-brand-50 rounded-lg p-3 grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
            <div>
              <div className="text-xs text-gray-500">Costo insumos</div>
              <div className="font-semibold">{cop(costoVista)}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Margen ({margenVista}%)</div>
              <div className="font-semibold">{cop(precioVista - costoVista)}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Precio sugerido</div>
              <div className="font-bold text-brand-700 text-base">{cop(precioVista)}</div>
            </div>
            {srv.precio_mercado_referencia && (
              <div className="col-span-2 md:col-span-3">
                <div className="text-xs text-gray-500">Precio de mercado ref.</div>
                <div className="font-medium text-green-700">{cop(Number(srv.precio_mercado_referencia))}</div>
              </div>
            )}
          </div>
          <div className="flex justify-end">
            <button
              className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
              onClick={() => { if (confirm('¿Eliminar este servicio?')) deleteMut.mutate() }}
            >
              <Trash2 size={13} /> Eliminar
            </button>
          </div>
        </div>
      )}

      {/* Modo edición inline */}
      {editing && (
        <div className="border-t border-brand-100 pt-4 space-y-4">

          {/* Insumos editables */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-700">Insumos del procedimiento</span>
              <button type="button" className="text-xs text-brand-600 hover:underline" onClick={addItem}>
                + Agregar insumo
              </button>
            </div>
            <div className="space-y-2">
              {items.map((it, i) => {
                const ins = insumos.find((x: any) => x.id === it.insumo_id)
                const costoUnit = ins?.precio_minimo ?? 0
                const costoItem = costoUnit * (parseFloat(it.cantidad) || 0)
                return (
                  <div key={i} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
                    <select
                      className="input text-xs py-1 flex-1"
                      value={it.insumo_id}
                      onChange={(e) => setItemField(i, 'insumo_id', e.target.value)}
                    >
                      <option value="">Seleccionar insumo...</option>
                      {insumos.map((ins: any) => (
                        <option key={ins.id} value={ins.id}>{ins.nombre}</option>
                      ))}
                    </select>
                    <input
                      className="input text-xs py-1 w-20 text-center"
                      type="number"
                      step="0.0001"
                      min="0"
                      placeholder="Cant."
                      value={it.cantidad}
                      onChange={(e) => setItemField(i, 'cantidad', e.target.value)}
                    />
                    <span className="text-xs text-brand-700 font-medium w-20 text-right flex-shrink-0">
                      {costoItem > 0 ? cop(costoItem) : '—'}
                    </span>
                    <button type="button" onClick={() => removeItem(i)} className="text-gray-400 hover:text-red-500 flex-shrink-0">
                      <X size={15} />
                    </button>
                  </div>
                )
              })}
              {items.length === 0 && (
                <p className="text-xs text-gray-400 py-2 text-center">Sin insumos. Agrega el primero.</p>
              )}
            </div>
          </div>

          {/* Resumen financiero editable */}
          <div className="bg-brand-50 rounded-xl p-4 space-y-3">
            <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Precio y margen</div>

            {/* Costo (solo lectura) */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Costo de insumos</span>
              <span className="font-semibold text-gray-900">{costoEditado > 0 ? cop(costoEditado) : '—'}</span>
            </div>

            {/* Margen editable */}
            <div className="flex items-center justify-between gap-3">
              <span className="text-sm text-gray-600 flex-shrink-0">Margen de ganancia %</span>
              <div className="flex items-center gap-1">
                <input
                  type="number"
                  className="input text-sm py-1 w-24 text-right"
                  value={margen}
                  onChange={(e) => handleMargenChange(e.target.value)}
                  step="0.5"
                />
                <span className="text-sm text-gray-500">%</span>
              </div>
            </div>

            {/* Precio sugerido editable */}
            <div className="flex items-center justify-between gap-3 border-t border-brand-200 pt-3">
              <span className="text-sm font-medium text-gray-700 flex-shrink-0">Precio sugerido (COP)</span>
              <input
                type="number"
                className="input text-sm py-1 w-36 text-right font-bold text-brand-700"
                value={precioSugerido}
                onChange={(e) => handlePrecioChange(e.target.value)}
              />
            </div>

            {/* Precio de mercado referencia */}
            <div className="flex items-center justify-between gap-3">
              <span className="text-sm text-gray-500 flex-shrink-0">Precio de mercado ref. (COP)</span>
              <input
                type="number"
                className="input text-sm py-1 w-36 text-right"
                placeholder="Opcional"
                value={precioMercado}
                onChange={(e) => setPrecioMercado(e.target.value)}
              />
            </div>

            {/* Resumen calculado */}
            {costoEditado > 0 && parseFloat(precioSugerido) > 0 && (
              <div className="flex items-center justify-between text-xs text-gray-500 border-t border-brand-200 pt-2">
                <span>Ganancia por procedimiento</span>
                <span className="font-semibold text-green-700">
                  {cop(parseFloat(precioSugerido) - costoEditado)}
                </span>
              </div>
            )}
          </div>

          {/* Botones */}
          {saveError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {saveError}
            </div>
          )}
          <div className="flex gap-3">
            <button
              className="btn-primary flex items-center gap-2 flex-1"
              onClick={guardar}
              disabled={updateMut.isPending}
            >
              <Check size={15} />
              {updateMut.isPending ? 'Guardando...' : 'Guardar cambios'}
            </button>
            <button className="btn-secondary" onClick={cancelar}>
              Cancelar
            </button>
            <button
              className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1 px-2"
              onClick={() => { if (confirm('¿Eliminar este servicio?')) deleteMut.mutate() }}
            >
              <Trash2 size={13} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function NuevoServicioModal({ espacioId, insumos, onClose }: { espacioId: string; insumos: any[]; onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    nombre: '', descripcion: '', precio_mercado_referencia: '', margen_ganancia_pct: '40',
  })
  const [items, setItems] = useState<ItemEdit[]>([])

  const costoTotal = items.reduce((acc, it) => {
    const ins = insumos.find((i: any) => i.id === it.insumo_id)
    return acc + (ins?.precio_minimo ?? 0) * (parseFloat(it.cantidad) || 0)
  }, 0)
  const precioSugerido = costoTotal * (1 + (parseFloat(form.margen_ganancia_pct) || 0) / 100)

  const mut = useMutation({
    mutationFn: (data: any) => api.post(`/espacios/${espacioId}/servicios`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['servicios', espacioId] }); onClose() },
  })

  function addItem() { setItems([...items, { insumo_id: '', cantidad: '1', notas: '' }]) }
  function removeItem(i: number) { setItems(items.filter((_, idx) => idx !== i)) }
  function setItemField(i: number, field: string, val: string) {
    const u = [...items]; u[i] = { ...u[i], [field]: val }; setItems(u)
  }

  function submit(e: React.FormEvent) {
    e.preventDefault()
    mut.mutate({
      nombre: form.nombre,
      descripcion: form.descripcion || null,
      precio_mercado_referencia: form.precio_mercado_referencia ? parseFloat(form.precio_mercado_referencia) : null,
      margen_ganancia_pct: parseFloat(form.margen_ganancia_pct) || 40,
      insumos: items.filter(it => it.insumo_id && parseFloat(it.cantidad) > 0).map(it => ({
        insumo_id: it.insumo_id,
        cantidad: parseFloat(it.cantidad),
        notas: it.notas || null,
      })),
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Nuevo servicio</h2>
          <button onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <form onSubmit={submit} className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Nombre del servicio *</label>
            <input className="input" required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Descripción</label>
            <textarea className="input h-16 resize-none" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Precio de mercado ref.</label>
              <input className="input" type="number" placeholder="Opcional" value={form.precio_mercado_referencia} onChange={(e) => setForm({ ...form, precio_mercado_referencia: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Margen de ganancia %</label>
              <input className="input" type="number" value={form.margen_ganancia_pct} onChange={(e) => setForm({ ...form, margen_ganancia_pct: e.target.value })} />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-gray-700">Insumos</label>
              <button type="button" className="text-xs text-brand-600 hover:underline" onClick={addItem}>+ Agregar</button>
            </div>
            {items.map((it, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <select className="input text-xs py-1 flex-1" value={it.insumo_id} onChange={(e) => setItemField(i, 'insumo_id', e.target.value)}>
                  <option value="">Insumo...</option>
                  {insumos.map((ins: any) => <option key={ins.id} value={ins.id}>{ins.nombre}</option>)}
                </select>
                <input className="input text-xs py-1 w-16" type="number" placeholder="Cant." step="0.0001" value={it.cantidad} onChange={(e) => setItemField(i, 'cantidad', e.target.value)} />
                <button type="button" onClick={() => removeItem(i)} className="text-gray-400 hover:text-red-500"><X size={16} /></button>
              </div>
            ))}
          </div>

          {costoTotal > 0 && (
            <div className="bg-brand-50 rounded-lg p-3 text-sm space-y-1">
              <div className="flex justify-between"><span className="text-gray-500">Costo estimado</span><span className="font-medium">{cop(costoTotal)}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Precio sugerido ({form.margen_ganancia_pct}%)</span><span className="font-bold text-brand-700">{cop(precioSugerido)}</span></div>
            </div>
          )}

          {mut.isError && <p className="text-sm text-red-600">Error al guardar.</p>}
          <div className="flex gap-3 pt-2">
            <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
              {mut.isPending ? 'Guardando...' : 'Guardar servicio'}
            </button>
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function ServiciosPage() {
  const { espacioId } = useParams()
  const t = useTerminos()
  const [showModal, setShowModal] = useState(false)

  const { data: servicios = [], isLoading } = useQuery({
    queryKey: ['servicios', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/servicios`).then((r) => r.data),
  })

  const { data: insumos = [] } = useQuery({
    queryKey: ['insumos', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/insumos`).then((r) => r.data),
  })

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.servicios}</h1>
          <p className="text-sm text-gray-500 mt-0.5">{servicios.length} {t.descripcionServicios}</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowModal(true)}>
          <Plus size={16} />
          <span className="hidden sm:inline">{t.nuevoServicio}</span>
        </button>
      </div>

      {isLoading && <div className="text-center py-8 text-gray-500">Cargando...</div>}

      <div className="space-y-3">
        {servicios.map((srv: any) => (
          <ServicioCard key={srv.id} srv={srv} espacioId={espacioId!} insumos={insumos} />
        ))}
        {!isLoading && servicios.length === 0 && (
          <div className="card text-center py-10 text-gray-400">
            {`No hay ${t.descripcionServicios} registrados. Crea el primero.`}
          </div>
        )}
      </div>

      {showModal && (
        <NuevoServicioModal espacioId={espacioId!} insumos={insumos} onClose={() => setShowModal(false)} />
      )}
    </div>
  )
}
