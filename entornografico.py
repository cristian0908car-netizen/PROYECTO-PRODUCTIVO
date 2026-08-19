import sqlite3
import os
import hashlib


# ==========================================================
# BASE DE DATOS
# ==========================================================

db = sqlite3.connect("agenda_ade.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS actividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    tipo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT NOT NULL
)
""")

db.commit()


# ==========================================================
# COLORES
# ==========================================================

AZUL = "\033[38;5;25m"
VERDE = "\033[92m"
ROJO = "\033[91m"
AMARILLO = "\033[93m"
BLANCO = "\033[97m"
GRIS = "\033[90m"
RESET = "\033[0m"
NEGRITA = "\033[1m"


# ==========================================================
# FUNCIONES GENERALES
# ==========================================================

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def encabezado(texto):

    limpiar()

    print(f"{AZUL}{'=' * 60}{RESET}")

    print(
        f"{AZUL}{NEGRITA}"
        "       📚 ADE - AGENDA DIGITAL ESCOLAR"
        f"{RESET}"
    )

    print(f"{AZUL}{'=' * 60}{RESET}")

    print(
        f"\n{VERDE}{NEGRITA}"
        f"{texto}"
        f"{RESET}"
    )

    print(
        f"{GRIS}{'-' * 60}{RESET}\n"
    )


def encriptar(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ==========================================================
# CREAR ADMIN
# ==========================================================

def crear_admin():

    cursor.execute(
        "SELECT id FROM usuarios WHERE usuario='admin'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
        INSERT INTO usuarios
        (nombre, usuario, password, rol)
        VALUES (?, ?, ?, ?)
        """, (
            "Profesor Administrador",
            "admin",
            encriptar("1234"),
            "admin"
        ))

        db.commit()


# ==========================================================
# REGISTRARSE
# ==========================================================

def registrarse():

    while True:

        encabezado("📝 REGISTRO")

        print("1. 👨‍🎓 Registrarse como estudiante")
        print("2. 👨‍🏫 Registrarse como profesor")
        print("0. ↩️ Volver")

        opcion = input("\nOpción: ").strip()

        if opcion == "0":
            return

        elif opcion == "1":

            rol = "usuario"
            nombre_rol = "Estudiante"
            break

        elif opcion == "2":

            rol = "admin"
            nombre_rol = "Profesor"
            break

        else:

            print(
                f"\n{ROJO}"
                "Opción inválida."
                f"{RESET}"
            )


    encabezado(
        f"📝 REGISTRO DE {nombre_rol.upper()}"
    )

    print("Escribe 0 en cualquier campo para volver.\n")


    nombre = input(
        "Nombre completo: "
    ).strip()

    if nombre == "0":
        return

    if not nombre:

        print(
            f"\n{ROJO}"
            "El nombre es obligatorio."
            f"{RESET}"
        )

        return


    usuario = input(
        "Nombre de usuario: "
    ).strip()

    if usuario == "0":
        return

    if not usuario:

        print(
            f"\n{ROJO}"
            "El usuario es obligatorio."
            f"{RESET}"
        )

        return


    password = input(
        "Contraseña: "
    ).strip()

    if password == "0":
        return

    if not password:

        print(
            f"\n{ROJO}"
            "La contraseña es obligatoria."
            f"{RESET}"
        )

        return


    confirmar = input(
        "Confirmar contraseña: "
    ).strip()

    if confirmar == "0":
        return


    if password != confirmar:

        print(
            f"\n{ROJO}"
            "Las contraseñas no coinciden."
            f"{RESET}"
        )

        return


    # ------------------------------------------------------
    # CLAVE DEL PROFESOR
    # ------------------------------------------------------

    if rol == "admin":

        clave = input(
            "Clave de autorización del profesor: "
        ).strip()

        if clave == "0":
            return

        if clave != "1234":

            print(
                f"\n{ROJO}"
                "Clave de profesor incorrecta."
                f"{RESET}"
            )

            return


    # ------------------------------------------------------
    # GUARDAR
    # ------------------------------------------------------

    try:

        cursor.execute("""
        INSERT INTO usuarios
        (nombre, usuario, password, rol)
        VALUES (?, ?, ?, ?)
        """, (
            nombre,
            usuario,
            encriptar(password),
            rol
        ))

        db.commit()

        print(
            f"\n{VERDE}"
            f"✓ Cuenta de {nombre_rol} creada correctamente."
            f"{RESET}"
        )

    except sqlite3.IntegrityError:

        print(
            f"\n{ROJO}"
            "Ese nombre de usuario ya existe."
            f"{RESET}"
        )


# ==========================================================
# INICIAR SESIÓN
# ==========================================================

def iniciar_sesion():

    encabezado("🔐 INICIAR SESIÓN")

    print("Escribe 0 para volver.\n")


    usuario = input(
        "Usuario: "
    ).strip()

    if usuario == "0":
        return


    password = input(
        "Contraseña: "
    ).strip()

    if password == "0":
        return


    cursor.execute("""
    SELECT id, nombre, usuario, rol
    FROM usuarios
    WHERE usuario=? AND password=?
    """, (
        usuario,
        encriptar(password)
    ))


    datos = cursor.fetchone()


    if datos is None:

        print(
            f"\n{ROJO}"
            "Usuario o contraseña incorrectos."
            f"{RESET}"
        )

        return


    usuario_actual = {
        "id": datos[0],
        "nombre": datos[1],
        "usuario": datos[2],
        "rol": datos[3]
    }


    if usuario_actual["rol"] == "admin":

        menu_profesor(usuario_actual)

    else:

        menu_estudiante(usuario_actual)


# ==========================================================
# MOSTRAR AGENDA
# ==========================================================

def mostrar_agenda():

    encabezado("📅 AGENDA ESCOLAR")


    cursor.execute("""
    SELECT
        id,
        titulo,
        tipo,
        fecha,
        descripcion,
        estado
    FROM actividades
    ORDER BY id DESC
    """)


    actividades = cursor.fetchall()


    if not actividades:

        print(
            f"{AMARILLO}"
            "No hay actividades registradas."
            f"{RESET}"
        )

        print("\n0. ↩️ Volver")

        input("\nOpción: ")

        return


    for a in actividades:

        if a[5] == "Completada":

            color_estado = VERDE

        else:

            color_estado = AMARILLO


        print(
            f"{AZUL}[ID {a[0]}]{RESET} "
            f"{NEGRITA}{a[1]}{RESET}"
        )

        print(
            f"   Tipo: {a[2]}"
        )

        print(
            f"   Fecha: {a[3]}"
        )

        print(
            f"   Descripción: {a[4]}"
        )

        print(
            f"   Estado: "
            f"{color_estado}{a[5]}{RESET}"
        )

        print(
            f"{GRIS}{'-' * 55}{RESET}"
        )


    print("\n0. ↩️ Volver")

    opcion = input("\nOpción: ").strip()

    if opcion == "0":
        return


# ==========================================================
# AGREGAR ACTIVIDAD
# ==========================================================

def agregar_actividad():

    encabezado("➕ AGREGAR ACTIVIDAD")


    print("Escribe 0 para volver.\n")


    titulo = input(
        "Título: "
    ).strip()

    if titulo == "0":
        return


    tipo = input(
        "Tipo (Tarea/Examen/Evento/Entrega): "
    ).strip()

    if tipo == "0":
        return


    fecha = input(
        "Fecha (DD/MM/AAAA): "
    ).strip()

    if fecha == "0":
        return


    descripcion = input(
        "Descripción: "
    ).strip()

    if descripcion == "0":
        return


    if not titulo or not tipo or not fecha:

        print(
            f"\n{ROJO}"
            "Título, tipo y fecha son obligatorios."
            f"{RESET}"
        )

        return


    cursor.execute("""
    INSERT INTO actividades
    (titulo, tipo, fecha, descripcion, estado)
    VALUES (?, ?, ?, ?, ?)
    """, (
        titulo,
        tipo,
        fecha,
        descripcion,
        "Pendiente"
    ))


    db.commit()


    print(
        f"\n{VERDE}"
        "✓ Actividad agregada correctamente."
        f"{RESET}"
    )


# ==========================================================
# EDITAR ACTIVIDAD
# ==========================================================

def editar_actividad():

    encabezado("✏️ EDITAR ACTIVIDAD")


    cursor.execute("""
    SELECT
        id,
        titulo,
        tipo,
        fecha,
        estado
    FROM actividades
    ORDER BY id
    """)


    actividades = cursor.fetchall()


    if not actividades:

        print(
            f"{AMARILLO}"
            "No hay actividades."
            f"{RESET}"
        )

        print("\n0. ↩️ Volver")

        input("\nOpción: ")

        return


    for a in actividades:

        print(
            f"{AZUL}[{a[0]}]{RESET} "
            f"{a[1]} | "
            f"{a[2]} | "
            f"{a[3]} | "
            f"{a[4]}"
        )


    print("\n0. ↩️ Volver")


    try:

        id_act = int(
            input("\nID a editar: ")
        )

    except ValueError:

        return


    if id_act == 0:
        return


    cursor.execute("""
    SELECT
        titulo,
        tipo,
        fecha,
        descripcion
    FROM actividades
    WHERE id=?
    """, (id_act,))


    actividad = cursor.fetchone()


    if actividad is None:

        print(
            f"\n{ROJO}"
            "No existe esa actividad."
            f"{RESET}"
        )

        return


    print(
        "\nDeja vacío un campo "
        "para conservar el valor actual."
    )

    print(
        "Escribe 0 para cancelar.\n"
    )


    titulo = input(
        f"Título [{actividad[0]}]: "
    ).strip()

    if titulo == "0":
        return


    tipo = input(
        f"Tipo [{actividad[1]}]: "
    ).strip()

    if tipo == "0":
        return


    fecha = input(
        f"Fecha [{actividad[2]}]: "
    ).strip()

    if fecha == "0":
        return


    descripcion = input(
        f"Descripción [{actividad[3]}]: "
    ).strip()

    if descripcion == "0":
        return


    if titulo == "":
        titulo = actividad[0]

    if tipo == "":
        tipo = actividad[1]

    if fecha == "":
        fecha = actividad[2]

    if descripcion == "":
        descripcion = actividad[3]


    cursor.execute("""
    UPDATE actividades
    SET
        titulo=?,
        tipo=?,
        fecha=?,
        descripcion=?
    WHERE id=?
    """, (
        titulo,
        tipo,
        fecha,
        descripcion,
        id_act
    ))


    db.commit()


    print(
        f"\n{VERDE}"
        "✓ Actividad actualizada correctamente."
        f"{RESET}"
    )


# ==========================================================
# ELIMINAR ACTIVIDAD
# ==========================================================

def eliminar_actividad():

    encabezado("🗑️ ELIMINAR ACTIVIDAD")


    cursor.execute("""
    SELECT
        id,
        titulo,
        tipo,
        fecha
    FROM actividades
    ORDER BY id
    """)


    actividades = cursor.fetchall()


    if not actividades:

        print(
            f"{AMARILLO}"
            "No hay actividades."
            f"{RESET}"
        )

        print("\n0. ↩️ Volver")

        input("\nOpción: ")

        return


    for a in actividades:

        print(
            f"{AZUL}[{a[0]}]{RESET} "
            f"{a[1]} | "
            f"{a[2]} | "
            f"{a[3]}"
        )


    print("\n0. ↩️ Volver")


    try:

        id_act = int(
            input("\nID a eliminar: ")
        )

    except ValueError:

        return


    if id_act == 0:
        return


    cursor.execute(
        """
        SELECT titulo
        FROM actividades
        WHERE id=?
        """,
        (id_act,)
    )


    actividad = cursor.fetchone()


    if actividad is None:

        print(
            f"\n{ROJO}"
            "No existe esa actividad."
            f"{RESET}"
        )

        return


    confirmar = input(
        f"\n¿Eliminar '{actividad[0]}'? (s/n): "
    ).lower().strip()


    if confirmar == "s":

        cursor.execute(
            """
            DELETE FROM actividades
            WHERE id=?
            """,
            (id_act,)
        )


        db.commit()


        print(
            f"\n{VERDE}"
            "✓ Actividad eliminada."
            f"{RESET}"
        )


# ==========================================================
# COMPLETAR ACTIVIDAD
# ==========================================================

def completar_actividad():

    encabezado("✅ COMPLETAR ACTIVIDAD")


    cursor.execute("""
    SELECT
        id,
        titulo,
        estado
    FROM actividades
    ORDER BY id
    """)


    actividades = cursor.fetchall()


    if not actividades:

        print(
            f"{AMARILLO}"
            "No hay actividades."
            f"{RESET}"
        )

        print("\n0. ↩️ Volver")

        input("\nOpción: ")

        return


    for a in actividades:

        print(
            f"{AZUL}[{a[0]}]{RESET} "
            f"{a[1]} - {a[2]}"
        )


    print("\n0. ↩️ Volver")


    try:

        id_act = int(
            input("\nID: ")
        )

    except ValueError:

        return


    if id_act == 0:
        return


    cursor.execute("""
    UPDATE actividades
    SET estado='Completada'
    WHERE id=?
    """, (id_act,))


    if cursor.rowcount > 0:

        db.commit()

        print(
            f"\n{VERDE}"
            "✓ Actividad completada."
            f"{RESET}"
        )

    else:

        print(
            f"\n{ROJO}"
            "No existe esa actividad."
            f"{RESET}"
        )


# ==========================================================
# VER DETALLE
# ==========================================================

def ver_detalle():

    encabezado("🔎 DETALLE DE ACTIVIDAD")


    cursor.execute("""
    SELECT
        id,
        titulo,
        tipo,
        fecha
    FROM actividades
    ORDER BY id
    """)


    actividades = cursor.fetchall()


    if not actividades:

        print(
            f"{AMARILLO}"
            "No hay actividades."
            f"{RESET}"
        )

        print("\n0. ↩️ Volver")

        input("\nOpción: ")

        return


    for a in actividades:

        print(
            f"{AZUL}[{a[0]}]{RESET} "
            f"{a[1]} | "
            f"{a[2]} | "
            f"{a[3]}"
        )


    print("\n0. ↩️ Volver")


    try:

        id_act = int(
            input("\nID: ")
        )

    except ValueError:

        return


    if id_act == 0:
        return


    cursor.execute("""
    SELECT
        titulo,
        tipo,
        fecha,
        descripcion,
        estado
    FROM actividades
    WHERE id=?
    """, (id_act,))


    a = cursor.fetchone()


    if a is None:

        return


    encabezado("🔎 DETALLE")


    print(
        f"Título: {a[0]}"
    )

    print(
        f"Tipo: {a[1]}"
    )

    print(
        f"Fecha: {a[2]}"
    )

    print(
        f"Descripción: {a[3]}"
    )

    print(
        f"Estado: {a[4]}"
    )


    print("\n0. ↩️ Volver")

    input("\nOpción: ")


# ==========================================================
# PERFIL
# ==========================================================

def perfil(usuario):

    encabezado("👤 MI PERFIL")


    print(
        f"Nombre: {usuario['nombre']}"
    )

    print(
        f"Usuario: {usuario['usuario']}"
    )


    if usuario["rol"] == "admin":

        print(
            "Rol: 👨‍🏫 Profesor"
        )

    else:

        print(
            "Rol: 👨‍🎓 Estudiante"
        )


    print("\n0. ↩️ Volver")

    input("\nOpción: ")


# ==========================================================
# SUBMENÚ PROFESOR
# ==========================================================

def submenu_agenda_profesor():

    while True:

        encabezado("📅 GESTIÓN DE AGENDA")


        print("1. 📋 Ver agenda")
        print("2. ➕ Agregar actividad")
        print("3. ✏️ Editar actividad")
        print("4. 🗑️ Eliminar actividad")
        print("5. ✅ Completar actividad")
        print("0. ↩️ Volver")


        opcion = input(
            "\nOpción: "
        ).strip()


        if opcion == "1":

            mostrar_agenda()


        elif opcion == "2":

            agregar_actividad()


        elif opcion == "3":

            editar_actividad()


        elif opcion == "4":

            eliminar_actividad()


        elif opcion == "5":

            completar_actividad()


        elif opcion == "0":

            break


        else:

            print(
                f"{ROJO}"
                "Opción inválida."
                f"{RESET}"
            )


# ==========================================================
# SUBMENÚ ESTUDIANTE
# ==========================================================

def submenu_agenda_estudiante():

    while True:

        encabezado("📅 MI AGENDA")


        print("1. 📋 Ver actividades")
        print("2. 🔎 Ver detalle")
        print("0. ↩️ Volver")


        opcion = input(
            "\nOpción: "
        ).strip()


        if opcion == "1":

            mostrar_agenda()


        elif opcion == "2":

            ver_detalle()


        elif opcion == "0":

            break


        else:

            print(
                f"{ROJO}"
                "Opción inválida."
                f"{RESET}"
            )


# ==========================================================
# MENÚ PROFESOR
# ==========================================================

def menu_profesor(usuario):

    while True:

        encabezado("👨‍🏫 PANEL DEL PROFESOR")


        print(
            f"Bienvenido, "
            f"{VERDE}{usuario['nombre']}{RESET}\n"
        )


        print("1. 📅 Gestionar agenda")
        print("2. 👤 Mi perfil")
        print("0. 🚪 Cerrar sesión")


        opcion = input(
            "\nOpción: "
        ).strip()


        if opcion == "1":

            submenu_agenda_profesor()


        elif opcion == "2":

            perfil(usuario)


        elif opcion == "0":

            break


        else:

            print(
                f"{ROJO}"
                "Opción inválida."
                f"{RESET}"
            )


# ==========================================================
# MENÚ ESTUDIANTE
# ==========================================================

def menu_estudiante(usuario):

    while True:

        encabezado("👨‍🎓 PANEL DEL ESTUDIANTE")


        print(
            f"Bienvenido, "
            f"{VERDE}{usuario['nombre']}{RESET}\n"
        )


        print("1. 📅 Consultar agenda")
        print("2. 👤 Mi perfil")
        print("0. 🚪 Cerrar sesión")


        opcion = input(
            "\nOpción: "
        ).strip()


        if opcion == "1":

            submenu_agenda_estudiante()


        elif opcion == "2":

            perfil(usuario)


        elif opcion == "0":

            break


        else:

            print(
                f"{ROJO}"
                "Opción inválida."
                f"{RESET}"
            )


# ==================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib


# ==========================================================
# BASE DE DATOS
# ==========================================================

db = sqlite3.connect("agenda_ade.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS actividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    tipo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT NOT NULL
)
""")

db.commit()


# ==========================================================
# COLORES
# ==========================================================

AZUL_CIELO = "#86B0D6"
VERDE_OSCURO = "#219E60"


VERDE = "#74D689"
ROJO = "#E55D5D"
AMARILLO = "#EAEC93"

TEXTO = "#FBFCFF"
GRIS = "#9DA9C1"

BLANCO = "#FFFFFF"

FONDO = AZUL_CIELO
MENU = VERDE_OSCURO


# ==========================================================
# VENTANA
# ==========================================================

ventana = tk.Tk()

ventana.title("ADE - Agenda Digital Escolar")

ventana.geometry("1100x700")

ventana.minsize(950, 600)

ventana.configure(bg=FONDO)


# ==========================================================
# FUNCIONES GENERALES
# ==========================================================

def limpiar_contenido():

    for widget in contenido.winfo_children():
        widget.destroy()


def encriptar(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def titulo_pagina(titulo, subtitulo=""):

    tk.Label(
        contenido,
        text=titulo,
        font=("Arial", 27, "bold"),
        bg=FONDO,
        fg=TEXTO
    ).pack(
        pady=(30, 5)
    )

    if subtitulo:

        tk.Label(
            contenido,
            text=subtitulo,
            font=("Arial", 13),
            bg=FONDO,
            fg=GRIS
        ).pack(
            pady=(0, 20)
        )


def boton(parent, texto, comando, color=VERDE):

    return tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=color,
        fg=TEXTO,
        activebackground=color,
        activeforeground=TEXTO,
        font=("Arial", 11, "bold"),
        bd=0,
        padx=18,
        pady=10,
        cursor="hand2"
    )


# ==========================================================
# CREAR ADMIN
# ==========================================================

def crear_admin():

    cursor.execute(
        "SELECT id FROM usuarios WHERE usuario='admin'"
    )

    if cursor.fetchone() is None:

        cursor.execute("""
        INSERT INTO usuarios
        (nombre, usuario, password, rol)
        VALUES (?, ?, ?, ?)
        """, (
            "Profesor Administrador",
            "admin",
            encriptar("1234"),
            "admin"
        ))

        db.commit()


# ==========================================================
# INICIO
# ==========================================================

def mostrar_inicio():

    limpiar_contenido()

    titulo_pagina(
        "📚 Agenda Digital Escolar",
        "Organiza tus actividades académicas fácilmente"
    )

    tarjeta = tk.Frame(
        contenido,
        bg=BLANCO,
        bd=0
    )

    tarjeta.pack(
        padx=80,
        pady=25,
        fill="both",
        expand=True
    )

    tk.Label(
        tarjeta,
        text="📅",
        font=("Arial", 55),
        bg=BLANCO
    ).pack(
        pady=(35, 5)
    )

    tk.Label(
        tarjeta,
        text="Bienvenido a ADE",
        font=("Arial", 25, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack()

    tk.Label(
        tarjeta,
        text=(
            "Agenda Digital Escolar para estudiantes "
            "y profesores."
        ),
        font=("Arial", 14),
        bg=BLANCO,
        fg=GRIS
    ).pack(
        pady=10
    )

    cursor.execute(
        "SELECT COUNT(*) FROM actividades"
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM actividades "
        "WHERE estado='Pendiente'"
    )

    pendientes = cursor.fetchone()[0]

    estadisticas = tk.Frame(
        tarjeta,
        bg=BLANCO
    )

    estadisticas.pack(
        pady=35
    )

    crear_estadistica(
        estadisticas,
        "📋",
        total,
        "Actividades"
    ).pack(
        side="left",
        padx=25
    )

    crear_estadistica(
        estadisticas,
        "⏳",
        pendientes,
        "Pendientes"
    ).pack(
        side="left",
        padx=25
    )


def crear_estadistica(parent, icono, numero, texto):

    frame = tk.Frame(
        parent,
        bg=AZUL_CIELO,
        width=160,
        height=110
    )

    frame.pack_propagate(False)

    tk.Label(
        frame,
        text=icono,
        font=("Arial", 22),
        bg=AZUL_CIELO
    ).pack()

    tk.Label(
        frame,
        text=str(numero),
        font=("Arial", 23, "bold"),
        bg=AZUL_CIELO,
        fg=TEXTO
    ).pack()

    tk.Label(
        frame,
        text=texto,
        font=("Arial", 10),
        bg=AZUL_CIELO,
        fg=TEXTO
    ).pack()

    return frame


# ==========================================================
# REGISTRO
# ==========================================================

def registrarse():

    limpiar_contenido()

    titulo_pagina(
        "📝 Crear cuenta",
        "Selecciona el tipo de usuario"
    )

    tarjeta = tk.Frame(
        contenido,
        bg=BLANCO
    )

    tarjeta.pack(
        padx=150,
        pady=20,
        fill="both",
        expand=True
    )

    tk.Label(
        tarjeta,
        text="Tipo de cuenta",
        font=("Arial", 16, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        pady=(30, 15)
    )

    rol = tk.StringVar(value="usuario")

    tk.Radiobutton(
        tarjeta,
        text="👨‍🎓 Estudiante",
        variable=rol,
        value="usuario",
        font=("Arial", 12),
        bg=BLANCO,
        fg=TEXTO,
        activebackground=BLANCO
    ).pack(
        pady=5
    )

    tk.Radiobutton(
        tarjeta,
        text="👨‍🏫 Profesor",
        variable=rol,
        value="admin",
        font=("Arial", 12),
        bg=BLANCO,
        fg=TEXTO,
        activebackground=BLANCO
    ).pack(
        pady=5
    )

    tk.Label(
        tarjeta,
        text="Nombre completo",
        bg=BLANCO,
        fg=TEXTO,
        font=("Arial", 11, "bold")
    ).pack(
        anchor="w",
        padx=50,
        pady=(25, 5)
    )

    entrada_nombre = tk.Entry(
        tarjeta,
        font=("Arial", 12)
    )

    entrada_nombre.pack(
        padx=50,
        fill="x"
    )

    tk.Label(
        tarjeta,
        text="Nombre de usuario",
        bg=BLANCO,
        fg=TEXTO,
        font=("Arial", 11, "bold")
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 5)
    )

    entrada_usuario = tk.Entry(
        tarjeta,
        font=("Arial", 12)
    )

    entrada_usuario.pack(
        padx=50,
        fill="x"
    )

    tk.Label(
        tarjeta,
        text="Contraseña",
        bg=BLANCO,
        fg=TEXTO,
        font=("Arial", 11, "bold")
    ).pack(
        anchor="w",
        padx=50,
        pady=(15, 5)
    )

    entrada_password = tk.Entry(
        tarjeta,
        show="*",
        font=("Arial", 12)
    )

    entrada_password.pack(
        padx=50,
        fill="x"
    )

    def guardar():

        nombre = entrada_nombre.get().strip()
        usuario = entrada_usuario.get().strip()
        password = entrada_password.get().strip()

        if not nombre or not usuario or not password:

            messagebox.showwarning(
                "Datos incompletos",
                "Completa todos los campos."
            )

            return

        if rol.get() == "admin":

            clave = entrada_clave.get().strip()

            if clave != "1234":

                messagebox.showerror(
                    "Error",
                    "Clave de profesor incorrecta."
                )

                return

        try:

            cursor.execute("""
            INSERT INTO usuarios
            (nombre, usuario, password, rol)
            VALUES (?, ?, ?, ?)
            """, (
                nombre,
                usuario,
                encriptar(password),
                rol.get()
            ))

            db.commit()

            messagebox.showinfo(
                "Registro",
                "Cuenta creada correctamente."
            )

            mostrar_inicio()

        except sqlite3.IntegrityError:

            messagebox.showerror(
                "Error",
                "Ese nombre de usuario ya existe."
            )

    def mostrar_clave():

        if rol.get() == "admin":

            clave_label.pack(
                anchor="w",
                padx=50,
                pady=(15, 5)
            )

            entrada_clave.pack(
                padx=50,
                fill="x"
            )

        else:

            clave_label.pack_forget()
            entrada_clave.pack_forget()

    clave_label = tk.Label(
        tarjeta,
        text="Clave de autorización del profesor",
        bg=BLANCO,
        fg=TEXTO,
        font=("Arial", 11, "bold")
    )

    entrada_clave = tk.Entry(
        tarjeta,
        show="*",
        font=("Arial", 12)
    )

    rol.trace_add(
        "write",
        lambda *args: mostrar_clave()
    )

    botones = tk.Frame(
        tarjeta,
        bg=BLANCO
    )

    botones.pack(
        pady=25
    )

    boton(
        botones,
        "📝 Registrarse",
        guardar
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        mostrar_inicio,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


# ==========================================================
# INICIAR SESIÓN
# ==========================================================

def iniciar_sesion():

    limpiar_contenido()

    titulo_pagina(
        "🔐 Iniciar sesión",
        "Accede a tu cuenta de ADE"
    )

    tarjeta = tk.Frame(
        contenido,
        bg=BLANCO
    )

    tarjeta.pack(
        padx=220,
        pady=20,
        fill="both",
        expand=True
    )

    tk.Label(
        tarjeta,
        text="Usuario",
        font=("Arial", 11, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        anchor="w",
        padx=60,
        pady=(60, 5)
    )

    entrada_usuario = tk.Entry(
        tarjeta,
        font=("Arial", 13)
    )

    entrada_usuario.pack(
        padx=60,
        fill="x"
    )

    tk.Label(
        tarjeta,
        text="Contraseña",
        font=("Arial", 11, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        anchor="w",
        padx=60,
        pady=(20, 5)
    )

    entrada_password = tk.Entry(
        tarjeta,
        show="*",
        font=("Arial", 13)
    )

    entrada_password.pack(
        padx=60,
        fill="x"
    )

    def entrar():

        usuario = entrada_usuario.get().strip()
        password = entrada_password.get().strip()

        cursor.execute("""
        SELECT id, nombre, usuario, rol
        FROM usuarios
        WHERE usuario=? AND password=?
        """, (
            usuario,
            encriptar(password)
        ))

        datos = cursor.fetchone()

        if datos is None:

            messagebox.showerror(
                "Error",
                "Usuario o contraseña incorrectos."
            )

            return

        usuario_actual = {
            "id": datos[0],
            "nombre": datos[1],
            "usuario": datos[2],
            "rol": datos[3]
        }

        if usuario_actual["rol"] == "admin":

            menu_profesor(usuario_actual)

        else:

            menu_estudiante(usuario_actual)

    botones = tk.Frame(
        tarjeta,
        bg=BLANCO
    )

    botones.pack(
        pady=35
    )

    boton(
        botones,
        "🔐 Entrar",
        entrar
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        mostrar_inicio,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


# ==========================================================
# AGENDA
# ==========================================================

def mostrar_agenda(volver):

    limpiar_contenido()

    titulo_pagina(
        "📅 Agenda escolar",
        "Actividades registradas"
    )

    marco = tk.Frame(
        contenido,
        bg=BLANCO
    )

    marco.pack(
        padx=30,
        pady=10,
        fill="both",
        expand=True
    )

    columnas = (
        "id",
        "titulo",
        "tipo",
        "fecha",
        "estado"
    )

    tabla = ttk.Treeview(
        marco,
        columns=columnas,
        show="headings"
    )

    tabla.heading("id", text="ID")
    tabla.heading("titulo", text="Título")
    tabla.heading("tipo", text="Tipo")
    tabla.heading("fecha", text="Fecha")
    tabla.heading("estado", text="Estado")

    tabla.column("id", width=50)
    tabla.column("titulo", width=250)
    tabla.column("tipo", width=120)
    tabla.column("fecha", width=120)
    tabla.column("estado", width=130)

    scrollbar = ttk.Scrollbar(
        marco,
        orient="vertical",
        command=tabla.yview
    )

    tabla.configure(
        yscrollcommand=scrollbar.set
    )

    tabla.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    cursor.execute("""
    SELECT id, titulo, tipo, fecha, estado
    FROM actividades
    ORDER BY id DESC
    """)

    actividades = cursor.fetchall()

    for a in actividades:

        tabla.insert(
            "",
            "end",
            values=a
        )

    boton(
        contenido,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        pady=15
    )


# ==========================================================
# AGREGAR ACTIVIDAD
# ==========================================================

def agregar_actividad(volver):

    limpiar_contenido()

    titulo_pagina(
        "➕ Agregar actividad",
        "Registrar una nueva actividad"
    )

    formulario = tk.Frame(
        contenido,
        bg=BLANCO
    )

    formulario.pack(
        padx=120,
        pady=10,
        fill="both",
        expand=True
    )

    def campo(texto):

        tk.Label(
            formulario,
            text=texto,
            bg=BLANCO,
            fg=TEXTO,
            font=("Arial", 11, "bold")
        ).pack(
            anchor="w",
            padx=40,
            pady=(15, 5)
        )

        entrada = tk.Entry(
            formulario,
            font=("Arial", 12)
        )

        entrada.pack(
            padx=40,
            fill="x"
        )

        return entrada

    entrada_titulo = campo("Título")

    entrada_tipo = campo(
        "Tipo (Tarea, Examen, Evento, Entrega)"
    )

    entrada_fecha = campo(
        "Fecha (DD/MM/AAAA)"
    )

    tk.Label(
        formulario,
        text="Descripción",
        bg=BLANCO,
        fg=TEXTO,
        font=("Arial", 11, "bold")
    ).pack(
        anchor="w",
        padx=40,
        pady=(15, 5)
    )

    entrada_descripcion = tk.Text(
        formulario,
        height=5,
        font=("Arial", 11)
    )

    entrada_descripcion.pack(
        padx=40,
        fill="x"
    )

    def guardar():

        titulo = entrada_titulo.get().strip()
        tipo = entrada_tipo.get().strip()
        fecha = entrada_fecha.get().strip()
        descripcion = entrada_descripcion.get(
            "1.0",
            tk.END
        ).strip()

        if not titulo or not tipo or not fecha:

            messagebox.showwarning(
                "Datos incompletos",
                "Título, tipo y fecha son obligatorios."
            )

            return

        cursor.execute("""
        INSERT INTO actividades
        (titulo, tipo, fecha, descripcion, estado)
        VALUES (?, ?, ?, ?, ?)
        """, (
            titulo,
            tipo,
            fecha,
            descripcion,
            "Pendiente"
        ))

        db.commit()

        messagebox.showinfo(
            "Actividad",
            "Actividad agregada correctamente."
        )

        volver()

    botones = tk.Frame(
        formulario,
        bg=BLANCO
    )

    botones.pack(
        pady=20
    )

    boton(
        botones,
        "💾 Guardar",
        guardar
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


# ==========================================================
# EDITAR ACTIVIDAD
# ==========================================================

def editar_actividad(volver):

    limpiar_contenido()

    titulo_pagina(
        "✏️ Editar actividad",
        "Selecciona una actividad"
    )

    marco = tk.Frame(
        contenido,
        bg=BLANCO
    )

    marco.pack(
        padx=30,
        pady=10,
        fill="both",
        expand=True
    )

    columnas = (
        "id",
        "titulo",
        "tipo",
        "fecha",
        "estado"
    )

    tabla = ttk.Treeview(
        marco,
        columns=columnas,
        show="headings"
    )

    for columna in columnas:

        tabla.heading(
            columna,
            text=columna.capitalize()
        )

    tabla.pack(
        fill="both",
        expand=True
    )

    cursor.execute("""
    SELECT id, titulo, tipo, fecha, estado
    FROM actividades
    ORDER BY id DESC
    """)

    for a in cursor.fetchall():

        tabla.insert(
            "",
            "end",
            values=a
        )

    def editar():

        seleccion = tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Seleccionar",
                "Selecciona una actividad."
            )

            return

        datos = tabla.item(
            seleccion[0],
            "values"
        )

        editar_formulario(
            datos[0],
            volver
        )

    botones = tk.Frame(
        contenido,
        bg=FONDO
    )

    botones.pack(
        pady=15
    )

    boton(
        botones,
        "✏️ Editar",
        editar
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


def editar_formulario(id_act, volver):

    cursor.execute("""
    SELECT titulo, tipo, fecha, descripcion
    FROM actividades
    WHERE id=?
    """, (id_act,))

    actividad = cursor.fetchone()

    if actividad is None:
        return

    limpiar_contenido()

    titulo_pagina(
        "✏️ Editar actividad"
    )

    formulario = tk.Frame(
        contenido,
        bg=BLANCO
    )

    formulario.pack(
        padx=120,
        pady=10,
        fill="both",
        expand=True
    )

    def crear_campo(nombre, valor):

        tk.Label(
            formulario,
            text=nombre,
            bg=BLANCO,
            fg=TEXTO,
            font=("Arial", 11, "bold")
        ).pack(
            anchor="w",
            padx=40,
            pady=(15, 5)
        )

        entrada = tk.Entry(
            formulario,
            font=("Arial", 12)
        )

        entrada.insert(
            0,
            valor or ""
        )

        entrada.pack(
            padx=40,
            fill="x"
        )

        return entrada

    entrada_titulo = crear_campo(
        "Título",
        actividad[0]
    )

    entrada_tipo = crear_campo(
        "Tipo",
        actividad[1]
    )

    entrada_fecha = crear_campo(
        "Fecha",
        actividad[2]
    )

    entrada_descripcion = crear_campo(
        "Descripción",
        actividad[3]
    )

    def guardar():

        cursor.execute("""
        UPDATE actividades
        SET titulo=?,
            tipo=?,
            fecha=?,
            descripcion=?
        WHERE id=?
        """, (
            entrada_titulo.get(),
            entrada_tipo.get(),
            entrada_fecha.get(),
            entrada_descripcion.get(),
            id_act
        ))

        db.commit()

        messagebox.showinfo(
            "Editar",
            "Actividad actualizada correctamente."
        )

        volver()

    botones = tk.Frame(
        formulario,
        bg=BLANCO
    )

    botones.pack(
        pady=25
    )

    boton(
        botones,
        "💾 Guardar cambios",
        guardar
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


# ==========================================================
# ELIMINAR
# ==========================================================

def eliminar_actividad(volver):

    limpiar_contenido()

    titulo_pagina(
        "🗑️ Eliminar actividad",
        "Selecciona la actividad que deseas eliminar"
    )

    lista = tk.Listbox(
        contenido,
        font=("Arial", 12),
        bg=BLANCO,
        fg=TEXTO,
        height=15
    )

    lista.pack(
        padx=100,
        pady=10,
        fill="both",
        expand=True
    )

    cursor.execute("""
    SELECT id, titulo, fecha
    FROM actividades
    ORDER BY id DESC
    """)

    actividades = cursor.fetchall()

    for a in actividades:

        lista.insert(
            tk.END,
            f"[{a[0]}] {a[1]} - {a[2]}"
        )

    def eliminar():

        seleccion = lista.curselection()

        if not seleccion:

            messagebox.showwarning(
                "Seleccionar",
                "Selecciona una actividad."
            )

            return

        actividad = actividades[
            seleccion[0]
        ]

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar '{actividad[1]}'?"
        )

        if confirmar:

            cursor.execute(
                "DELETE FROM actividades WHERE id=?",
                (actividad[0],)
            )

            db.commit()

            messagebox.showinfo(
                "Eliminar",
                "Actividad eliminada."
            )

            eliminar_actividad(volver)

    botones = tk.Frame(
        contenido,
        bg=FONDO
    )

    botones.pack(
        pady=15
    )

    boton(
        botones,
        "🗑️ Eliminar",
        eliminar,
        ROJO
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


# ==========================================================
# COMPLETAR
# ==========================================================

def completar_actividad(volver):

    limpiar_contenido()

    titulo_pagina(
        "✅ Completar actividad",
        "Selecciona una actividad"
    )

    lista = tk.Listbox(
        contenido,
        font=("Arial", 12),
        bg=BLANCO,
        fg=TEXTO,
        height=15
    )

    lista.pack(
        padx=100,
        pady=10,
        fill="both",
        expand=True
    )

    cursor.execute("""
    SELECT id, titulo, estado
    FROM actividades
    ORDER BY id DESC
    """)

    actividades = cursor.fetchall()

    for a in actividades:

        lista.insert(
            tk.END,
            f"[{a[0]}] {a[1]} - {a[2]}"
        )

    def completar():

        seleccion = lista.curselection()

        if not seleccion:

            messagebox.showwarning(
                "Seleccionar",
                "Selecciona una actividad."
            )

            return

        id_act = actividades[
            seleccion[0]
        ][0]

        cursor.execute("""
        UPDATE actividades
        SET estado='Completada'
        WHERE id=?
        """, (id_act,))

        db.commit()

        messagebox.showinfo(
            "Actividad",
            "Actividad completada."
        )

        completar_actividad(volver)

    botones = tk.Frame(
        contenido,
        bg=FONDO
    )

    botones.pack(
        pady=15
    )

    boton(
        botones,
        "✅ Completar",
        completar
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


# ==========================================================
# DETALLE
# ==========================================================

def ver_detalle(volver):

    limpiar_contenido()

    titulo_pagina(
        "🔎 Detalle de actividad",
        "Selecciona una actividad"
    )

    lista = tk.Listbox(
        contenido,
        font=("Arial", 12),
        bg=BLANCO,
        fg=TEXTO,
        height=12
    )

    lista.pack(
        padx=100,
        pady=10,
        fill="both",
        expand=True
    )

    cursor.execute("""
    SELECT id, titulo, fecha
    FROM actividades
    ORDER BY id DESC
    """)

    actividades = cursor.fetchall()

    for a in actividades:

        lista.insert(
            tk.END,
            f"[{a[0]}] {a[1]} - {a[2]}"
        )

    def mostrar():

        seleccion = lista.curselection()

        if not seleccion:

            messagebox.showwarning(
                "Seleccionar",
                "Selecciona una actividad."
            )

            return

        id_act = actividades[
            seleccion[0]
        ][0]

        cursor.execute("""
        SELECT titulo, tipo, fecha,
               descripcion, estado
        FROM actividades
        WHERE id=?
        """, (id_act,))

        a = cursor.fetchone()

        messagebox.showinfo(
            "Detalle",
            f"Título: {a[0]}\n\n"
            f"Tipo: {a[1]}\n\n"
            f"Fecha: {a[2]}\n\n"
            f"Descripción: {a[3]}\n\n"
            f"Estado: {a[4]}"
        )

    botones = tk.Frame(
        contenido,
        bg=FONDO
    )

    botones.pack(
        pady=15
    )

    boton(
        botones,
        "🔎 Ver detalle",
        mostrar
    ).pack(
        side="left",
        padx=5
    )

    boton(
        botones,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        side="left",
        padx=5
    )


# ==========================================================
# PERFIL
# ==========================================================

def perfil(usuario, volver):

    limpiar_contenido()

    titulo_pagina(
        "👤 Mi perfil"
    )

    tarjeta = tk.Frame(
        contenido,
        bg=BLANCO
    )

    tarjeta.pack(
        padx=200,
        pady=30,
        fill="both",
        expand=True
    )

    rol = (
        "👨‍🏫 Profesor"
        if usuario["rol"] == "admin"
        else
        "👨‍🎓 Estudiante"
    )

    tk.Label(
        tarjeta,
        text=f"Nombre: {usuario['nombre']}",
        font=("Arial", 14),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        pady=(60, 10)
    )

    tk.Label(
        tarjeta,
        text=f"Usuario: {usuario['usuario']}",
        font=("Arial", 14),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        pady=10
    )

    tk.Label(
        tarjeta,
        text=f"Rol: {rol}",
        font=("Arial", 14, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        pady=10
    )

    boton(
        tarjeta,
        "↩️ Volver",
        volver,
        AZUL_CIELO
    ).pack(
        pady=30
    )


# ==========================================================
# MENÚ PROFESOR
# ==========================================================

def menu_profesor(usuario):

    limpiar_contenido()

    titulo_pagina(
        "👨‍🏫 Panel del profesor",
        f"Bienvenido, {usuario['nombre']}"
    )

    marco = tk.Frame(
        contenido,
        bg=BLANCO
    )

    marco.pack(
        padx=120,
        pady=20,
        fill="both",
        expand=True
    )

    tk.Label(
        marco,
        text="GESTIÓN DE AGENDA",
        font=("Arial", 18, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        pady=(30, 20)
    )

    boton(
        marco,
        "📅 Ver agenda",
        lambda: mostrar_agenda(menu_profesor)
    ).pack(
        pady=6
    )

    boton(
        marco,
        "➕ Agregar actividad",
        lambda: agregar_actividad(menu_profesor)
    ).pack(
        pady=6
    )

    boton(
        marco,
        "✏️ Editar actividad",
        lambda: editar_actividad(menu_profesor)
    ).pack(
        pady=6
    )

    boton(
        marco,
        "🗑️ Eliminar actividad",
        lambda: eliminar_actividad(menu_profesor),
        ROJO
    ).pack(
        pady=6
    )

    boton(
        marco,
        "✅ Completar actividad",
        lambda: completar_actividad(menu_profesor)
    ).pack(
        pady=6
    )

    boton(
        marco,
        "👤 Mi perfil",
        lambda: perfil(usuario, menu_profesor),
        AZUL_CIELO
    ).pack(
        pady=6
    )

    boton(
        marco,
        "🚪 Cerrar sesión",
        mostrar_inicio,
        AZUL_CIELO
    ).pack(
        pady=15
    )


# ==========================================================
# MENÚ ESTUDIANTE
# ==========================================================

def menu_estudiante(usuario):

    limpiar_contenido()

    titulo_pagina(
        "👨‍🎓 Panel del estudiante",
        f"Bienvenido, {usuario['nombre']}"
    )

    marco = tk.Frame(
        contenido,
        bg=BLANCO
    )

    marco.pack(
        padx=150,
        pady=20,
        fill="both",
        expand=True
    )

    tk.Label(
        marco,
        text="MENÚ DEL ESTUDIANTE",
        font=("Arial", 18, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        pady=(40, 20)
    )

    boton(
        marco,
        "📅 Consultar agenda",
        lambda: mostrar_agenda(menu_estudiante)
    ).pack(
        pady=8
    )

    boton(
        marco,
        "🔎 Ver detalle",
        lambda: ver_detalle(menu_estudiante)
    ).pack(
        pady=8
    )

    boton(
        marco,
        "👤 Mi perfil",
        lambda: perfil(usuario, menu_estudiante),
        AZUL_CIELO
    ).pack(
        pady=8
    )

    boton(
        marco,
        "🚪 Cerrar sesión",
        mostrar_inicio,
        AZUL_CIELO
    ).pack(
        pady=20
    )


# ==========================================================
# SOBRE ADE
# ==========================================================

def sobre_ade():

    limpiar_contenido()

    titulo_pagina(
        "ℹ️ Sobre ADE"
    )

    tarjeta = tk.Frame(
        contenido,
        bg=BLANCO
    )

    tarjeta.pack(
        padx=100,
        pady=20,
        fill="both",
        expand=True
    )

    texto = """
AGENDA DIGITAL ESCOLAR

ADE es un sistema diseñado para organizar
las actividades académicas de una institución.

👨‍🏫 PROFESOR

* Agregar actividades
* Editar actividades
* Eliminar actividades
* Completar actividades
* Consultar la agenda

👨‍🎓 ESTUDIANTE

* Consultar actividades
* Ver detalles
* Consultar su perfil

La información se almacena en una
base de datos SQLite.
"""

    tk.Label(
        tarjeta,
        text=texto,
        font=("Arial", 13),
        bg=BLANCO,
        fg=TEXTO,
        justify="left"
    ).pack(
        padx=40,
        pady=35,
        anchor="nw"
    )

    boton(
        tarjeta,
        "↩️ Volver",
        mostrar_inicio,
        AZUL_CIELO
    ).pack(
        pady=20
    )


# ==========================================================
# MENÚ PRINCIPAL
# ==========================================================

def menu_principal():

    limpiar_contenido()

    titulo_pagina(
        "🏠 Menú principal",
        "Agenda Digital Escolar"
    )

    marco = tk.Frame(
        contenido,
        bg=BLANCO
    )

    marco.pack(
        padx=180,
        pady=20,
        fill="both",
        expand=True
    )

    tk.Label(
        marco,
        text="Bienvenido a ADE",
        font=("Arial", 22, "bold"),
        bg=BLANCO,
        fg=TEXTO
    ).pack(
        pady=(45, 25)
    )

    boton(
        marco,
        "🔐 Iniciar sesión",
        iniciar_sesion
    ).pack(
        pady=8
    )

    boton(
        marco,
        "📝 Registrarse",
        registrarse
    ).pack(
        pady=8
    )

    boton(
        marco,
        "ℹ️ Sobre ADE",
        sobre_ade,
        AZUL_CIELO
    ).pack(
        pady=8
    )

    boton(
        marco,
        "🚪 Salir",
        cerrar_programa,
        ROJO
    ).pack(
        pady=20
    )


# ==========================================================
# MENÚ LATERAL
# ==========================================================

menu = tk.Frame(
    ventana,
    bg=MENU,
    width=220
)

menu.pack(
    side="left",
    fill="y"
)

menu.pack_propagate(False)


# ==========================================================
# LOGO A.D.E
# ==========================================================

def crear_logo(parent):

    logo = tk.Frame(
        parent,
        bg=MENU,
        width=220,
        height=145
    )

    logo.pack(
        pady=(20, 5)
    )

    logo.pack_propagate(False)

    # Canvas para colocar las letras una sobre otra
    canvas = tk.Canvas(
        logo,
        width=220,
        height=95,
        bg=MENU,
        highlightthickness=0
    )

    canvas.pack()

    # ======================================================
    # LETRA A
    # ======================================================

    canvas.create_text(
        65,
        42,
        text="A",
        font=("Arial", 65, "bold"),
        fill=TEXTO
    )

    # ======================================================
    # LETRA D
    # ======================================================

    canvas.create_text(
        105,
        42,
        text="D",
        font=("Arial", 65, "bold"),
        fill=TEXTO
    )

    # ======================================================
    # LETRA E
    # ======================================================

    canvas.create_text(
        150,
        42,
        text="E",
        font=("Arial", 65, "bold"),
        fill=TEXTO
    )

    # ======================================================
    # TEXTO DEBAJO DEL LOGO
    # ======================================================

    tk.Label(
        logo,
        text="AGENDA DIGITAL ESCOLAR",
        font=("Arial", 10, "bold"),
        bg=MENU,
        fg=TEXTO
    ).pack(
        pady=(0, 5)
    )

    return logo


# Crear logo
crear_logo(menu)


# ==========================================================
# BOTONES DEL MENÚ LATERAL
# ==========================================================

def boton_menu(texto, comando):

    return tk.Button(
        menu,
        text=texto,
        command=comando,
        bg=MENU,
        fg=TEXTO,
        activebackground=AZUL_CIELO,
        activeforeground=TEXTO,
        font=("Arial", 11, "bold"),
        bd=0,
        anchor="w",
        padx=20,
        pady=14,
        cursor="hand2"
    )


boton_menu(
    "🏠   Inicio",
    mostrar_inicio
).pack(
    fill="x"
)

boton_menu(
    "🔐   Iniciar sesión",
    iniciar_sesion
).pack(
    fill="x"
)

boton_menu(
    "📝   Registrarse",
    registrarse
).pack(
    fill="x"
)

boton_menu(
    "ℹ️   Sobre ADE",
    sobre_ade
).pack(
    fill="x"
)


# ==========================================================
# CONTENIDO
# ==========================================================

contenido = tk.Frame(
    ventana,
    bg=FONDO
)

contenido.pack(
    side="right",
    fill="both",
    expand=True
)


# ==========================================================
# CERRAR
# ==========================================================

def cerrar_programa():

    confirmar = messagebox.askyesno(
        "Salir",
        "¿Quieres cerrar ADE?"
    )

    if confirmar:

        db.close()
        ventana.destroy()


ventana.protocol(
    "WM_DELETE_WINDOW",
    cerrar_programa
)


# ==========================================================
# INICIO DEL PROGRAMA
# ==========================================================

crear_admin()

mostrar_inicio()

ventana.mainloop()