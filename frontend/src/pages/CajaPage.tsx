import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import {
  Plus, X, AlertTriangle, TrendingUp, TrendingDown, Wallet,
  HandCoins, ClipboardCheck, Ban, Check,
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
  // Se fuerza a mediodia UTC para que la zona horaria no corra el dia.
  return new Date(iso + 'T12:00:00').toLocaleDateString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

const CATEGORIAS = [
  { valor: 'venta', etiqueta: 'Venta' },
  { valor: 'compra', etiqueta: 'Compra de mercancía' },
  { valor: 'gasto', etiqueta: 'Gasto' },
  { valor: 'prestamo', etiqueta: 'Préstamo' },
  { valor: 'abono', etiqueta: 'Abono recibido' },
  { valor: 'ajuste', etiqueta: 'Ajuste de caja' },
  { valor: 'otro', etiqueta: 'Otro' },
]

function etiquetaCategoria(valor: string) {
  return CATEGORIAS.find((c) => c.valor === valor)?.etiqueta ?? valor
}

// ----------------------------------------------------------------- tarjetas

function Indicador({ titulo, valor, icono: Icono, color, nota }: any) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <div className="text-xs text-gray-500">{titulo}</div>
          <div className={`text-xl font-bold mt-0.5 ${color}`}>{cop(valor)}</div>
          {nota && <div className="text-xs text-gray-400 mt-0.5">{nota}</div>}
        </div>
        <Icono size={18} className="text-gray-300 flex-shrink-0 ml-2" />
      </div>
    </div>
  )
}

function PanelAlertas({ alertas }: { alertas: any[] }) {
  if (!alertas?.length) return null
  return (
    <div className="space-y-2">
      {alertas.map((a, i) => (
        <div
          key={i}
          className={`rounded-xl px-4 py-3 flex gap-3 border ${
            a.severidad === 'alta'
              ? 'bg-red-50 border-red-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}
        >
          <AlertTriangle
            size={17}
            className={`flex-shrink-0 mt-0.5 ${
              a.severidad === 'alta' ? 'text-red-500' : 'text-yellow-600'
            }`}
          />
          <div className="min-w-0">
            <div className={`text-sm font-medium ${
              a.severidad === 'alta' ? 'text-red-800' : 'text-yellow-800'
            }`}>
              {a.mensaje}
            </div>
            {a.detalle && (
              <div className="text-xs text-gray-600 mt-0.5">{a.detalle}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

// ----------------------------------------------------------------- modales

function ModalMovimiento({ espacioId, onClose }: { espacioId: string; onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    fecha: hoy(), tipo: 'ingreso', categoria: 'venta', concepto: '', monto: '',
  })
  const [error, setError] = useState<string | null>(null)

  const mut = useMutation({
    mutationFn: (data: any) => api.post(`/espacios/${espacioId}/caja/movimientos`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['caja', espacioId] })
      onClose()
    },
    onError: (err: any) => {
      const d = err?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'No se pudo registrar el movimiento.')
    },
  })

  function enviar(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    mut.mutate({ ...form, monto: parseFloat(form.monto) || 0 })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <form onSubmit={enviar} className="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Nuevo movimiento</h2>
          <button type="button" onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-2 gap-2">
            {['ingreso', 'egreso'].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setForm({ ...form, tipo: t })}
                className={`py-2.5 rounded-lg text-sm font-medium border transition-colors ${
                  form.tipo === t
                    ? t === 'ingreso'
                      ? 'bg-green-600 text-white border-green-600'
                      : 'bg-red-600 text-white border-red-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {t === 'ingreso' ? 'Entra dinero' : 'Sale dinero'}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Fecha *</label>
              <input type="date" className="input" required value={form.fecha}
                onChange={(e) => setForm({ ...form, fecha: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Categoría *</label>
              <select className="input" value={form.categoria}
                onChange={(e) => setForm({ ...form, categoria: e.target.value })}>
                {CATEGORIAS.map((c) => (
                  <option key={c.valor} value={c.valor}>{c.etiqueta}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Concepto *</label>
            <input className="input" required placeholder="Ej: Venta de V-Daily a la Dra. Quintero"
              value={form.concepto} onChange={(e) => setForm({ ...form, concepto: e.target.value })} />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Monto (COP) *</label>
            <input type="number" className="input" required min="1" placeholder="350000"
              value={form.monto} onChange={(e) => setForm({ ...form, monto: e.target.value })} />
            {form.monto && (
              <p className="text-xs text-gray-500 mt-1">{cop(form.monto)}</p>
            )}
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
        <div className="flex gap-3 p-5 border-t border-gray-100">
          <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
            {mut.isPending ? 'Guardando...' : 'Registrar movimiento'}
          </button>
          <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}

function ModalPrestamo({ espacioId, onClose }: { espacioId: string; onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    fecha: hoy(), deudor: '', concepto: '', monto: '', notas: '', afecta_caja: true,
  })
  const [error, setError] = useState<string | null>(null)

  const mut = useMutation({
    mutationFn: (data: any) => api.post(`/espacios/${espacioId}/caja/prestamos`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['caja', espacioId] })
      onClose()
    },
    onError: (err: any) => {
      const d = err?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'No se pudo registrar el préstamo.')
    },
  })

  function enviar(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    mut.mutate({ ...form, monto: parseFloat(form.monto) || 0 })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <form onSubmit={enviar} className="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Nuevo préstamo</h2>
          <button type="button" onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Fecha *</label>
              <input type="date" className="input" required value={form.fecha}
                onChange={(e) => setForm({ ...form, fecha: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Monto (COP) *</label>
              <input type="number" className="input" required min="1" placeholder="400000"
                value={form.monto} onChange={(e) => setForm({ ...form, monto: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">¿A quién? *</label>
            <input className="input" required placeholder="Ej: Dra. María Fernanda"
              value={form.deudor} onChange={(e) => setForm({ ...form, deudor: e.target.value })} />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Concepto</label>
            <input className="input" placeholder="Ej: Préstamo a la empresa"
              value={form.concepto} onChange={(e) => setForm({ ...form, concepto: e.target.value })} />
          </div>
          <label className="flex items-start gap-2 text-sm text-gray-700 cursor-pointer">
            <input type="checkbox" className="mt-0.5" checked={form.afecta_caja}
              onChange={(e) => setForm({ ...form, afecta_caja: e.target.checked })} />
            <span>
              Descontar de la caja
              <span className="block text-xs text-gray-500">
                Desmárcalo si el dinero no salió de la caja registrada.
              </span>
            </span>
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
        <div className="flex gap-3 p-5 border-t border-gray-100">
          <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
            {mut.isPending ? 'Guardando...' : 'Registrar préstamo'}
          </button>
          <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}

function ModalArqueo({ espacioId, saldoTeorico, onClose }: any) {
  const qc = useQueryClient()
  const [form, setForm] = useState({ fecha: hoy(), efectivo_contado: '', notas: '' })
  const [error, setError] = useState<string | null>(null)

  const contado = parseFloat(form.efectivo_contado) || 0
  const diferencia = form.efectivo_contado !== '' ? contado - saldoTeorico : null

  const mut = useMutation({
    mutationFn: (data: any) => api.post(`/espacios/${espacioId}/caja/arqueos`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['caja', espacioId] })
      onClose()
    },
    onError: (err: any) => {
      const d = err?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'No se pudo registrar el arqueo.')
    },
  })

  function enviar(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    mut.mutate({ ...form, efectivo_contado: contado })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <form onSubmit={enviar} className="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Arqueo de caja</h2>
          <button type="button" onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <div className="p-5 space-y-4">
          <p className="text-sm text-gray-600">
            Cuenta el efectivo que tienes físicamente y anótalo aquí. El sistema lo
            compara contra el saldo esperado y deja registrada la diferencia.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Fecha *</label>
              <input type="date" className="input" required value={form.fecha}
                onChange={(e) => setForm({ ...form, fecha: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Efectivo contado *</label>
              <input type="number" className="input" required min="0" placeholder="900000"
                value={form.efectivo_contado}
                onChange={(e) => setForm({ ...form, efectivo_contado: e.target.value })} />
            </div>
          </div>

          <div className="bg-gray-50 rounded-xl p-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Saldo esperado</span>
              <span className="font-medium">{cop(saldoTeorico)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Efectivo contado</span>
              <span className="font-medium">{cop(contado)}</span>
            </div>
            {diferencia !== null && (
              <div className="flex justify-between border-t border-gray-200 pt-2">
                <span className="text-gray-700 font-medium">Diferencia</span>
                <span className={`font-bold ${
                  diferencia === 0 ? 'text-green-700'
                    : diferencia > 0 ? 'text-blue-700' : 'text-red-700'
                }`}>
                  {diferencia === 0 ? 'Cuadra' : (diferencia > 0 ? 'Sobran ' : 'Faltan ') + cop(Math.abs(diferencia))}
                </span>
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Notas</label>
            <textarea className="input h-16 resize-none"
              placeholder="Explica la diferencia si la hay"
              value={form.notas} onChange={(e) => setForm({ ...form, notas: e.target.value })} />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
        <div className="flex gap-3 p-5 border-t border-gray-100">
          <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
            {mut.isPending ? 'Guardando...' : 'Registrar arqueo'}
          </button>
          <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}

// ----------------------------------------------------------------- secciones

function FilaPrestamo({ prestamo, espacioId }: { prestamo: any; espacioId: string }) {
  const qc = useQueryClient()
  const [abonando, setAbonando] = useState(false)
  const [form, setForm] = useState({ fecha: hoy(), monto: '', notas: '', afecta_caja: true })

  const mut = useMutation({
    mutationFn: (data: any) => api.post(`/caja/prestamos/${prestamo.id}/abonos`, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['caja', espacioId] })
      setAbonando(false)
      setForm({ fecha: hoy(), monto: '', notas: '', afecta_caja: true })
    },
  })

  const saldo = parseFloat(prestamo.saldo)
  const pagado = saldo <= 0

  return (
    <div className={`border rounded-xl px-4 py-3 ${pagado ? 'border-green-200 bg-green-50/50' : 'border-gray-200'}`}>
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-gray-900">{prestamo.deudor}</span>
            {pagado && <span className="badge bg-green-100 text-green-700">Pagado</span>}
          </div>
          {prestamo.concepto && <p className="text-xs text-gray-500 mt-0.5">{prestamo.concepto}</p>}
          <p className="text-xs text-gray-400 mt-0.5">{fechaLarga(prestamo.fecha)}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-xs text-gray-500">Saldo por cobrar</div>
          <div className={`font-bold ${pagado ? 'text-green-700' : 'text-red-600'}`}>{cop(saldo)}</div>
          <div className="text-xs text-gray-400">
            de {cop(prestamo.monto)}
            {parseFloat(prestamo.total_abonado) > 0 && ` · abonado ${cop(prestamo.total_abonado)}`}
          </div>
        </div>
      </div>

      {prestamo.abonos?.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-100 space-y-1">
          {prestamo.abonos.map((a: any) => (
            <div key={a.id} className="flex justify-between text-xs text-gray-500">
              <span>Abono · {fechaLarga(a.fecha)}</span>
              <span className="text-green-700 font-medium">{cop(a.monto)}</span>
            </div>
          ))}
        </div>
      )}

      {!pagado && !abonando && (
        <button
          className="text-xs text-brand-600 hover:underline mt-2"
          onClick={() => setAbonando(true)}
        >
          + Registrar abono
        </button>
      )}

      {abonando && (
        <div className="mt-3 pt-3 border-t border-gray-100 space-y-2">
          <div className="flex gap-2">
            <input type="date" className="input text-xs py-1 flex-1" value={form.fecha}
              onChange={(e) => setForm({ ...form, fecha: e.target.value })} />
            <input type="number" className="input text-xs py-1 w-28" placeholder="Monto" min="1"
              value={form.monto} onChange={(e) => setForm({ ...form, monto: e.target.value })} />
          </div>
          <label className="flex items-center gap-2 text-xs text-gray-600">
            <input type="checkbox" checked={form.afecta_caja}
              onChange={(e) => setForm({ ...form, afecta_caja: e.target.checked })} />
            Sumar a la caja
          </label>
          <div className="flex gap-2">
            <button
              className="btn-primary text-xs py-1 px-3 flex items-center gap-1"
              disabled={mut.isPending || !form.monto}
              onClick={() => mut.mutate({ ...form, monto: parseFloat(form.monto) || 0 })}
            >
              <Check size={13} /> Guardar
            </button>
            <button className="btn-secondary text-xs py-1 px-3" onClick={() => setAbonando(false)}>
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function FilaMovimiento({ mov }: { mov: any }) {
  const qc = useQueryClient()
  const { espacioId } = useParams()
  const [anulando, setAnulando] = useState(false)
  const [motivo, setMotivo] = useState('')

  const mut = useMutation({
    mutationFn: () => api.post(`/caja/movimientos/${mov.id}/anular`, { motivo }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['caja', espacioId] })
      setAnulando(false)
    },
  })

  const esIngreso = mov.tipo === 'ingreso'

  return (
    <div className={`px-4 py-2.5 flex items-start justify-between gap-3 ${mov.anulado ? 'opacity-50' : ''}`}>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`text-sm text-gray-900 ${mov.anulado ? 'line-through' : ''}`}>
            {mov.concepto}
          </span>
          <span className="badge bg-gray-100 text-gray-600">{etiquetaCategoria(mov.categoria)}</span>
          {mov.anulado && <span className="badge bg-red-100 text-red-700">Anulado</span>}
        </div>
        <div className="text-xs text-gray-400 mt-0.5">{fechaLarga(mov.fecha)}</div>
        {mov.anulado && mov.motivo_anulacion && (
          <div className="text-xs text-red-600 mt-0.5">Motivo: {mov.motivo_anulacion}</div>
        )}
        {anulando && (
          <div className="mt-2 flex gap-2">
            <input
              className="input text-xs py-1 flex-1"
              placeholder="¿Por qué se anula?"
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
            />
            <button
              className="btn-primary text-xs py-1 px-3"
              disabled={!motivo || mut.isPending}
              onClick={() => mut.mutate()}
            >
              Anular
            </button>
            <button className="btn-secondary text-xs py-1 px-3" onClick={() => setAnulando(false)}>
              Cancelar
            </button>
          </div>
        )}
      </div>
      <div className="text-right flex-shrink-0 flex items-start gap-2">
        <span className={`font-semibold text-sm ${
          mov.anulado ? 'text-gray-400' : esIngreso ? 'text-green-700' : 'text-red-600'
        }`}>
          {esIngreso ? '+' : '−'}{cop(mov.monto)}
        </span>
        {!mov.anulado && !anulando && (
          <button
            className="text-gray-300 hover:text-red-500 transition-colors"
            title="Anular movimiento"
            onClick={() => setAnulando(true)}
          >
            <Ban size={14} />
          </button>
        )}
      </div>
    </div>
  )
}

// ----------------------------------------------------------------- pagina

export default function CajaPage() {
  const { espacioId } = useParams()
  const [modal, setModal] = useState<null | 'movimiento' | 'prestamo' | 'arqueo'>(null)
  const [tab, setTab] = useState<'movimientos' | 'prestamos'>('movimientos')

  const { data: resumen, isLoading } = useQuery({
    queryKey: ['caja', espacioId, 'resumen'],
    queryFn: () => api.get(`/espacios/${espacioId}/caja/resumen`).then((r) => r.data),
  })

  const { data: movimientos = [] } = useQuery({
    queryKey: ['caja', espacioId, 'movimientos'],
    queryFn: () => api.get(`/espacios/${espacioId}/caja/movimientos`).then((r) => r.data),
  })

  const { data: prestamos = [] } = useQuery({
    queryKey: ['caja', espacioId, 'prestamos'],
    queryFn: () => api.get(`/espacios/${espacioId}/caja/prestamos`).then((r) => r.data),
  })

  const saldoTeorico = parseFloat(resumen?.saldo_teorico ?? 0)

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Caja</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Movimientos de efectivo, préstamos y cuadre
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button className="btn-secondary flex items-center gap-2 text-sm"
            onClick={() => setModal('arqueo')}>
            <ClipboardCheck size={15} /> Arqueo
          </button>
          <button className="btn-secondary flex items-center gap-2 text-sm"
            onClick={() => setModal('prestamo')}>
            <HandCoins size={15} /> Préstamo
          </button>
          <button className="btn-primary flex items-center gap-2"
            onClick={() => setModal('movimiento')}>
            <Plus size={16} /> Movimiento
          </button>
        </div>
      </div>

      {isLoading && <div className="text-center py-8 text-gray-500">Cargando...</div>}

      {resumen && (
        <>
          <PanelAlertas alertas={resumen.alertas} />

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Indicador titulo="Saldo en caja" valor={resumen.saldo_teorico} icono={Wallet}
              color={saldoTeorico < 0 ? 'text-red-600' : 'text-brand-700'}
              nota="Según lo registrado" />
            <Indicador titulo="Ingresos" valor={resumen.total_ingresos} icono={TrendingUp}
              color="text-green-700" />
            <Indicador titulo="Egresos" valor={resumen.total_egresos} icono={TrendingDown}
              color="text-red-600" />
            <Indicador titulo="Por cobrar" valor={resumen.saldo_por_cobrar} icono={HandCoins}
              color="text-yellow-700"
              nota={`Prestado ${cop(resumen.total_prestado)}`} />
          </div>

          {resumen.ultimo_arqueo && (
            <div className="card flex items-center justify-between gap-3 flex-wrap">
              <div className="text-sm">
                <span className="text-gray-500">Último arqueo · </span>
                <span className="text-gray-700">{fechaLarga(resumen.ultimo_arqueo.fecha)}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-500">Contado </span>
                <span className="font-medium">{cop(resumen.ultimo_arqueo.efectivo_contado)}</span>
                <span className="text-gray-400"> vs esperado </span>
                <span className="font-medium">{cop(resumen.ultimo_arqueo.saldo_teorico)}</span>
                <span className={`ml-2 font-semibold ${
                  parseFloat(resumen.ultimo_arqueo.diferencia) === 0
                    ? 'text-green-700' : 'text-red-600'
                }`}>
                  {parseFloat(resumen.ultimo_arqueo.diferencia) === 0
                    ? '✓ cuadra'
                    : cop(resumen.ultimo_arqueo.diferencia)}
                </span>
              </div>
            </div>
          )}
        </>
      )}

      <div className="flex gap-1 border-b border-gray-200">
        {([['movimientos', `Movimientos (${movimientos.length})`],
           ['prestamos', `Préstamos (${prestamos.length})`]] as const).map(([valor, etiqueta]) => (
          <button
            key={valor}
            onClick={() => setTab(valor)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === valor
                ? 'border-brand-600 text-brand-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {etiqueta}
          </button>
        ))}
      </div>

      {tab === 'movimientos' && (
        <div className="card p-0 divide-y divide-gray-100">
          {movimientos.map((m: any) => <FilaMovimiento key={m.id} mov={m} />)}
          {movimientos.length === 0 && (
            <div className="py-12 text-center text-gray-400">
              <Wallet size={36} className="mx-auto mb-2 text-gray-300" />
              <p className="font-medium text-gray-500">Sin movimientos</p>
              <p className="text-sm">Registra el primer ingreso o egreso.</p>
            </div>
          )}
        </div>
      )}

      {tab === 'prestamos' && (
        <div className="space-y-2">
          {prestamos.map((p: any) => (
            <FilaPrestamo key={p.id} prestamo={p} espacioId={espacioId!} />
          ))}
          {prestamos.length === 0 && (
            <div className="card py-12 text-center text-gray-400">
              <HandCoins size={36} className="mx-auto mb-2 text-gray-300" />
              <p className="font-medium text-gray-500">Sin préstamos</p>
              <p className="text-sm">Registra el dinero que has prestado.</p>
            </div>
          )}
        </div>
      )}

      {modal === 'movimiento' && (
        <ModalMovimiento espacioId={espacioId!} onClose={() => setModal(null)} />
      )}
      {modal === 'prestamo' && (
        <ModalPrestamo espacioId={espacioId!} onClose={() => setModal(null)} />
      )}
      {modal === 'arqueo' && (
        <ModalArqueo espacioId={espacioId!} saldoTeorico={saldoTeorico} onClose={() => setModal(null)} />
      )}
    </div>
  )
}
