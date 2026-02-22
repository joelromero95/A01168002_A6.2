# A01168002_A6.2 — Ejercicio de programación 3 y pruebas unitarias (Reservation System)

Repositorio de la Actividad **6.2** del curso **Pruebas de software y aseguramiento de la calidad**.  
Implementa un sistema de reservaciones con persistencia en archivos JSON y pruebas unitarias con `unittest`, cumpliendo **PEP 8**, **flake8** y **pylint**, además de **cobertura de líneas ≥ 85%**.

---

## Objetivos

- Explicar y aplicar fundamentos del desarrollo de **pruebas unitarias**.
- Implementar pruebas unitarias siguiendo **mejores prácticas** (aislamiento, repetibilidad, aserciones claras).
- Verificar calidad del código con herramientas de análisis estático (**flake8** y **pylint**).
- Validar manejo correcto de **casos negativos** (datos inválidos en archivos sin detener ejecución).

---

## Descripción del sistema

El sistema contiene los siguientes módulos (carpeta `source/`):

- `customer.py`: Gestión de clientes (**Create, Delete, Display, Modify**).
- `hotel.py`: Gestión de hoteles (**Create, Delete, Display, Modify**) y control de habitaciones (**reserve/cancel**).
- `reservation.py`: Gestión de reservaciones (**Create/Cancel/Display**) entre Customer y Hotel.
- `storage.py`: Persistencia en JSON y manejo de errores de archivos/datos inválidos (imprime en consola y continúa).
- `exceptions.py`: Excepciones de dominio (`ValidationError`, `NotFoundError`, etc.).

Persistencia en archivos JSON (carpeta `data/`):
- `data/customers.json`
- `data/hotels.json`
- `data/reservations.json`

> Nota: Los tests **no** dependen de `data/` real. Se ejecutan de forma aislada creando archivos temporales para asegurar repetibilidad.

---

## Estructura del repositorio

```
A01168002_A6.2/
  data/
    customers.json
    hotels.json
    reservations.json
  htmlcov/
    (reporte HTML de coverage)
  results/
    coverage_unittest_ConsoleOutput.txt
    coverageReport.png
    flake8Results.png
    pylintResults.png
    test_customer_ConsoleOutput.txt
    test_hotel_ConsoleOutput.txt
    test_reservation_ConsoleOutput.txt
    test_storage_ConsoleOutput.txt
  source/
    __init__.py
    customer.py
    exceptions.py
    hotel.py
    reservation.py
    storage.py
  tests/
    fixtures/
    test_customer.py
    test_hotel.py
    test_reservation.py
    test_storage.py
```

---

## Requisitos

- Python 3.x
- Paquetes:
  - `flake8`
  - `pylint`
  - `coverage`

Instalación recomendada:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install flake8 pylint coverage
```

---

## Ejecución de pruebas unitarias (unittest)

Ejecutar todos los tests:

```bash
python -m unittest discover -s tests -v
```

Ejecutar un archivo específico:

```bash
python -m unittest tests.test_customer -v
python -m unittest tests.test_hotel -v
python -m unittest tests.test_reservation -v
python -m unittest tests.test_storage -v
```

Los outputs de consola de ejecución se documentan en:
- `results/test_customer_ConsoleOutput.txt`
- `results/test_hotel_ConsoleOutput.txt`
- `results/test_reservation_ConsoleOutput.txt`
- `results/test_storage_ConsoleOutput.txt`

---

## Cobertura de código (coverage ≥ 85%)

Generar y mostrar reporte en consola:

```bash
coverage run -m unittest discover -s tests
coverage report -m
```

Generar reporte HTML:

```bash
coverage html
```

El reporte HTML se guarda en la carpeta:
- `htmlcov/`

Evidencia adicional:
- `results/coverage_unittest_ConsoleOutput.txt`
- `results/coverageReport.png`

---

## Análisis estático

### flake8 (PEP 8)

```bash
flake8 source tests
```

Evidencia:
- `results/flake8Results.png`

### pylint

```bash
pylint source tests
```

Evidencia:
- `results/pylintResults.png`

---

## Manejo de casos negativos (datos inválidos)

El sistema está diseñado para manejar datos inválidos **sin detener la ejecución**, especialmente en `storage.py` y los validadores de cada repositorio.  
Cuando se detecta un archivo inexistente/corrupto o registros inválidos, el programa:

- Imprime el error/advertencia en consola.
- Ignora registros inválidos cuando aplica.
- Continúa la ejecución devolviendo una estructura segura (por ejemplo, lista vacía `[]`).

### Ejemplos de casos negativos cubiertos en pruebas

- Archivo JSON no existe → se usa `[]` y se imprime advertencia.
- Archivo JSON vacío o solo espacios → se usa `[]`.
- JSON corrupto → se usa `[]` y se imprime error.
- JSON válido pero no es lista → se usa `[]`.
- Lista con elementos no diccionario → se ignoran e imprime error por índice.
- Intentar reservar sin disponibilidad → `ValidationError`.
- Cancelar reservación inexistente → `NotFoundError`.
- Modificar/eliminar recursos inexistentes → `NotFoundError`.

> Se incluyen al menos **5 casos negativos** por módulo en los tests (según el componente).

---

## Notas de implementación

- Se sigue el estándar de estilo **PEP 8** y se valida con `flake8`.
- Se valida calidad con `pylint`.
- Las pruebas están diseñadas para ser:
  - **Aisladas** (uso de `tempfile` para archivos temporales).
  - **Determinísticas** (no dependen del estado de `data/`).
  - **Claras** (1 comportamiento por test).
- Los comentarios del código están en español para facilitar comprensión y evaluación.

---

## Evidencias incluidas

En la carpeta `results/` se documentan:
- Salidas de consola de pruebas unitarias.
- Evidencia de cobertura y cumplimiento de herramientas de análisis estático:
  - Coverage (consola y/o captura)
  - flake8 (captura)
  - pylint (captura)

---

## Autor

- Joel Romero, A01168002
