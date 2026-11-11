# =============================================================
# Módulo 01 – Ejercicio 02: Variables y Tipos de Datos en Python
# =============================================================
# En Python, una variable es un nombre que apunta a un valor
# almacenado en memoria. No necesitas declarar el tipo de la
# variable: Python lo infiere automáticamente.
#
# Tipos básicos (primitivos):
#   str   -> cadenas de texto       "hola"
#   int   -> números enteros        42
#   float -> números decimales      3.14
#   bool  -> verdadero / falso      True / False
#
# Tipos de colección:
#   list  -> lista ordenada y mutable          [1, 2, 3]
#   tuple -> lista ordenada e inmutable        (1, 2, 3)
#   dict  -> pares clave-valor                 {"a": 1}
#   set   -> conjunto sin duplicados           {1, 2, 3}
# =============================================================


# ---------------------------
# 1. TIPOS PRIMITIVOS
# ---------------------------

# str – cadena de texto
curso = "RAG-LAB"
descripcion = "Laboratorio de Recuperación Aumentada con IA"

# int – número entero
duracion_horas = 8
num_modulos = 5

# float – número de punto flotante
avance = 0.25          # 25 % completado
precio_usd = 199.99

# bool – booleano
entorno_listo = True
es_gratuito = False

print("=" * 45)
print("  TIPOS PRIMITIVOS")
print("=" * 45)
print(f"Curso         : {curso}  -> tipo: {type(curso)}")
print(f"Descripción   : {descripcion}  -> tipo: {type(descripcion)}")
print(f"Duración      : {duracion_horas} horas  -> tipo: {type(duracion_horas)}")
print(f"Módulos       : {num_modulos}  -> tipo: {type(num_modulos)}")
print(f"Avance        : {avance} ({avance * 100:.0f}%)  -> tipo: {type(avance)}")
print(f"Precio        : ${precio_usd}  -> tipo: {type(precio_usd)}")
print(f"Entorno listo : {entorno_listo}  -> tipo: {type(entorno_listo)}")
print(f"Es gratuito   : {es_gratuito}  -> tipo: {type(es_gratuito)}")


# ---------------------------
# 2. TIPO LIST (lista)
# ---------------------------
# Una lista puede contener cualquier combinación de tipos.
# Se define con corchetes [ ] y es mutable (se puede modificar).

herramientas = ["Python", "PyCharm", "Git", "GitHub"]

# Agregar un elemento al final
herramientas.append("OpenRouter")

# Acceder por índice (empieza en 0)
primera = herramientas[0]
ultima  = herramientas[-1]   # índice -1 = último elemento

print("\n" + "=" * 45)
print("  LISTAS")
print("=" * 45)
print(f"Herramientas  : {herramientas}")
print(f"Primera       : {primera}")
print(f"Última        : {ultima}")
print(f"Total items   : {len(herramientas)}")
print("Recorriendo la lista:")
for herramienta in herramientas:
    print(f"  - {herramienta}")


# ---------------------------
# 3. TIPO TUPLE (tupla)
# ---------------------------
# Igual que una lista, pero INMUTABLE: no se puede cambiar
# después de crearse. Útil para valores que no deben modificarse.

coordenadas = (19.4326, -99.1332)   # latitud y longitud de CDMX
semestre    = (2026, 1)             # año, primer semestre

print("\n" + "=" * 45)
print("  TUPLAS")
print("=" * 45)
print(f"Coordenadas   : {coordenadas}  -> lat={coordenadas[0]}, lon={coordenadas[1]}")
print(f"Semestre      : año={semestre[0]}, período={semestre[1]}")


# ---------------------------
# 4. TIPO DICT (diccionario)
# ---------------------------
# Almacena pares clave-valor. Las claves deben ser únicas.
# Se define con llaves { } y es mutable.

alumno = {
    "nombre": "Ana López",
    "edad": 28,
    "modulo_actual": 1,
    "aprobado": False,
}

# Acceder a un valor por su clave
print("\n" + "=" * 45)
print("  DICCIONARIOS")
print("=" * 45)
print(f"Alumno        : {alumno}")
print(f"Nombre        : {alumno['nombre']}")
print(f"Edad          : {alumno['edad']}")

# Actualizar un valor
alumno["aprobado"] = True
alumno["calificacion"] = 9.5          # agregar nueva clave
print(f"Alumno (actualizado): {alumno}")

# Recorrer clave-valor
print("Detalles del alumno:")
for clave, valor in alumno.items():
    print(f"  {clave}: {valor}")


# ---------------------------
# 5. TIPO SET (conjunto)
# ---------------------------
# Colección sin duplicados y sin orden garantizado.
# Útil para operaciones de conjuntos (unión, intersección, etc.)

tecnologias_a = {"Python", "SQL", "Docker", "Git"}
tecnologias_b = {"Python", "JavaScript", "Docker", "React"}

print("\n" + "=" * 45)
print("  CONJUNTOS (SET)")
print("=" * 45)
print(f"Set A              : {tecnologias_a}")
print(f"Set B              : {tecnologias_b}")
print(f"Interseccion (A&B)  : {tecnologias_a & tecnologias_b}")
print(f"Union        (A|B)  : {tecnologias_a | tecnologias_b}")
print(f"Diferencia   (A-B)  : {tecnologias_a - tecnologias_b}")


# ---------------------------
# 6. CONVERSIÓN DE TIPOS (casting)
# ---------------------------
# Puedes convertir entre tipos con int(), float(), str(), bool().

numero_texto = "42"
numero_int   = int(numero_texto)      # str -> int
numero_float = float(numero_texto)    # str -> float
texto_numero = str(numero_int)        # int -> str

print("\n" + "=" * 45)
print("  CONVERSIÓN DE TIPOS (CASTING)")
print("=" * 45)
print(f"Original (str) : '{numero_texto}'  -> tipo: {type(numero_texto)}")
print(f"-> int          : {numero_int}       -> tipo: {type(numero_int)}")
print(f"-> float        : {numero_float}     -> tipo: {type(numero_float)}")
print(f"-> str de nuevo : '{texto_numero}'  -> tipo: {type(texto_numero)}")

# Valores "falsy" vs "truthy"
print("\nValores falsy (evalúan a False):")
for val in [0, 0.0, "", [], {}, None, False]:
    print(f"  bool({val!r:10}) = {bool(val)}")
