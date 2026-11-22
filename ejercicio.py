from abc import ABC, abstractmethod
from datetime import datetime
import logging


logging.basicConfig(
    filename='sistema_errores.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ErrorSistema(Exception):
    """Clase base para excepciones personalizadas del sistema."""
    pass

class ClienteInvalidoError(ErrorSistema):
    """Se lanza cuando los datos del cliente no son válidos."""
    pass

class ServicioNoDisponibleError(ErrorSistema):
    """Se lanza cuando un servicio no está disponible o no existe."""
    pass

class ReservaError(ErrorSistema):
    """Se lanza ante fallos al procesar una reserva."""
    pass


class EntidadBase(ABC):
    @abstractmethod
    def obtener_detalles(self):
        pass

class Cliente(EntidadBase):
    def __init__(self, cedula: str, nombre: str, correo: str):
        self.cedula = cedula
        self.nombre = nombre
        self.correo = correo

    @property
    def cedula(self):
        return self.__cedula

    @cedula.setter
    def cedula(self, valor):
        if not valor or not str(valor).isdigit() or len(str(valor)) < 6:
            logging.error(f"Intento de registro con cédula inválida: {valor}")
            raise ClienteInvalidoError(f"Cédula inválida: '{valor}'. Debe contener solo números y al menos 6 dígitos.")
        self.__cedula = valor

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            logging.error(f"Intento de registro con correo inválido: {valor}")
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self.__correo = valor

    def obtener_detalles(self):
        return f"Cliente: {self.nombre} | Cédula: {self.cedula} | Correo: {self.correo}"


class Servicio(ABC):
    def __init__(self, id_servicio: str, nombre: str, costo_base: float):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = True

    @abstractmethod
    def calcular_costo(self):
        pass

    def obtener_detalles(self):
        return f"Servicio: {self.nombre} (ID: {self.id_servicio}) - Costo Base: ${self.costo_base}"


class ReservaSala(Servicio):
    def __init__(self, id_servicio: str, nombre: str, costo_base: float, capacidad: int):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacidad

    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19):
        try:
            if descuento < 0 or impuesto < 0:
                raise ValueError("Los valores de descuento o impuesto no pueden ser negativos.")
            subtotal = self.costo_base * (1 - descuento)
            total = subtotal * (1 + impuesto)
            return round(total, 2)
        except Exception as e:
            logging.error(f"Error en cálculo de costo para Sala {self.nombre}: {e}")
            raise

    def obtener_detalles(self):
        return f"[Sala] {super().obtener_detalles()} | Capacidad: {self.capacidad} personas"


class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio: str, nombre: str, costo_base: float, horas: int):
        super().__init__(id_servicio, nombre, costo_base)
        self.horas = horas

    def calcular_costo(self, tarifa_hora: float = 15.0):
        return round(self.costo_base + (self.horas * tarifa_hora), 2)

    def obtener_detalles(self):
        return f"[Equipo] {super().obtener_detalles()} | Horas: {self.horas}"


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio: str, nombre: str, costo_base: float, nivel_experticia: str):
        super().__init__(id_servicio, nombre, costo_base)
        self.nivel_experticia = nivel_experticia

    def calcular_costo(self, bono_extra: float = 0.0):
        return round(self.costo_base + bono_extra, 2)

    def obtener_detalles(self):
        return f"[Asesoría] {super().obtener_detalles()} | Nivel: {self.nivel_experticia}"


class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.estado = "Pendiente"

    def procesar_reserva(self):
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio {self.servicio.nombre} no se encuentra disponible.")
            
    
            costo_final = self.servicio.calcular_costo()
            self.estado = "Confirmada"
            logging.info(f"Reserva {self.id_reserva} procesada exitosamente. Total: ${costo_final}")
            print(f" ÉXITO Reserva {self.id_reserva} confirmada para {self.cliente.nombre}. Total a pagar: ${costo_final}")
            
        except ServicioNoDisponibleError as sne:
            self.estado = "Fallida"
            logging.warning(f"Advertencia en reserva {self.id_reserva}: {sne}")
            print(f" ADVERTENCIA {sne}")
        except Exception as e:
            self.estado = "Error"
            logging.error(f"Error crítico al procesar reserva {self.id_reserva}: {e}", exc_info=True)
            print(f" ERROR CRÍTICO No se pudo procesar la reserva {self.id_reserva}.")
            raise ReservaError(f"Falla general en la reserva {self.id_reserva}") from e
        else:
            print(f"   -> Operación validada correctamente sin excepciones imprevistas.")
        finally:
            print(f"   -> LOG Transacción de reserva {self.id_reserva} finalizada con estado: {self.estado}\n")

    def cancelar_reserva(self):
        self.estado = "Cancelada"
        logging.info(f"Reserva {self.id_reserva} cancelada.")
        print(f"🔄 Reserva {self.id_reserva} cancelada correctamente.")

# SIMULACIÓN DE 10 OPERACIONES
if __name__ == "__main__":
    print("INICIANDO SIMULACIÓN DEL SISTEMA SOFTWARE FJ \n")
    
    sala_vip = ReservaSala("S001", "Sala Ejecutiva", 100.0, 15)
    equipo_dev = AlquilerEquipo("E001", "MacBook Pro M3", 50.0, 4)
    asesoria_ti = AsesoriaEspecializada("A001", "Arquitectura Cloud", 200.0, "Senior")
    
    sala_mantenimiento = ReservaSala("S002", "Sala Mantenimiento", 80.0, 10)
    sala_mantenimiento.disponible = False

    operaciones = [
        lambda: Reserva("R-001", Cliente("10101234", "Carlos Pérez", "carlos@mail.com"), sala_vip).procesar_reserva(),
        
        lambda: Reserva("R-002", Cliente("ABC123XYZ", "Ana Gomez", "ana@mail.com"), equipo_dev).procesar_reserva(),
        
        lambda: Reserva("R-003", Cliente("10105678", "María Rodríguez", "maria@mail.com"), equipo_dev).procesar_reserva(),
        
        lambda: Reserva("R-004", Cliente("10109999", "Pedro Picapiedra", "correo_malo.com"), asesoria_ti).procesar_reserva(),
        
        lambda: Reserva("R-005", Cliente("55443322", "Lucía Benítez", "lucia@mail.com"), asesoria_ti).procesar_reserva(),
        
        lambda: Reserva("R-006", Cliente("77889900", "Jorge Mario", "jorge@mail.com"), sala_mantenimiento).procesar_reserva(),
        
        lambda: Reserva("R-007", Cliente("33221144", "Sofía Vergara", "sofia@mail.com"), sala_vip).procesar_reserva(),
        
        lambda: Reserva("R-008", Cliente("123", "Esteban Quito", "esteban@mail.com"), equipo_dev).procesar_reserva(),
        
        lambda: Reserva("R-009", Cliente("99887766", "Valeria Morales", "valeria@mail.com"), equipo_dev).procesar_reserva(),
        
        lambda: Reserva("R-010", Cliente("11223344", "Andrés Felipe", "andres@mail.com"), asesoria_ti).procesar_reserva()
    ]

    for i, op in enumerate(operaciones, start=1):
        print(f"- OPERACIÓN NÚMERO {i} -")
        try:
            op()
        except Exception as ex:
            print(f"-> Excepción capturada en bloque principal de prueba: {ex}\n")

    print(" SIMULACIÓN FINALIZADA CON ÉXITO ")