import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import {
  Plus, X, KeyRound, ChevronLeft, Shield, Building2,
  Copy, Check, UserX, UserCheck, AlertTriangle,
} from 'lucide-react'

function ModalNuevoUsuario({ empresas, onClose }: { empresas: any[]; onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    email: '', password: '', rol: 'empresa', empresa_id: empresas[0]?.id ?? '',
  })
  const [error, setError] = useState<string | null>(null)

  const mut = useMutation({
    mutationFn: (data: any) => api.post('/usuarios', data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['usuarios'] }); onClose() },
    onError: (err: any) => {
      const d = err?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'No se pudo crear el usuario.')
    },
  })

  function enviar(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    mut.mutate({
      email: form.email.trim().toLowerCase(),
      password: form.password,
      rol: form.rol,
      empresa_id: form.rol === 'empresa' ? form.empresa_id : null,
      debe_cambiar_password: true,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <form onSubmit={enviar} className="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Nuevo usuario</h2>
          <button type="button" onClick={onClose}><X size={20} className="text-gray-400" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Correo *</label>
            <input type="email" className="input" required placeholder="persona@empresa.co"
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Contraseña inicial *</label>
            <input className="input" required minLength={8} placeholder="Mínimo 8 caracteres"
              value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <p className="text-xs text-gray-500 mt-1">
              Se le pedirá cambiarla la primera vez que entre.
            </p>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Rol *</label>
            <select className="input" value={form.rol}
              onChange={(e) => setForm({ ...form, rol: e.target.value })}>
              <option value="empresa">Empresa — usa su inventario</option>
              <option value="superadmin">Superadmin — administra todo</option>
            </select>
          </div>
          {form.rol === 'empresa' && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Empresa *</label>
              <select className="input" required value={form.empresa_id}
                onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}>
                <option value="">Seleccionar...</option>
                {empresas.map((e: any) => <option key={e.id} value={e.id}>{e.nombre}</option>)}
              </select>
            </div>
          )}
          {error && <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>}
        </div>
        <div className="flex gap-3 p-5 border-t border-gray-100">
          <button type="submit" className="btn-primary flex-1" disabled={mut.isPending}>
            {mut.isPending ? 'Creando...' : 'Crear usuario'}
          </button>
          <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}

function ModalPasswordTemporal({ datos, onClose }: { datos: any; onClose: () => void }) {
  const [copiado, setCopiado] = useState(false)

  async function copiar() {
    try {
      await navigator.clipboard.writeText(datos.password_temporal)
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    } catch {
      // Si el navegador bloquea el portapapeles, la clave sigue visible en pantalla.
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div className="p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">Contraseña temporal</h2>
          <p className="text-sm text-gray-500 mt-0.5">{datos.email}</p>
        </div>
        <div className="p-5 space-y-4">
          <div className="bg-brand-50 border border-brand-200 rounded-xl p-4 text-center">
            <div className="font-mono text-xl font-bold text-brand-800 tracking-wider break-all">
              {datos.password_temporal}
            </div>
            <button
              onClick={copiar}
              className="mt-3 text-xs text-brand-600 hover:underline flex items-center gap-1 mx-auto"
            >
              {copiado ? <><Check size={13} /> Copiada</> : <><Copy size={13} /> Copiar</>}
            </button>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 flex gap-3">
            <AlertTriangle size={17} className="text-yellow-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-yellow-800">
              Cópiala ahora: no se vuelve a mostrar. Al entrar con ella, la persona
              tendrá que elegir una contraseña propia.
            </p>
          </div>
        </div>
        <div className="p-5 border-t border-gray-100">
          <button className="btn-primary w-full" onClick={onClose}>Listo</button>
        </div>
      </div>
    </div>
  )
}

function FilaUsuario({ usuario, esUnoMismo }: { usuario: any; esUnoMismo: boolean }) {
  const qc = useQueryClient()
  const [temporal, setTemporal] = useState<any>(null)
  const [confirmando, setConfirmando] = useState(false)

  const restablecer = useMutation({
    mutationFn: () => api.post(`/usuarios/${usuario.id}/restablecer-password`).then((r) => r.data),
    onSuccess: (datos) => {
      setTemporal(datos)
      setConfirmando(false)
      qc.invalidateQueries({ queryKey: ['usuarios'] })
    },
  })

  const alternarActivo = useMutation({
    mutationFn: () => api.put(`/usuarios/${usuario.id}`, { activo: !usuario.activo }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['usuarios'] }),
  })

  return (
    <>
      <div className={`card space-y-2 ${!usuario.activo ? 'opacity-60' : ''}`}>
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-medium text-gray-900 break-all">{usuario.email}</span>
              {esUnoMismo && <span className="badge bg-brand-100 text-brand-700">Tú</span>}
              {!usuario.activo && <span className="badge bg-red-100 text-red-700">Inactivo</span>}
              {usuario.debe_cambiar_password && (
                <span className="badge bg-yellow-100 text-yellow-700">Clave temporal</span>
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1 flex items-center gap-1.5 flex-wrap">
              {usuario.rol === 'superadmin' ? (
                <><Shield size={12} /> Superadmin</>
              ) : (
                <><Building2 size={12} /> {usuario.empresa_nombre ?? 'Sin empresa'}</>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3 flex-shrink-0">
            {!confirmando && (
              <button
                className="text-xs text-brand-600 hover:underline flex items-center gap-1"
                onClick={() => setConfirmando(true)}
              >
                <KeyRound size={13} /> Restablecer clave
              </button>
            )}
            {!esUnoMismo && (
              <button
                className={`text-xs flex items-center gap-1 ${
                  usuario.activo ? 'text-red-500 hover:text-red-700' : 'text-green-600 hover:text-green-800'
                }`}
                onClick={() => alternarActivo.mutate()}
                disabled={alternarActivo.isPending}
              >
                {usuario.activo ? <><UserX size={13} /> Desactivar</> : <><UserCheck size={13} /> Activar</>}
              </button>
            )}
          </div>
        </div>

        {confirmando && (
          <div className="border-t border-gray-100 pt-2 space-y-2">
            <p className="text-xs text-gray-600">
              Se genera una contraseña nueva y la anterior deja de funcionar de inmediato.
            </p>
            <div className="flex gap-2">
              <button className="btn-primary text-xs py-1 px-3"
                onClick={() => restablecer.mutate()} disabled={restablecer.isPending}>
                {restablecer.isPending ? 'Generando...' : 'Generar contraseña'}
              </button>
              <button className="btn-secondary text-xs py-1 px-3" onClick={() => setConfirmando(false)}>
                Cancelar
              </button>
            </div>
          </div>
        )}
      </div>

      {temporal && <ModalPasswordTemporal datos={temporal} onClose={() => setTemporal(null)} />}
    </>
  )
}

export default function UsuariosPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [modal, setModal] = useState(false)

  const { data: usuarios = [], isLoading } = useQuery({
    queryKey: ['usuarios'],
    queryFn: () => api.get('/usuarios').then((r) => r.data),
  })

  const { data: empresas = [] } = useQuery({
    queryKey: ['empresas'],
    queryFn: () => api.get('/empresas').then((r) => r.data),
  })

  const esSuperadmin = user?.rol === 'superadmin'

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-3xl mx-auto space-y-5">
        <button
          onClick={() => navigate('/seleccionar-espacio')}
          className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <ChevronLeft size={16} /> Volver
        </button>

        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Usuarios</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {esSuperadmin
                ? 'Crea cuentas y restablece contraseñas olvidadas'
                : 'Cuentas de tu empresa'}
            </p>
          </div>
          {esSuperadmin && (
            <button className="btn-primary flex items-center gap-2" onClick={() => setModal(true)}>
              <Plus size={16} /> Nuevo usuario
            </button>
          )}
        </div>

        {isLoading && <div className="text-center py-8 text-gray-500">Cargando...</div>}

        <div className="space-y-3">
          {usuarios.map((u: any) => (
            <FilaUsuario key={u.id} usuario={u} esUnoMismo={u.id === user?.id} />
          ))}
        </div>

        {modal && (
          <ModalNuevoUsuario empresas={empresas} onClose={() => setModal(false)} />
        )}
      </div>
    </div>
  )
}
