import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { RotateCcw, X, Check, AlertTriangle } from 'lucide-react'

/**
 * Restaura el ambiente de demostracion. Se renderiza solo cuando la sesion es la
 * cuenta demo; el backend vuelve a verificarlo, asi que no depende de la interfaz.
 */
export default function BotonRestaurarDemo() {
  const qc = useQueryClient()
  const [confirmando, setConfirmando] = useState(false)
  const [restaurando, setRestaurando] = useState(false)
  const [listo, setListo] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { data } = useQuery({
    queryKey: ['es-demo'],
    queryFn: () => api.get('/demo/es-demo').then((r) => r.data),
    staleTime: Infinity,
  })

  if (!data?.es_demo) return null

  async function restaurar() {
    setError(null)
    setRestaurando(true)
    try {
      await api.post('/demo/restaurar')
      // El espacio se recrea con otro id, asi que hay que soltar el guardado.
      localStorage.removeItem('espacio')
      setListo(true)
      setTimeout(() => { window.location.href = '/seleccionar-espacio' }, 1500)
    } catch (err: any) {
      const detalle = err?.response?.data?.detail
      setError(typeof detalle === 'string' ? detalle : 'No se pudo restaurar.')
      setRestaurando(false)
    }
  }

  return (
    <>
      <button
        onClick={() => setConfirmando(true)}
        className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 w-full"
      >
        <RotateCcw size={18} />
        Restaurar demo
      </button>

      {confirmando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md">
            {listo ? (
              <div className="p-8 text-center">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
                  <Check size={24} className="text-green-600" />
                </div>
                <h2 className="font-semibold text-gray-900">Demo restaurada</h2>
                <p className="text-sm text-gray-500 mt-1">Volviendo al inicio...</p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between p-5 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <RotateCcw size={18} className="text-brand-600" />
                    <h2 className="font-semibold text-gray-900">Restaurar demostración</h2>
                  </div>
                  <button onClick={() => setConfirmando(false)} disabled={restaurando}>
                    <X size={20} className="text-gray-400" />
                  </button>
                </div>

                <div className="p-5 space-y-3">
                  <p className="text-sm text-gray-600">
                    Devuelve el ambiente a su estado original: 12 productos, 3 combos
                    y tres meses de movimientos de caja.
                  </p>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 flex gap-3">
                    <AlertTriangle size={17} className="text-yellow-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-yellow-800">
                      Todo lo que se haya creado o modificado en la demo se pierde.
                      Solo afecta a esta cuenta de prueba.
                    </p>
                  </div>
                  {error && <p className="text-sm text-red-600">{error}</p>}
                </div>

                <div className="flex gap-3 p-5 border-t border-gray-100">
                  <button className="btn-primary flex-1" onClick={restaurar} disabled={restaurando}>
                    {restaurando ? 'Restaurando...' : 'Sí, restaurar'}
                  </button>
                  <button className="btn-secondary" onClick={() => setConfirmando(false)} disabled={restaurando}>
                    Cancelar
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  )
}
