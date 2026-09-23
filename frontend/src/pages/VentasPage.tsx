import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import {
  Plus, X, ShoppingCart, TrendingUp, Clock, AlertTriangle,
  Ban, Check, Package, Layers,
} from 'lucide-react'

function cop(n: number | string) {
  const v = typeof n === 'string' ? parseFloat(n) : n
  return new Intl.NumberFormat('es-CO', {
    style: 'currency', currency: 'COP', maximumFractionDigits: 0,
  }).format(v || 0)
}

function hoy() {
  return new Date().toISOString().slice(0, 10)
}

function fechaLarga(iso: string) {
  return new Date(iso + 'T12:00:00').toLocaleDateString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

type LineaEdit = {
  tipo: 'producto' | 'combo'
  id: string
  cantidad: string
  precio: string
  precioTocado: boolean
}

// ----------------------------------------------------------------- indicadores

function Indicador({ titulo, valor, icono: Icono, color, nota }: any) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <div className="text-xs text-gray-500">{titulo}</div>
          <div className={`text-xl font-bold mt-0.5 ${color}`}>{valor}</div>
          {nota && <div className="text-xs text-gray-400 mt-0.5">{nota}</div>}
        </div>
        <Icono size={18} className="text-gray-300 flex-shrink-0 ml-2" />
      </div>
    </div>
  )
}

// ----------------------------------------------------------------- nueva venta

function ModalVenta({ espacioId, productos, combos, onClose }: any) {
  const qc = useQueryClient()
  const [cabecera, setCabecera] = useState({
    fecha: hoy(), cliente: '', notas: '', estado_pago: 'pagado',
  })
  const [lineas, setLineas] = useState<LineaEdit[]>([])
  const [error, setError] = useState<string | null>(null)

  function sugerido(linea: LineaEdit): number {
    if (!linea.id) return 0
    if (linea.tipo === 'producto') {
      const p = productos.find((x: any) => x.id === linea.id)
      if (!p) return 0
      if (p.precio_venta != null) return parseFloat(p.precio_venta)
      return Math.round((p.precio_minimo ?? 0) * 1.4)
    }
    const c = combos.find((x: any) => x.id === linea.id)
    if (!c) return 0
    const costo = c.insumos.reduce((a: number, i: any) => a + (i.costo_total || 0), 0)
    return Math.round(costo * (1 + parseFloat(c.margen_ganancia_pct || 40) / 100))
  }

  function stockDisponible(linea: LineaEdit): number | null {
    if (linea.tipo !== 'producto' || !linea.id) return null
    const p = productos.find((x: any) => x.id === linea.id)
    return p ? parseFloat(p.stock_actual ?? 0) : null
  }

  function agregar() {
    setLineas([...lineas, { tipo: 'producto', id: '', cantidad: '1', precio: '', precioTocado: false }])
  }

  function quitar(i: number) {
    setLineas(lineas.filter((_, idx) => idx !== i))
  }

  function actualizar(i: number, cambios: Partial<LineaEdit>) {
    const copia = [...lineas]
    copia[i] = { ...copia[i], ...cambios }
    // Al elegir producto o cambiar de tipo, se repone el precio sugerido
    // salvo que el usuario ya lo haya escrito a mano.
    if ((cambios.id !== undefined || cambios.tipo !== undefined) && !copia[i].precioTocado) {
      copia[i].precio = String(sugerido(copia[i]) || '')
    }
    setLineas(copia)
  }

  const total = lineas.reduce((a, l) => a + (parseFloat(l.precio) || 0) * (parseFloat(l.cantidad) || 0), 0)

  const mut = useMutation({
    mutationFn: (data: any) => api.post(`/espacios/${espacioId}/ventas`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ventas', espacioId] })
      qc.invalidateQueries({ queryKey: ['insumos', espacioId] })
      qc.invalidateQueries({ queryKey: ['caja', espacioId] })
      onClose()
    },
    onError: (err: any) => {
      const d = err?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'No se pudo registrar la venta.')
    },
  })

  function enviar(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    const items = lineas
      .filter((l) => l.id && parseFloat(l.cantidad) > 0)
      .map((l) => ({
        [l.tipo === 'producto' ? 'insumo_id' : 'servicio_id']: l.id,
        cantidad: parseFloat(l.cantidad),
        precio_unitario: l.precio === '' ? null : parseFloat(l.precio),
      }))
    if (!items.length) {
      setError('Agrega al menos un producto o combo.')
      return
    }
    mut.mutate({ ...cabecera, cliente: cabecera.cliente || null, notas: cabecera.notas || null, items })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <form onSubmit={enviar} className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[92vh] flex flex-col">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Nueva venta</h2>
          <button type="button" onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>

        <div className="p-5 space-y-4 overflow-y-auto">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Fecha *</label>
              <input type="date" className="input" required value={cabecera.fecha}
                onChange={(e) => setCabecera({ ...cabecera, fecha: e.target.value })} />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-700 mb-1">Cliente</label>
              <input className="input" placeholder="Nombre de quien compra"
                value={cabecera.cliente}
                onChange={(e) => setCabecera({ ...cabecera, cliente: e.target.value })} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {[['pagado', 'Pagada'], ['pendiente', 'Queda debiendo']].map(([valor, etiqueta]) => (
              <button
                key={valor}
                type="button"
                onClick={() => setCabecera({ ...cabecera, estado_pago: valor })}
                className={`py-2.5 rounded-lg text-sm font-medium border transition-colors ${
                  cabecera.estado_pago === valor
                    ? valor === 'pagado'
                      ? 'bg-green-600 text-white border-green-600'
                      : 'bg-yellow-500 text-white border-yellow-500'
                    : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {etiqueta}
              </button>
            ))}
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-700">Qué se vendió</span>
              <button type="button" className="text-xs text-brand-600 hover:underline" onClick={agregar}>
                + Agregar línea
              </button>
            </div>

            <div className="space-y-2">
              {lineas.map((linea, i) => {
                const sug = sugerido(linea)
                const precio = parseFloat(linea.precio) || 0
                const cantidad = parseFloat(linea.cantidad) || 0
                const stock = stockDisponible(linea)
                const faltaStock = stock !== null && cantidad > stock
                const fueraDeLista = linea.id && sug > 0 && Math.abs(precio - sug) > 1

                return (
                  <div key={i} className="bg-gray-50 rounded-lg p-3 space-y-2">
                    <div className="flex gap-2">
                      <select
                        className="input text-xs py-1 w-28 flex-shrink-0"
                        value={linea.tipo}
                        onChange={(e) => actualizar(i, { tipo: e.target.value as any, id: '' })}
                      >
                        <option value="producto">Producto</option>
                        <option value="combo">Combo</option>
                      </select>
                      <select
                        className="input text-xs py-1 flex-1 min-w-0"
                        value={linea.id}
                        onChange={(e) => actualizar(i, { id: e.target.value })}
                      >
                        <option value="">Seleccionar...</option>
                        {(linea.tipo === 'producto' ? productos : combos).map((o: any) => (
                          <option key={o.id} value={o.id}>{o.nombre}</option>
                        ))}
                      </select>
                      <button type="button" onClick={() => quitar(i)}
                        className="text-gray-400 hover:text-red-500 flex-shrink-0">
                        <X size={15} />
                      </button>
                    </div>

                    <div className="flex gap-2 items-center">
                      <div className="w-20 flex-shrink-0">
                        <input type="number" className="input text-xs py-1 text-center" min="0" step="0.01"
                          placeholder="Cant." value={linea.cantidad}
                          onChange={(e) => actualizar(i, { cantidad: e.target.value })} />
                      </div>
                      <span className="text-xs text-gray-400">×</span>
                      <div className="flex-1 min-w-0">
                        <input type="number" className="input text-xs py-1 text-right" min="0"
                          placeholder="Precio" value={linea.precio}
                          onChange={(e) => actualizar(i, { precio: e.target.value, precioTocado: true })} />
                      </div>
                      <span className="text-xs font-semibold text-brand-700 w-24 text-right flex-shrink-0">
                        {cop(precio * cantidad)}
                      </span>
                    </div>

                    {linea.id && (
                      <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs">
                        {sug > 0 && (
                          <span className="text-gray-500">
                            Sugerido {cop(sug)}
                            {linea.precioTocado && precio !== sug && (
                              <button type="button" className="ml-1 text-brand-600 hover:underline"
                                onClick={() => actualizar(i, { precio: String(sug), precioTocado: false })}>
                                usar
                              </button>
                            )}
                          </span>
                        )}
                        {stock !== null && (
                          <span className={faltaStock ? 'text-red-600 font-medium' : 'text-gray-500'}>
                            Stock: {stock}
                            {faltaStock && ' — insuficiente'}
                          </span>
                        )}
                        {fueraDeLista && (
                          <span className="text-yellow-700">
                            {precio > sug ? 'Por encima' : 'Por debajo'} de lista
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
              {lineas.length === 0 && (
                <p className="text-xs text-gray-400 py-3 text-center">
                  Sin líneas. Agrega el primer producto o combo.
                </p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Notas</label>
            <input className="input" placeholder="Opcional"
              value={cabecera.notas}
              onChange={(e) => setCabecera({ ...cabecera, notas: e.target.value })} />
          </div>

          {error && <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>}
        </div>

        <div className="border-t border-gray-100 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total de la venta</span>
            <span className="text-xl font-bold text-brand-700">{cop(total)}</span>
          </div>
          <div className="flex gap-3">
            <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
              {mut.isPending ? 'Guardando...' : 'Registrar venta'}
            </button>
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
          </div>
        </div>
      </form>
    </div>
  )
}

// ----------------------------------------------------------------- fila

function FilaVenta({ venta, espacioId }: { venta: any; espacioId: string }) {
  const qc = useQueryClient()
  const [abierta, setAbierta] = useState(false)
  const [anulando, setAnulando] = useState(false)
  const [motivo, setMotivo] = useState('')

  function invalidar() {
    qc.invalidateQueries({ queryKey: ['ventas', espacioId] })
    qc.invalidateQueries({ queryKey: ['insumos', espacioId] })
    qc.invalidateQueries({ queryKey: ['caja', espacioId] })
  }

  const anular = useMutation({
    mutationFn: () => api.post(`/ventas/${venta.id}/anular`, { motivo }),
    onSuccess: () => { invalidar(); setAnulando(false) },
  })

  const pagar = useMutation({
    mutationFn: () => api.post(`/ventas/${venta.id}/registrar-pago`, { fecha_pago: hoy() }),
    onSuccess: invalidar,
  })

  const pendiente = venta.estado_pago === 'pendiente'

  return (
    <div className={`card space-y-2 ${venta.anulada ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between gap-3 cursor-pointer" onClick={() => setAbierta(!abierta)}>
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`font-medium text-gray-900 ${venta.anulada ? 'line-through' : ''}`}>
              {venta.cliente || 'Venta sin cliente'}
            </span>
            {venta.anulada && <span className="badge bg-red-100 text-red-700">Anulada</span>}
            {!venta.anulada && pendiente && (
              <span className="badge bg-yellow-100 text-yellow-700">Sin pagar</span>
            )}
            {!venta.anulada && !pendiente && (
              <span className="badge bg-green-100 text-green-700">Pagada</span>
            )}
            {venta.alertas?.length > 0 && !venta.anulada && (
              <span className="badge bg-orange-100 text-orange-700 flex items-center gap-1">
                <AlertTriangle size={10} /> {venta.alertas.length}
              </span>
            )}
          </div>
          <div className="text-xs text-gray-400 mt-0.5">
            {fechaLarga(venta.fecha)} · {venta.items.length} {venta.items.length === 1 ? 'línea' : 'líneas'}
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="font-bold text-brand-700">{cop(venta.total)}</div>
          {!venta.anulada && (
            <div className="text-xs text-gray-400">utilidad {cop(venta.utilidad)}</div>
          )}
        </div>
      </div>

      {venta.alertas?.length > 0 && !venta.anulada && (
        <div className="space-y-1">
          {venta.alertas.map((a: any, i: number) => (
            <div key={i} className={`text-xs rounded-lg px-3 py-2 flex gap-2 ${
              a.severidad === 'alta' ? 'bg-red-50 text-red-800' : 'bg-yellow-50 text-yellow-800'
            }`}>
              <AlertTriangle size={13} className="flex-shrink-0 mt-0.5" />
              {a.mensaje}
            </div>
          ))}
        </div>
      )}

      {venta.anulada && venta.motivo_anulacion && (
        <div className="text-xs text-red-600">Motivo de anulación: {venta.motivo_anulacion}</div>
      )}

      {abierta && (
        <div className="border-t border-gray-100 pt-2 space-y-1">
          {venta.items.map((it: any) => (
            <div key={it.id} className="flex items-center gap-2 text-xs bg-gray-50 rounded px-3 py-1.5">
              {it.servicio_id ? <Layers size={12} className="text-pink-500" /> : <Package size={12} className="text-blue-500" />}
              <span className="flex-1 text-gray-700">{it.descripcion}</span>
              <span className="text-gray-500">×{Number(it.cantidad).toFixed(2)}</span>
              <span className="text-gray-500 hidden sm:inline">@ {cop(it.precio_unitario)}</span>
              <span className="font-medium text-brand-700 w-24 text-right">{cop(it.subtotal)}</span>
            </div>
          ))}
          {venta.notas && <p className="text-xs text-gray-500 pt-1">{venta.notas}</p>}
        </div>
      )}

      {!venta.anulada && (
        <div className="flex items-center justify-end gap-3 pt-1">
          {pendiente && (
            <button
              className="text-xs text-green-700 hover:underline flex items-center gap-1"
              onClick={() => pagar.mutate()}
              disabled={pagar.isPending}
            >
              <Check size={13} /> Registrar pago
            </button>
          )}
          {!anulando && (
            <button className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
              onClick={() => setAnulando(true)}>
              <Ban size={13} /> Anular
            </button>
          )}
        </div>
      )}

      {anulando && (
        <div className="border-t border-gray-100 pt-2 space-y-2">
          <p className="text-xs text-gray-500">
            Se devuelve el stock y se revierte el ingreso. La venta queda registrada.
          </p>
          <div className="flex gap-2">
            <input className="input text-xs py-1 flex-1" placeholder="¿Por qué se anula?"
              value={motivo} onChange={(e) => setMotivo(e.target.value)} />
            <button className="btn-primary text-xs py-1 px-3" disabled={!motivo || anular.isPending}
              onClick={() => anular.mutate()}>
              Anular
            </button>
            <button className="btn-secondary text-xs py-1 px-3" onClick={() => setAnulando(false)}>
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ----------------------------------------------------------------- pagina

export default function VentasPage() {
  const { espacioId } = useParams()
  const [modal, setModal] = useState(false)
  const [filtro, setFiltro] = useState<'todas' | 'pendiente' | 'alertas'>('todas')

  const { data: resumen } = useQuery({
    queryKey: ['ventas', espacioId, 'resumen'],
    queryFn: () => api.get(`/espacios/${espacioId}/ventas/resumen`).then((r) => r.data),
  })

  const { data: ventas = [], isLoading } = useQuery({
    queryKey: ['ventas', espacioId, 'lista'],
    queryFn: () => api.get(`/espacios/${espacioId}/ventas`).then((r) => r.data),
  })

  const { data: productos = [] } = useQuery({
    queryKey: ['insumos', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/insumos`).then((r) => r.data),
  })

  const { data: combos = [] } = useQuery({
    queryKey: ['servicios', espacioId],
    queryFn: () => api.get(`/espacios/${espacioId}/servicios`).then((r) => r.data),
  })

  const visibles = ventas.filter((v: any) => {
    if (filtro === 'pendiente') return v.estado_pago === 'pendiente' && !v.anulada
    if (filtro === 'alertas') return v.alertas?.length > 0 && !v.anulada
    return true
  })

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ventas</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Cada venta descuenta inventario y suma a caja
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setModal(true)}>
          <Plus size={16} /> Nueva venta
        </button>
      </div>

      {resumen && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <Indicador titulo="Vendido" valor={cop(resumen.total_vendido)} icono={ShoppingCart}
            color="text-brand-700" nota={`${resumen.cantidad_ventas} ventas`} />
          <Indicador titulo="Utilidad" valor={cop(resumen.utilidad)} icono={TrendingUp}
            color="text-green-700"
            nota={resumen.margen_pct != null ? `margen ${resumen.margen_pct.toFixed(0)}%` : undefined} />
          <Indicador titulo="Por cobrar" valor={cop(resumen.por_cobrar)} icono={Clock}
            color="text-yellow-700" nota={`${resumen.ventas_pendientes} sin pagar`} />
          <Indicador titulo="Con alertas" valor={String(resumen.ventas_con_alertas)} icono={AlertTriangle}
            color={resumen.ventas_con_alertas > 0 ? 'text-orange-600' : 'text-gray-400'}
            nota="requieren revisión" />
        </div>
      )}

      <div className="flex gap-1 border-b border-gray-200">
        {([['todas', `Todas (${ventas.length})`],
           ['pendiente', `Sin pagar (${resumen?.ventas_pendientes ?? 0})`],
           ['alertas', `Con alertas (${resumen?.ventas_con_alertas ?? 0})`]] as const).map(([v, etiqueta]) => (
          <button key={v} onClick={() => setFiltro(v)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              filtro === v ? 'border-brand-600 text-brand-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}>
            {etiqueta}
          </button>
        ))}
      </div>

      {isLoading && <div className="text-center py-8 text-gray-500">Cargando...</div>}

      <div className="space-y-3">
        {visibles.map((v: any) => <FilaVenta key={v.id} venta={v} espacioId={espacioId!} />)}
        {!isLoading && visibles.length === 0 && (
          <div className="card py-12 text-center text-gray-400">
            <ShoppingCart size={36} className="mx-auto mb-2 text-gray-300" />
            <p className="font-medium text-gray-500">
              {filtro === 'todas' ? 'Sin ventas registradas' : 'Nada en este filtro'}
            </p>
            {filtro === 'todas' && <p className="text-sm">Registra la primera venta.</p>}
          </div>
        )}
      </div>

      {modal && (
        <ModalVenta espacioId={espacioId!} productos={productos} combos={combos}
          onClose={() => setModal(false)} />
      )}
    </div>
  )
}
