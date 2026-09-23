/**
 * Cómo se nombran las cosas según el tipo de negocio.
 *
 * El modelo de datos es el mismo para todos: un insumo es lo que se compra y un
 * servicio es lo que se arma con varios insumos. Lo único que cambia es la
 * palabra, porque una IPS habla de insumos y procedimientos, y una distribuidora
 * de productos y combos. Usar el vocabulario del cliente evita que tenga que
 * traducir mentalmente cada pantalla.
 */

export type TipoNegocio = 'salud' | 'comercio'

export type Terminos = {
  insumo: string
  insumos: string
  servicio: string
  servicios: string
  paquete: string
  paquetes: string
  nuevoInsumo: string
  nuevoServicio: string
  descripcionServicios: string
  componentes: string
}

const SALUD: Terminos = {
  insumo: 'Insumo',
  insumos: 'Inventario',
  servicio: 'Servicio',
  servicios: 'Servicios',
  paquete: 'Paquete',
  paquetes: 'Paquetes',
  nuevoInsumo: 'Nuevo insumo',
  nuevoServicio: 'Nuevo servicio',
  descripcionServicios: 'procedimientos',
  componentes: 'Insumos del procedimiento',
}

const COMERCIO: Terminos = {
  insumo: 'Producto',
  insumos: 'Inventario',
  servicio: 'Combo',
  servicios: 'Combos',
  paquete: 'Promoción',
  paquetes: 'Promociones',
  nuevoInsumo: 'Nuevo producto',
  nuevoServicio: 'Nuevo combo',
  descripcionServicios: 'combos',
  componentes: 'Productos del combo',
}

const POR_TIPO: Record<TipoNegocio, Terminos> = {
  salud: SALUD,
  comercio: COMERCIO,
}

/** Lee el tipo del espacio activo. Ante la duda asume 'salud', que es el original. */
export function tipoNegocioActual(): TipoNegocio {
  try {
    const guardado = localStorage.getItem('espacio')
    if (guardado) {
      const tipo = JSON.parse(guardado)?.tipo_negocio
      if (tipo === 'comercio' || tipo === 'salud') return tipo
    }
  } catch {
    // Un localStorage corrupto o bloqueado no debe tumbar la interfaz.
  }
  return 'salud'
}

export function useTerminos(): Terminos {
  return POR_TIPO[tipoNegocioActual()]
}
