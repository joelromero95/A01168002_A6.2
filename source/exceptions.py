"""Excepciones de dominio para el sistema de reservaciones."""


class NotFoundError(Exception):
    """Se lanza cuando no se encuentra un recurso."""


class ValidationError(Exception):
    """Se lanza cuando los datos no cumplen validaciones."""


class PersistenceError(Exception):
    """Se lanza cuando ocurre un error de lectura/escritura persistente."""