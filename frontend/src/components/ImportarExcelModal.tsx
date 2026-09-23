import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import {
  X, Upload, FileSpreadsheet, AlertTriangle, Check,
  PlusCircle, RefreshCw, MinusCircle,
} from 'lucide-react'

type Analisis = {
  filas: {
    fila: number
    nombre: string
    accion: 'crear' | 'actualizar' | 'sin_cambios' | 'ignorar'
    cambios: string[]
    alertas: { severidad: string; mensaje: string }[]
  }[]
  resumen: {
    leidas: number; crear: number; actualizar: number
    sin_cambios: number; ignorar: number; con_alertas: number
  }
  no_presentes: string[]
}

const ETIQUETA_ACCION: Record<string, { texto: string; clase: string; icono: any }> = {
  crear:       { texto: 'Nuevo',        clase: 'bg-green-100 text-green-700',  icono: PlusCircle },
  actualizar:  { texto: 'Cambia',       clase: 'bg-blue-100 text-blue-700',    icono: RefreshCw },
  sin_cambios: { texto: 'Igual',        clase: 'bg-gray-100 text-gray-500',    icono: Check },
  ignorar:     { texto: 'Se omite',     clase: 'bg-red-100 text-red-700',      icono: MinusCircle },
}

export default function ImportarExcelModal({ espacioId, onClose }: { espacioId: string; onClose: () => void }) {
  const qc = useQueryClient()
  const [archivo, setArchivo] = useState<File | null>(null)
  const [analisis, setAnalisis] = useState<Analisis | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resultado, setResultado] = useState<any>(null)
  const [soloCambios, setSoloCambios] = useState(true)

  async function enviar(ruta: string, file: File) {
    const form = new FormData()
    form.append('archivo', file)
    const { data } = await api.post(`/espacios/${espacioId}/inventario/${ruta}`, form)
    return data
  }

  async function seleccionar(file: File | null) {
    setError(null)
    setAnalisis(null)
    setArchivo(file)
    if (!file) return
    setCargando(true)
    try {
      setAnalisis(await enviar('analizar', file))
    } catch (err: any) {
      const d = err?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'No se pudo leer el archivo.')
    } finally {
      setCargando(false)
    }
  }

  async function confirmar() {
    if (!archivo) return
    setError(null)
    setCargando(true)
    try {
      setResultado(await enviar('importar', archivo))
      qc.invalidateQueries({ queryKey: ['insumos', espacioId] })
    } catch (err: any) {
      const d = err?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'No se pudo importar.')
    } finally {
      setCargando(false)
    }
  }

  const visibles = analisis?.filas.filter(
    (f) => !soloCambios || f.accion !== 'sin_cambios'
  ) ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[92vh] flex flex-col">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <FileSpreadsheet size={18} className="text-brand-600" />
            <h2 className="font-semibold text-gray-900">Importar desde Excel</h2>
          </div>
          <button onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>

        <div className="p-5 space-y-4 overflow-y-auto">
          {resultado ? (
            <div className="text-center py-6">
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
                <Check size={24} className="text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Importación completada</h3>
              <p className="text-sm text-gray-600 mt-1">
                {resultado.creados} productos creados · {resultado.actualizados} actualizados
              </p>
              {resultado.detalles?.length > 0 && (
                <div className="mt-4 text-left bg-gray-50 rounded-xl p-3 max-h-48 overflow-y-auto">
                  {resultado.detalles.map((d: string, i: number) => (
                    <div key={i} className="text-xs text-gray-600 py-0.5">{d}</div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <>
              <div>
                <label className="block border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-brand-400 hover:bg-brand-50/40 transition-colors">
                  <input
                    type="file"
                    accept=".xlsx,.xlsm"
                    className="hidden"
                    onChange={(e) => seleccionar(e.target.files?.[0] ?? null)}
                  />
                  <Upload size={24} className="mx-auto text-gray-400 mb-2" />
                  <div className="text-sm font-medium text-gray-700">
                    {archivo ? archivo.name : 'Elige tu archivo de Excel'}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {archivo ? 'Haz clic para cambiarlo' : 'Formato .xlsx, hasta 5 MB'}
                  </div>
                </label>
                <p className="text-xs text-gray-500 mt-2">
                  Descarga primero la plantilla desde el botón <strong>Exportar</strong> y trabaja sobre ella.
                  Nada se guarda hasta que revises los cambios y confirmes.
                </p>
              </div>

              {cargando && !analisis && (
                <div className="text-center py-6 text-gray-500 text-sm">Leyendo el archivo...</div>
              )}

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 flex gap-3">
                  <AlertTriangle size={17} className="text-red-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}

              {analisis && (
                <>
                  <div className="grid grid-cols-4 gap-2 text-center">
                    {[
                      ['Nuevos', analisis.resumen.crear, 'text-green-700'],
                      ['Cambian', analisis.resumen.actualizar, 'text-blue-700'],
                      ['Iguales', analisis.resumen.sin_cambios, 'text-gray-500'],
                      ['Alertas', analisis.resumen.con_alertas, 'text-orange-600'],
                    ].map(([etiqueta, valor, color]: any) => (
                      <div key={etiqueta} className="bg-gray-50 rounded-lg py-2">
                        <div className={`text-lg font-bold ${color}`}>{valor}</div>
                        <div className="text-xs text-gray-500">{etiqueta}</div>
                      </div>
                    ))}
                  </div>

                  {analisis.no_presentes.length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 text-xs text-blue-800">
                      <strong>{analisis.no_presentes.length} productos</strong> de la aplicación no están
                      en el archivo. No se van a tocar ni a borrar:{' '}
                      {analisis.no_presentes.slice(0, 5).join(', ')}
                      {analisis.no_presentes.length > 5 && ` y ${analisis.no_presentes.length - 5} más`}.
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-700">
                      Qué va a pasar ({visibles.length} de {analisis.resumen.leidas} filas)
                    </span>
                    <label className="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer">
                      <input type="checkbox" checked={soloCambios}
                        onChange={(e) => setSoloCambios(e.target.checked)} />
                      Ocultar los que no cambian
                    </label>
                  </div>

                  <div className="border border-gray-200 rounded-xl divide-y divide-gray-100 max-h-72 overflow-y-auto">
                    {visibles.map((f) => {
                      const conf = ETIQUETA_ACCION[f.accion]
                      const Icono = conf.icono
                      return (
                        <div key={f.fila} className="px-3 py-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className={`badge flex items-center gap-1 ${conf.clase}`}>
                              <Icono size={10} /> {conf.texto}
                            </span>
                            <span className="text-sm text-gray-900 font-medium">
                              {f.nombre || <em className="text-gray-400">sin nombre</em>}
                            </span>
                            <span className="text-xs text-gray-400">fila {f.fila}</span>
                          </div>
                          {f.cambios.length > 0 && (
                            <div className="text-xs text-gray-600 mt-1 ml-1">{f.cambios.join(' · ')}</div>
                          )}
                          {f.alertas.map((a, i) => (
                            <div key={i} className={`text-xs mt-1 ml-1 flex gap-1.5 ${
                              a.severidad === 'alta' ? 'text-red-700' : 'text-yellow-700'
                            }`}>
                              <AlertTriangle size={12} className="flex-shrink-0 mt-0.5" />
                              {a.mensaje}
                            </div>
                          ))}
                        </div>
                      )
                    })}
                    {visibles.length === 0 && (
                      <div className="py-6 text-center text-sm text-gray-400">
                        No hay cambios respecto a lo que ya está cargado.
                      </div>
                    )}
                  </div>

                  {analisis.resumen.con_alertas > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 flex gap-3">
                      <AlertTriangle size={17} className="text-yellow-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-yellow-800">
                        Hay {analisis.resumen.con_alertas} filas con advertencias. Puedes importar de
                        todas formas: los valores entran tal como los escribiste y las advertencias
                        quedan solo como aviso.
                      </p>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>

        <div className="flex gap-3 p-5 border-t border-gray-100">
          {resultado ? (
            <button className="btn-primary flex-1" onClick={onClose}>Listo</button>
          ) : (
            <>
              <button
                className="btn-primary flex-1"
                onClick={confirmar}
                disabled={!analisis || cargando ||
                  (analisis.resumen.crear + analisis.resumen.actualizar === 0)}
              >
                {cargando ? 'Importando...'
                  : analisis
                    ? `Aplicar ${analisis.resumen.crear + analisis.resumen.actualizar} cambios`
                    : 'Aplicar cambios'}
              </button>
              <button className="btn-secondary" onClick={onClose}>Cancelar</button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
