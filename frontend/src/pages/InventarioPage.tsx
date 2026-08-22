import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { Plus, Search, AlertTriangle, ChevronDown, ChevronUp, Pencil, Trash2, X, Check, Settings } from 'lucide-react'

function cop(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

const CATEGORIAS = ['medico', 'medicamento', 'aseo']
const CAT_LABELS: Record<string, string> = { medico: 'Médico', medicamento: 'Medicamento', aseo: 'Aseo' }
const CAT_COLORS: Record<string, string> = {
  medico: 'bg-blue-100 text-blue-700',
  medicamento: 'bg-purple-100 text-purple-700',
  aseo: 'bg-green-100 text-green-700',
}

function EditPrecioRow({ precio, espacioId, onDone }: { precio: any; espacioId: string; onDone: () => void }) {
  const [precioVal, setPrecioVal] = useState(String(precio.precio_presentacion))
  const [uds, setUds] = useState(String(precio.unidades_por_presentacion ?? ''))
  const [desc, setDesc] = useState(precio.descripcion_presentacion ?? '')
  const qc = useQueryClient()

  const mut = useMutation({
    mutationFn: (data: any) => api.put(`/precios/${precio.id}`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['insumos', espacioId] }); onDone() },
  })

  function submit() {
    mut.mutate({
      precio_presentacion: parseFloat(precioVal) || undefined,
      unidades_por_presentacion: uds ? parseInt(uds) : null,
      descripcion_presentacion: desc || null,
    })
  }

  return (
    <div className="bg-brand-50 border border-brand-200 rounded-lg p-2 space-y-2">
      <div className="grid grid-cols-2 gap-2">
        <input className="input text-xs py-1" placeholder="Precio presentación" type="number" value={precioVal} onChange={(e) => setPrecioVal(e.target.value)} />
        <input className="input text-xs py-1" placeholder="Uds por presentación" type="number" value={uds} onChange={(e) => setUds(e.target.value)} />
        <input className="input text-xs py-1 col-span-2" placeholder="Descripción (ej: Caja 100 uds)" value={desc} onChange={(e) => setDesc(e.target.value)} />
      </div>
      <div className="flex gap-2">
        <button className="btn-primary text-xs py-1 px-3" onClick={submit} disabled={mut.isPending}>Guardar</button>
        <button className="btn-secondary text-xs py-1 px-3" onClick={onDone}>Cancelar</button>
      </div>
    </div>
  )
}

function InsumoRow({ ins, espacioId, proveedores }: { ins: any; espacioId: string; proveedores: any[] }) {
  const [expanded, setExpanded] = useState(false)
  const [editingInfo, setEditingInfo] = useState(false)
  const [editingPrecioId, setEditingPrecioId] = useState<string | null>(null)
  const [stock, setStock] = useState(String(ins.stock_actual ?? 0))
  const [infoForm, setInfoForm] = useState({
    nombre: ins.nombre,
    categoria: ins.categoria ?? 'medico',
    unidad_medida: ins.unidad_medida ?? '',
    invima: ins.invima ?? '',
    stock_minimo: String(ins.stock_minimo ?? 0),
  })
  const qc = useQueryClient()

  const updateMut = useMutation({
    mutationFn: (data: any) => api.put(`/insumos/${ins.id}`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['insumos', espacioId] }); setEditingInfo(false) },
  })

  const deleteMut = useMutation({
    mutationFn: () => api.delete(`/insumos/${ins.id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['insumos', espacioId] }),
  })

  const addPrecioMut = useMutation({
    mutationFn: (data: any) => api.post(`/insumos/${ins.id}/precios`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['insumos', espacioId] }),
  })

  const deletePrecioMut = useMutation({
    mutationFn: (precioId: string) => api.delete(`/precios/${precioId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['insumos', espacioId] }),
  })

  return (
    <>
      <tr
        className={`hover:bg-gray-50 cursor-pointer ${ins.alerta_stock ? 'bg-red-50' : ''}`}
        onClick={() => { if (!editingInfo) setExpanded(!expanded) }}
      >
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            {ins.alerta_stock && <AlertTriangle size={14} className="text-red-500 flex-shrink-0" />}
            <span className="font-medium text-gray-900 text-sm">{ins.nombre}</span>
          </div>
          {ins.invima && <div className="text-xs text-gray-400 mt-0.5">INVIMA: {ins.invima}</div>}
        </td>
        <td className="px-4 py-3 hidden md:table-cell">
          {ins.categoria && (
            <span className={`badge ${CAT_COLORS[ins.categoria] || 'bg-gray-100 text-gray-600'}`}>
              {CAT_LABELS[ins.categoria] || ins.categoria}
            </span>
          )}
        </td>
        <td className="px-4 py-3 text-right text-sm">
          <span className={ins.alerta_stock ? 'text-red-600 font-semibold' : 'text-gray-700'}>
            {Number(ins.stock_actual).toFixed(0)}
          </span>
          <span className="text-gray-400"> / {Number(ins.stock_minimo).toFixed(0)}</span>
        </td>
        <td className="px-4 py-3 text-right text-sm font-medium text-brand-700">
          {ins.precio_minimo != null ? cop(ins.precio_minimo) : '—'}
        </td>
        <td className="px-4 py-3 text-right">
          {expanded ? <ChevronUp size={16} className="text-gray-400 ml-auto" /> : <ChevronDown size={16} className="text-gray-400 ml-auto" />}
        </td>
      </tr>
      {expanded && (
        <tr className="bg-gray-50">
          <td colSpan={5} className="px-4 pb-4 pt-2">
            {editingInfo ? (
              <div className="space-y-3">
                <div className="text-xs font-medium text-gray-700 mb-2">Editar información del insumo</div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="col-span-2">
                    <label className="block text-xs text-gray-500 mb-0.5">Nombre</label>
                    <input className="input text-sm py-1.5" value={infoForm.nombre} onChange={(e) => setInfoForm({ ...infoForm, nombre: e.target.value })} />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-0.5">Categoría</label>
                    <select className="input text-sm py-1.5" value={infoForm.categoria} onChange={(e) => setInfoForm({ ...infoForm, categoria: e.target.value })}>
                      {CATEGORIAS.map((c) => <option key={c} value={c}>{CAT_LABELS[c]}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-0.5">Unidad de medida</label>
                    <input className="input text-sm py-1.5" placeholder="ml, unidad, par..." value={infoForm.unidad_medida} onChange={(e) => setInfoForm({ ...infoForm, unidad_medida: e.target.value })} />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-0.5">Stock mínimo</label>
                    <input className="input text-sm py-1.5" type="number" value={infoForm.stock_minimo} onChange={(e) => setInfoForm({ ...infoForm, stock_minimo: e.target.value })} />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-0.5">INVIMA</label>
                    <input className="input text-sm py-1.5" value={infoForm.invima} onChange={(e) => setInfoForm({ ...infoForm, invima: e.target.value })} />
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    className="btn-primary text-xs py-1.5 px-4"
                    onClick={() => updateMut.mutate({
                      nombre: infoForm.nombre,
                      categoria: infoForm.categoria,
                      unidad_medida: infoForm.unidad_medida || null,
                      invima: infoForm.invima || null,
                      stock_minimo: parseFloat(infoForm.stock_minimo) || 0,
                    })}
                    disabled={updateMut.isPending}
                  >
                    Guardar cambios
                  </button>
                  <button className="btn-secondary text-xs py-1.5 px-4" onClick={() => setEditingInfo(false)}>Cancelar</button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Stock rápido */}
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-xs font-medium text-gray-600">Stock actual:</span>
                  <input
                    type="number"
                    className="input w-24 text-sm py-1"
                    value={stock}
                    onChange={(e) => setStock(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <button
                    className="btn-primary text-xs py-1 px-3"
                    onClick={(e) => { e.stopPropagation(); updateMut.mutate({ stock_actual: parseFloat(stock) }) }}
                  >
                    Guardar
                  </button>
                  <div className="ml-auto flex items-center gap-3">
                    <button
                      className="text-xs text-brand-600 hover:text-brand-800 flex items-center gap-1"
                      onClick={(e) => { e.stopPropagation(); setEditingInfo(true) }}
                    >
                      <Pencil size={13} /> Editar info
                    </button>
                    <button
                      className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
                      onClick={(e) => { e.stopPropagation(); if (confirm('¿Eliminar este insumo?')) deleteMut.mutate() }}
                    >
                      <Trash2 size={13} /> Eliminar
                    </button>
                  </div>
                </div>

                {/* Precios por proveedor */}
                <div>
                  <div className="text-xs font-medium text-gray-600 mb-2">Precios por proveedor</div>
                  {ins.precios.length === 0 && <p className="text-xs text-gray-400">Sin precios registrados.</p>}
                  <div className="space-y-1">
                    {ins.precios.map((p: any) => (
                      <div key={p.id}>
                        {editingPrecioId === p.id ? (
                          <EditPrecioRow precio={p} espacioId={espacioId} onDone={() => setEditingPrecioId(null)} />
                        ) : (
                          <div className="text-xs flex items-center gap-2 bg-white rounded px-3 py-1.5 border border-gray-100">
                            <span className="font-medium text-gray-700 w-24 flex-shrink-0">{p.proveedor_nombre}</span>
                            <span className="text-gray-500 flex-1">{p.descripcion_presentacion}</span>
                            <span className="font-semibold text-brand-700">{cop(p.precio_presentacion)}</span>
                            {p.unidades_por_presentacion && (
                              <span className="text-gray-400">→ {cop(p.precio_unitario)}/u</span>
                            )}
                            <button
                              className="text-gray-400 hover:text-brand-600 ml-1"
                              onClick={(e) => { e.stopPropagation(); setEditingPrecioId(p.id) }}
                              title="Editar precio"
                            >
                              <Pencil size={12} />
                            </button>
                            <button
                              className="text-gray-400 hover:text-red-500"
                              onClick={(e) => { e.stopPropagation(); if (confirm('¿Eliminar este precio?')) deletePrecioMut.mutate(p.id) }}
                              title="Eliminar precio"
                            >
                              <Trash2 size={12} />
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <AddPrecioForm
                    proveedores={proveedores}
                    onAdd={(data) => addPrecioMut.mutate(data)}
                  />
                </div>
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  )
}

function AddPrecioForm({ proveedores, onAdd }: { proveedores: any[]; onAdd: (d: any) => void }) {
  const [show, setShow] = useState(false)
  const [provId, setProvId] = useState('')
  const [precio, setPrecio] = useState('')
  const [uds, setUds] = useState('')
  const [desc, setDesc] = useState('')

  if (!show) return (
    <button className="text-xs text-brand-600 hover:underline mt-2" onClick={() => setShow(true)}>
      + Agregar precio
    </button>
  )

  function submit() {
    if (!provId || !precio) return
    onAdd({
      proveedor_id: provId,
      precio_presentacion: parseFloat(precio),
      unidades_por_presentacion: uds ? parseInt(uds) : null,
      descripcion_presentacion: desc || null,
    })
    setShow(false)
    setPrecio(''); setUds(''); setDesc(''); setProvId('')
  }

  return (
    <div className="mt-2 bg-white border border-brand-200 rounded-lg p-3 space-y-2">
      <div className="grid grid-cols-2 gap-2">
        <select className="input text-xs py-1" value={provId} onChange={(e) => setProvId(e.target.value)}>
          <option value="">Proveedor...</option>
          {proveedores.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
        </select>
        <input className="input text-xs py-1" placeholder="Precio presentación COP" type="number" value={precio} onChange={(e) => setPrecio(e.target.value)} />
        <input className="input text-xs py-1" placeholder="Unidades por presentación" type="number" value={uds} onChange={(e) => setUds(e.target.value)} />
        <input className="input text-xs py-1" placeholder="Descripción (ej: Caja 100 uds)" value={desc} onChange={(e) => setDesc(e.target.value)} />
      </div>
      <div className="flex gap-2">
        <button className="btn-primary text-xs py-1 px-3" onClick={submit}>Guardar</button>
        <button className="btn-secondary text-xs py-1 px-3" onClick={() => setShow(false)}>Cancelar</button>
      </div>
    </div>
  )
}

function ProveedoresModal({ espacioId, proveedores, onClose }: { espacioId: string; proveedores: any[]; onClose: () => void }) {
  const qc = useQueryClient()
  const [nuevoNombre, setNuevoNombre] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editNombre, setEditNombre] = useState('')

  const crearMut = useMutation({
    mutationFn: (data: any) => api.post(`/espacios/${espacioId}/proveedores`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['proveedores', espacioId] }); setNuevoNombre('') },
  })

  const editarMut = useMutation({
    mutationFn: ({ id, nombre }: { id: string; nombre: string }) => api.put(`/proveedores/${id}`, { nombre }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['proveedores', espacioId] }); setEditingId(null) },
  })

  const eliminarMut = useMutation({
    mutationFn: (id: string) => api.delete(`/proveedores/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['proveedores', espacioId] }),
  })

  function startEdit(prov: any) {
    setEditingId(prov.id)
    setEditNombre(prov.nombre)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Gestionar proveedores</h2>
          <button onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <div className="p-5 space-y-4">
          {/* Lista */}
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {proveedores.length === 0 && <p className="text-sm text-gray-400 text-center py-4">Sin proveedores registrados.</p>}
            {proveedores.map((prov: any) => (
              <div key={prov.id} className="flex items-center gap-2">
                {editingId === prov.id ? (
                  <>
                    <input
                      className="input text-sm py-1.5 flex-1"
                      value={editNombre}
                      onChange={(e) => setEditNombre(e.target.value)}
                      autoFocus
                    />
                    <button
                      className="text-brand-600 hover:text-brand-800 p-1"
                      onClick={() => editarMut.mutate({ id: prov.id, nombre: editNombre })}
                      disabled={editarMut.isPending}
                    >
                      <Check size={16} />
                    </button>
                    <button className="text-gray-400 hover:text-gray-600 p-1" onClick={() => setEditingId(null)}>
                      <X size={16} />
                    </button>
                  </>
                ) : (
                  <>
                    <span className="flex-1 text-sm text-gray-800 px-2 py-1.5 bg-gray-50 rounded-lg">{prov.nombre}</span>
                    <button className="text-gray-400 hover:text-brand-600 p-1" onClick={() => startEdit(prov)} title="Editar">
                      <Pencil size={14} />
                    </button>
                    <button
                      className="text-gray-400 hover:text-red-500 p-1"
                      onClick={() => { if (confirm(`¿Eliminar proveedor "${prov.nombre}"?`)) eliminarMut.mutate(prov.id) }}
                      title="Eliminar"
                    >
                      <Trash2 size={14} />
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>

          {/* Agregar nuevo */}
          <div className="border-t border-gray-100 pt-4">
            <div className="text-xs font-medium text-gray-600 mb-2">Agregar proveedor</div>
            <div className="flex gap-2">
              <input
                className="input text-sm py-1.5 flex-1"
                placeholder="Nombre del proveedor"
                value={nuevoNombre}
                onChange={(e) => setNuevoNombre(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && nuevoNombre.trim()) crearMut.mutate({ nombre: nuevoNombre.trim() }) }}
              />
              <button
                className="btn-primary text-xs py-1.5 px-4"
                onClick={() => { if (nuevoNombre.trim()) crearMut.mutate({ nombre: nuevoNombre.trim() }) }}
                disabled={crearMut.isPending || !nuevoNombre.trim()}
              >
                Agregar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function NuevoInsumoModal({ espacioId, proveedores, onClose }: { espacioId: string; proveedores: any[]; onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    nombre: '', categoria: 'medico', unidad_medida: '', invima: '',
    stock_actual: '0', stock_minimo: '0',
  })
  const [precios, setPrecios] = useState<any[]>([])

  const mut = useMutation({
    mutationFn: (data: any) => api.post(`/espacios/${espacioId}/insumos`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['insumos', espacioId] }); onClose() },
  })

  function addPrecio() {
    setPrecios([...precios, { proveedor_id: '', precio_presentacion: '', unidades_por_presentacion: '', descripcion_presentacion: '' }])
  }

  function setPrecioField(i: number, field: string, val: string) {
    const updated = [...precios]
    updated[i] = { ...updated[i], [field]: val }
    setPrecios(updated)
  }

  function submit(e: React.FormEvent) {
    e.preventDefault()
    mut.mutate({
      ...form,
      stock_actual: parseFloat(form.stock_actual) || 0,
      stock_minimo: parseFloat(form.stock_minimo) || 0,
      precios: precios
        .filter((p) => p.proveedor_id && p.precio_presentacion)
        .map((p) => ({
          ...p,
          precio_presentacion: parseFloat(p.precio_presentacion),
          unidades_por_presentacion: p.unidades_por_presentacion ? parseInt(p.unidades_por_presentacion) : null,
        })),
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Nuevo insumo</h2>
          <button onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <form onSubmit={submit} className="p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-700 mb-1">Nombre *</label>
              <input className="input" required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Categoría</label>
              <select className="input" value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })}>
                {CATEGORIAS.map((c) => <option key={c} value={c}>{CAT_LABELS[c]}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Unidad de medida</label>
              <input className="input" placeholder="unidad, ml, par..." value={form.unidad_medida} onChange={(e) => setForm({ ...form, unidad_medida: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Stock actual</label>
              <input className="input" type="number" value={form.stock_actual} onChange={(e) => setForm({ ...form, stock_actual: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Stock mínimo</label>
              <input className="input" type="number" value={form.stock_minimo} onChange={(e) => setForm({ ...form, stock_minimo: e.target.value })} />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-700 mb-1">INVIMA (opcional)</label>
              <input className="input" value={form.invima} onChange={(e) => setForm({ ...form, invima: e.target.value })} />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-gray-700">Precios por proveedor</label>
              <button type="button" className="text-xs text-brand-600 hover:underline" onClick={addPrecio}>+ Agregar</button>
            </div>
            {precios.map((p, i) => (
              <div key={i} className="grid grid-cols-2 gap-2 mb-2 bg-gray-50 rounded-lg p-2">
                <select className="input text-xs py-1" value={p.proveedor_id} onChange={(e) => setPrecioField(i, 'proveedor_id', e.target.value)}>
                  <option value="">Proveedor...</option>
                  {proveedores.map((pv) => <option key={pv.id} value={pv.id}>{pv.nombre}</option>)}
                </select>
                <input className="input text-xs py-1" placeholder="Precio presentación" type="number" value={p.precio_presentacion} onChange={(e) => setPrecioField(i, 'precio_presentacion', e.target.value)} />
                <input className="input text-xs py-1" placeholder="Uds por presentación" type="number" value={p.unidades_por_presentacion} onChange={(e) => setPrecioField(i, 'unidades_por_presentacion', e.target.value)} />
                <input className="input text-xs py-1" placeholder="Descripción presentación" value={p.descripcion_presentacion} onChange={(e) => setPrecioField(i, 'descripcion_presentacion', e.target.value)} />
              </div>
            ))}
          </div>

          {mut.isError && <p className="text-sm text-red-600">Error al guardar. Intente de nuevo.</p>}
          <div className="flex gap-3 pt-2">
            <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
              {mut.isPending ? 'Guardando...' : 'Guardar insumo'}
            </button>
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function InventarioPage() {
  const { espacioId } = useParams()
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [showProveedores, setShowProveedores] = useState(false)
  const [soloAlertas, setSoloAlertas] = useState(false)

  const { data: insumos = [], isLoading } = useQuery({
    queryKey: ['insumos', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/insumos`).then((r) => r.data),
  })

  const { data: proveedores = [] } = useQuery({
    queryKey: ['proveedores', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/proveedores`).then((r) => r.data),
  })

  const filtered = insumos.filter((ins: any) => {
    const matchSearch = ins.nombre.toLowerCase().includes(search.toLowerCase())
    const matchCat = !catFilter || ins.categoria === catFilter
    const matchAlerta = !soloAlertas || ins.alerta_stock
    return matchSearch && matchCat && matchAlerta
  })

  const alertCount = insumos.filter((i: any) => i.alerta_stock).length

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventario</h1>
          <p className="text-sm text-gray-500 mt-0.5">{insumos.length} insumos registrados</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="btn-secondary flex items-center gap-2"
            onClick={() => setShowProveedores(true)}
            title="Gestionar proveedores"
          >
            <Settings size={15} />
            <span className="hidden sm:inline">Proveedores</span>
          </button>
          <button className="btn-primary flex items-center gap-2" onClick={() => setShowModal(true)}>
            <Plus size={16} />
            <span className="hidden sm:inline">Nuevo insumo</span>
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-2">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            className="input pl-8"
            placeholder="Buscar insumo..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select className="input w-auto" value={catFilter} onChange={(e) => setCatFilter(e.target.value)}>
          <option value="">Todas las categorías</option>
          {CATEGORIAS.map((c) => <option key={c} value={c}>{CAT_LABELS[c]}</option>)}
        </select>
        {alertCount > 0 && (
          <button
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium border transition-colors ${
              soloAlertas ? 'bg-red-600 text-white border-red-600' : 'bg-white text-red-600 border-red-300 hover:bg-red-50'
            }`}
            onClick={() => setSoloAlertas(!soloAlertas)}
          >
            <AlertTriangle size={14} />
            {alertCount} alerta{alertCount !== 1 ? 's' : ''}
          </button>
        )}
      </div>

      {/* Tabla */}
      <div className="card p-0 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Cargando...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Insumo</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Categoría</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Stock / Mín</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Precio mín.</th>
                <th className="px-4 py-3 w-8" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filtered.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">Sin resultados</td></tr>
              )}
              {filtered.map((ins: any) => (
                <InsumoRow key={ins.id} ins={ins} espacioId={espacioId!} proveedores={proveedores} />
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <NuevoInsumoModal espacioId={espacioId!} proveedores={proveedores} onClose={() => setShowModal(false)} />
      )}
      {showProveedores && (
        <ProveedoresModal espacioId={espacioId!} proveedores={proveedores} onClose={() => setShowProveedores(false)} />
      )}
    </div>
  )
}
