import { useState } from 'react'
import { api } from '../api/client'
import { X, Eye, EyeOff, Check, ShieldCheck } from 'lucide-react'

const MIN_PASSWORD = 8

export default function CambiarPasswordModal(
  { onClose, forzado = false }: { onClose: () => void; forzado?: boolean },
) {
  const [actual, setActual] = useState('')
  const [nueva, setNueva] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [verClaves, setVerClaves] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [guardando, setGuardando] = useState(false)
  const [listo, setListo] = useState(false)

  const coinciden = nueva !== '' && nueva === confirmacion
  const suficienteLarga = nueva.length >= MIN_PASSWORD
  const puedeEnviar = actual !== '' && suficienteLarga && coinciden && nueva !== actual

  async function enviar(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setGuardando(true)
    try {
      const { data } = await api.post('/auth/cambiar-password', {
        password_actual: actual,
        password_nueva: nueva,
      })
      // El backend devuelve un token nuevo para no perder la sesion.
      localStorage.setItem('token', data.access_token)
      // El usuario guardado trae la marca de contraseña temporal; hay que
      // refrescarlo o la aplicación seguiría exigiendo el cambio.
      try {
        const { data: yo } = await api.get('/auth/me')
        localStorage.setItem('user', JSON.stringify(yo))
      } catch {
        // Si falla, recargar igual deja el estado consistente.
      }
      setListo(true)
      setTimeout(() => { forzado ? window.location.reload() : onClose() }, 1500)
    } catch (err: any) {
      const detalle = err?.response?.data?.detail
      setError(typeof detalle === 'string' ? detalle : 'No se pudo cambiar la contraseña.')
    } finally {
      setGuardando(false)
    }
  }

  if (listo) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
          <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
            <Check size={24} className="text-green-600" />
          </div>
          <h2 className="font-semibold text-gray-900">Contraseña actualizada</h2>
          <p className="text-sm text-gray-500 mt-1">
            Úsala la próxima vez que inicies sesión.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <form onSubmit={enviar} className="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} className="text-brand-600" />
            <h2 className="font-semibold text-gray-900">Cambiar contraseña</h2>
          </div>
          {!forzado && (
            <button type="button" onClick={onClose}>
              <X size={20} className="text-gray-400" />
            </button>
          )}
        </div>

        <div className="p-5 space-y-4">
          {forzado && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 text-sm text-yellow-800">
              Tu contraseña fue asignada por un administrador. Elige una propia
              para continuar.
            </div>
          )}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              {forzado ? 'Contraseña temporal *' : 'Contraseña actual *'}
            </label>
            <input
              type={verClaves ? 'text' : 'password'}
              className="input"
              required
              autoComplete="current-password"
              value={actual}
              onChange={(e) => setActual(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Contraseña nueva *
            </label>
            <input
              type={verClaves ? 'text' : 'password'}
              className="input"
              required
              autoComplete="new-password"
              value={nueva}
              onChange={(e) => setNueva(e.target.value)}
            />
            <p className={`text-xs mt-1 ${
              nueva === '' ? 'text-gray-500'
                : suficienteLarga ? 'text-green-600' : 'text-yellow-600'
            }`}>
              {nueva === '' || suficienteLarga
                ? `Mínimo ${MIN_PASSWORD} caracteres`
                : `Te faltan ${MIN_PASSWORD - nueva.length} caracteres`}
            </p>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Repite la contraseña nueva *
            </label>
            <input
              type={verClaves ? 'text' : 'password'}
              className="input"
              required
              autoComplete="new-password"
              value={confirmacion}
              onChange={(e) => setConfirmacion(e.target.value)}
            />
            {confirmacion !== '' && !coinciden && (
              <p className="text-xs text-red-600 mt-1">Las contraseñas no coinciden</p>
            )}
          </div>

          <button
            type="button"
            className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700"
            onClick={() => setVerClaves(!verClaves)}
          >
            {verClaves ? <EyeOff size={13} /> : <Eye size={13} />}
            {verClaves ? 'Ocultar contraseñas' : 'Mostrar contraseñas'}
          </button>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
          )}
        </div>

        <div className="flex gap-3 p-5 border-t border-gray-100">
          <button type="submit" className="btn-primary flex-1" disabled={!puedeEnviar || guardando}>
            {guardando ? 'Guardando...' : 'Cambiar contraseña'}
          </button>
          {!forzado && (
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancelar
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
