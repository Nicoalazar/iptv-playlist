#!/usr/bin/env python3
"""Generate PDF manual for M3U Playlist Unifier."""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from fpdf import FPDF

ARIAL = "C:/Windows/Fonts/arial.ttf"
ARIAL_B = "C:/Windows/Fonts/arialbd.ttf"
ARIAL_I = "C:/Windows/Fonts/ariali.ttf"
ARIAL_BI = "C:/Windows/Fonts/arialbi.ttf"
COUR = "C:/Windows/Fonts/cour.ttf"
COUR_B = "C:/Windows/Fonts/courbd.ttf"


class ManualPDF(FPDF):
    """Custom PDF with header/footer."""

    def __init__(self):
        super().__init__()
        self.add_font("Arial", "", ARIAL)
        self.add_font("Arial", "B", ARIAL_B)
        self.add_font("Arial", "I", ARIAL_I)
        self.add_font("Arial", "BI", ARIAL_BI)
        self.add_font("Cour", "", COUR)
        self.add_font("Cour", "B", COUR_B)

    def header(self):
        self.set_font("Arial", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "M3U Playlist Unifier - Manual de Usuario", align="R")
        self.ln(4)
        self.set_draw_color(0, 120, 200)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 90, 170)
        self.cell(0, 12, title)
        self.ln(10)

    def sub_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, title)
        self.ln(8)

    def body_text(self, text):
        self.set_font("Arial", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def code_block(self, text):
        self.set_font("Cour", "", 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(30, 30, 30)
        x = self.get_x()
        y = self.get_y()
        lines = text.split('\n')
        block_h = len(lines) * 5.5 + 6
        if y + block_h > 270:
            self.add_page()
            y = self.get_y()
        self.rect(x, y, 190, block_h, 'F')
        self.set_xy(x + 3, y + 3)
        for line in lines:
            self.cell(0, 5.5, line)
            self.ln(5.5)
            self.set_x(x + 3)
        self.ln(5)

    def bullet(self, text, indent=15):
        x = self.get_x()
        self.set_font("Arial", "", 10)
        self.set_text_color(30, 30, 30)
        self.set_x(indent)
        self.cell(5, 6, "\u2022")
        self.multi_cell(170, 6, text)
        self.ln(1)

    def numbered_item(self, number, text, indent=15):
        self.set_font("Arial", "B", 10)
        self.set_text_color(0, 90, 170)
        self.set_x(indent)
        self.cell(8, 6, f"{number}.")
        self.set_font("Arial", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(165, 6, text)
        self.ln(1)

    def table_row(self, cols, widths, bold=False, fill=False):
        style = "B" if bold else ""
        self.set_font("Arial", style, 9)
        if fill:
            self.set_fill_color(0, 90, 170)
            self.set_text_color(255, 255, 255)
        else:
            self.set_text_color(30, 30, 30)
            self.set_fill_color(245, 245, 245)
        h = 7
        x_start = self.get_x()
        for i, (col, w) in enumerate(zip(cols, widths)):
            self.cell(w, h, col, border=1, fill=fill or (not bold and i % 2 == 0))
        self.ln(h)
        self.set_text_color(30, 30, 30)

    def warning_box(self, text):
        self.set_fill_color(255, 248, 220)
        self.set_draw_color(255, 180, 0)
        self.set_line_width(0.3)
        y = self.get_y()
        self.rect(10, y, 190, 14, 'DF')
        self.set_xy(14, y + 2)
        self.set_font("Arial", "B", 9)
        self.set_text_color(180, 100, 0)
        self.cell(5, 5, "!")
        self.set_font("Arial", "", 9)
        self.multi_cell(175, 5, text)
        self.ln(6)

    def tip_box(self, text):
        self.set_fill_color(220, 245, 220)
        self.set_draw_color(60, 180, 60)
        self.set_line_width(0.3)
        y = self.get_y()
        # Calculate height
        lines = len(text) // 80 + 2
        h = max(14, lines * 6 + 4)
        self.rect(10, y, 190, h, 'DF')
        self.set_xy(14, y + 2)
        self.set_font("Arial", "B", 9)
        self.set_text_color(30, 120, 30)
        self.cell(10, 5, "TIP:")
        self.set_font("Arial", "", 9)
        self.multi_cell(165, 5, text)
        self.ln(6)


def create_manual():
    pdf = ManualPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # =====================================================
    # COVER PAGE
    # =====================================================
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Arial", "B", 32)
    pdf.set_text_color(0, 90, 170)
    pdf.cell(0, 15, "M3U Playlist Unifier", align="C")
    pdf.ln(18)
    pdf.set_font("Arial", "", 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Manual de Usuario", align="C")
    pdf.ln(12)
    pdf.set_draw_color(0, 120, 200)
    pdf.set_line_width(1)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(20)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "Herramienta para unificar multiples listas IPTV", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, "en un solo archivo .m3u organizado por categorias", align="C")
    pdf.ln(30)
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "Version 1.0 - Marzo 2026", align="C")

    # =====================================================
    # TABLE OF CONTENTS
    # =====================================================
    pdf.add_page()
    pdf.section_title("Indice")
    pdf.ln(5)

    toc = [
        ("1. Que es M3U Playlist Unifier?", 3),
        ("2. Requisitos previos", 3),
        ("3. Archivos del proyecto", 4),
        ("4. Modo interactivo (primera vez)", 4),
        ("5. Modo automatico (con configuracion)", 6),
        ("6. Opciones de linea de comandos", 6),
        ("7. Agregar o quitar URLs de listas", 7),
        ("8. Personalizar categorias", 7),
        ("9. Testeo de canales", 8),
        ("10. Solucionar problemas", 8),
        ("11. Referencia rapida", 9),
    ]

    for title, page in toc:
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(30, 30, 30)
        w = pdf.get_string_width(title)
        pdf.cell(w + 2, 8, title)
        dots = "." * (60 - len(title))
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, f" {dots} {page}")
        pdf.ln(8)

    # =====================================================
    # 1. WHAT IS IT
    # =====================================================
    pdf.add_page()
    pdf.section_title("1. Que es M3U Playlist Unifier?")

    pdf.body_text(
        "M3U Playlist Unifier es un script en Python que automatiza el proceso de "
        "unificar multiples listas de reproduccion IPTV (archivos .m3u) en un solo "
        "archivo organizado por categorias."
    )

    pdf.sub_title("Que hace?")
    pdf.bullet("Descarga automaticamente listas M3U desde multiples URLs")
    pdf.bullet("Parsea y extrae todos los canales con sus metadatos (nombre, logo, grupo)")
    pdf.bullet("Normaliza categorias similares (ej: 'DEPORTES', 'Sports', 'Deportes' se unifican)")
    pdf.bullet("Elimina canales duplicados por URL")
    pdf.bullet("Permite seleccionar que categorias conservar")
    pdf.bullet("Genera un archivo .m3u limpio y organizado")
    pdf.bullet("Testea una muestra de canales para verificar funcionamiento")
    pdf.bullet("Guarda la configuracion para futuras ejecuciones rapidas")

    pdf.ln(5)
    pdf.sub_title("Para quien es?")
    pdf.body_text(
        "Para usuarios de aplicaciones IPTV (como VLC, IPTV Smarters, TiviMate, Kodi) "
        "que manejan multiples listas .m3u y quieren consolidarlas en una sola lista "
        "organizada y sin duplicados."
    )

    # =====================================================
    # 2. REQUIREMENTS
    # =====================================================
    pdf.section_title("2. Requisitos previos")

    pdf.sub_title("Software necesario")
    pdf.numbered_item(1, "Python 3.8 o superior instalado")
    pdf.numbered_item(2, "Libreria 'requests' de Python")
    pdf.ln(3)

    pdf.sub_title("Instalar dependencias")
    pdf.body_text("Abre una terminal/consola y ejecuta:")
    pdf.code_block("python -m pip install requests")

    pdf.body_text("Para verificar que Python esta instalado:")
    pdf.code_block("python --version")

    pdf.warning_box("En algunos sistemas puede ser 'python3' en lugar de 'python'.")

    # =====================================================
    # 3. PROJECT FILES
    # =====================================================
    pdf.add_page()
    pdf.section_title("3. Archivos del proyecto")

    widths = [55, 135]
    pdf.table_row(["Archivo", "Descripcion"], widths, bold=True, fill=True)
    pdf.table_row(["m3u_unifier.py", "Script principal (el que ejecutas)"], widths)
    pdf.table_row(["lista_unificada.m3u", "Lista M3U generada (resultado)"], widths)
    pdf.table_row(["m3u_config.json", "Configuracion guardada para reusar"], widths)
    pdf.table_row(["m3u_data.json", "Datos crudos (cache de canales)"], widths)
    pdf.table_row(["m3u_normalized.json", "Datos normalizados por categoria"], widths)

    pdf.ln(5)
    pdf.tip_box("Solo necesitas m3u_unifier.py para empezar. Los demas se generan automaticamente.")

    # =====================================================
    # 4. INTERACTIVE MODE
    # =====================================================
    pdf.ln(5)
    pdf.section_title("4. Modo interactivo (primera vez)")

    pdf.body_text("La primera vez, ejecuta el script sin argumentos:")
    pdf.code_block("python m3u_unifier.py")

    pdf.ln(3)
    pdf.sub_title("Paso 1: Descarga automatica")
    pdf.body_text(
        "El script descarga todas las listas M3U de las URLs configuradas. "
        "Veras el progreso en la consola:"
    )
    pdf.code_block(
        "Descargando 17 listas M3U...\n"
        "--------------------------------------------\n"
        "  OK  http://tecnotv.club/.../lista.m3u (856 canales)\n"
        "  OK  http://tecnotv.club/.../lista1.m3u (116 canales)\n"
        "  FAIL http://bit.ly/... : Failed to download\n"
        "...\n"
        "Total: 12742 canales de 16 fuentes"
    )

    pdf.add_page()
    pdf.sub_title("Paso 2: Ver categorias disponibles")
    pdf.body_text(
        "El script muestra todas las categorias encontradas, divididas en "
        "CONTENIDO y PAISES, con la cantidad de canales en cada una:"
    )
    pdf.code_block(
        "CATEGORIAS DE CONTENIDO\n"
        "============================================\n"
        "  [ 1] Entretenimiento          2815 canales\n"
        "  [ 2] TV Premium               1684 canales\n"
        "  [ 3] Cine y Peliculas         1311 canales\n"
        "  [ 4] Canales 24/7              485 canales\n"
        "  [ 5] Musica                    357 canales\n"
        "  ...\n"
        "\n"
        "CATEGORIAS POR PAIS\n"
        "============================================\n"
        "  [ 1] Chile                     458 canales\n"
        "  [ 2] Argentina                 303 canales\n"
        "  ..."
    )

    pdf.sub_title("Paso 3: Seleccionar categorias")
    pdf.body_text("Para CONTENIDO, escribe los numeros separados por coma:")
    pdf.code_block(
        "Categorias de contenido:\n"
        "  Ingresa los numeros separados por coma (ej: 1,2,3,5)\n"
        "  'all' para todas, 'all-X,Y' para todas excepto X e Y\n"
        "  > 1,2,3,4,5,6,7,8"
    )

    pdf.body_text("Para PAISES, mismo formato. Usa 'none' si no quieres ninguno:")
    pdf.code_block(
        "Categorias por pais:\n"
        "  > 2         (solo Argentina)\n"
        "  > all       (todos los paises)\n"
        "  > none      (ningun pais)\n"
        "  > all-5,6   (todos menos el 5 y 6)"
    )

    pdf.sub_title("Paso 4: Resultado")
    pdf.body_text(
        "Se genera el archivo lista_unificada.m3u y se guarda la configuracion "
        "en m3u_config.json para reusar."
    )

    # =====================================================
    # 5. AUTOMATIC MODE
    # =====================================================
    pdf.add_page()
    pdf.section_title("5. Modo automatico (con configuracion)")

    pdf.body_text(
        "Una vez que ejecutaste el modo interactivo, se guarda tu seleccion. "
        "Para regenerar la lista con la misma configuracion:"
    )
    pdf.code_block("python m3u_unifier.py --config m3u_config.json")

    pdf.body_text(
        "Esto es util para actualizar la lista periodicamente sin tener que "
        "volver a seleccionar categorias."
    )

    pdf.tip_box(
        "Puedes crear un archivo .bat (Windows) o .sh (Linux/Mac) para ejecutar "
        "esto con un doble clic. Ejemplo: crear 'actualizar.bat' con el contenido: "
        "python m3u_unifier.py --config m3u_config.json --test"
    )

    # =====================================================
    # 6. CLI OPTIONS
    # =====================================================
    pdf.ln(3)
    pdf.section_title("6. Opciones de linea de comandos")

    widths2 = [50, 140]
    pdf.table_row(["Opcion", "Descripcion"], widths2, bold=True, fill=True)
    pdf.table_row(["--urls archivo.txt", "Cargar URLs desde un archivo (una por linea)"], widths2)
    pdf.table_row(["--config config.json", "Usar configuracion guardada (sin interaccion)"], widths2)
    pdf.table_row(["--output nombre.m3u", "Nombre del archivo de salida (default: lista_unificada.m3u)"], widths2)
    pdf.table_row(["--test", "Testear canales despues de generar"], widths2)
    pdf.table_row(["--test-count N", "Cantidad de canales a testear (default: 30)"], widths2)

    pdf.ln(5)
    pdf.sub_title("Ejemplos de uso")

    pdf.body_text("Generar con URLs personalizadas:")
    pdf.code_block("python m3u_unifier.py --urls mis_urls.txt")

    pdf.body_text("Generar y testear 50 canales:")
    pdf.code_block("python m3u_unifier.py --config m3u_config.json --test --test-count 50")

    pdf.body_text("Guardar con otro nombre:")
    pdf.code_block("python m3u_unifier.py --config m3u_config.json --output mi_lista.m3u")

    # =====================================================
    # 7. ADDING/REMOVING URLS
    # =====================================================
    pdf.add_page()
    pdf.section_title("7. Agregar o quitar URLs de listas")

    pdf.sub_title("Opcion A: Editar el script")
    pdf.body_text(
        "Abre m3u_unifier.py en un editor de texto y busca la seccion "
        "DEFAULT_URLS. Agrega o quita URLs de la lista:"
    )
    pdf.code_block(
        'DEFAULT_URLS = [\n'
        '    "http://ejemplo.com/lista1.m3u",\n'
        '    "http://ejemplo.com/lista2.m3u",\n'
        '    # Agrega aqui tus nuevas URLs\n'
        '    "http://nueva-fuente.com/canales.m3u",\n'
        ']'
    )

    pdf.sub_title("Opcion B: Usar un archivo externo")
    pdf.body_text("Crea un archivo de texto (ej: urls.txt) con una URL por linea:")
    pdf.code_block(
        "http://ejemplo.com/lista1.m3u\n"
        "http://ejemplo.com/lista2.m3u\n"
        "# Lineas con # son ignoradas\n"
        "http://otra-fuente.com/canales.m3u"
    )
    pdf.body_text("Luego ejecuta:")
    pdf.code_block("python m3u_unifier.py --urls urls.txt")

    # =====================================================
    # 8. CUSTOMIZE CATEGORIES
    # =====================================================
    pdf.section_title("8. Personalizar categorias")

    pdf.body_text(
        "El script tiene un mapa de normalizacion (CATEGORY_MAP) que agrupa "
        "categorias similares. Por ejemplo, 'DEPORTES', 'Sports' y 'Deportes' "
        "se unifican como 'Deportes'."
    )

    pdf.body_text("Para agregar nuevas reglas, edita CATEGORY_MAP en m3u_unifier.py:")
    pdf.code_block(
        'CATEGORY_MAP = {\n'
        '    ...\n'
        '    # Agregar nuevas reglas:\n'
        '    "Mi Categoria": "Entretenimiento",\n'
        '    "New Group": "Noticias",\n'
        '    ...\n'
        '}'
    )

    pdf.warning_box(
        "Si una categoria no esta en el mapa, se conserva con su nombre original."
    )

    # =====================================================
    # 9. TESTING
    # =====================================================
    pdf.add_page()
    pdf.section_title("9. Testeo de canales")

    pdf.body_text(
        "El script puede testear una muestra aleatoria de canales para verificar "
        "que las URLs funcionan. El test verifica que el servidor responda con "
        "codigo 200 y envie datos."
    )

    pdf.code_block(
        "Testeando 30 canales aleatorios...\n"
        "--------------------------------------------\n"
        "  [  OK] [Entretenimiento] Univer TV (1080p)\n"
        "  [  OK] [TV Premium     ] Telesur\n"
        "  [FAIL] [Argentina      ] PANC TV\n"
        "  ...\n"
        "Resultado: 22/30 funcionando (73%)"
    )

    pdf.body_text("Es normal que algunos canales fallen por:")
    pdf.bullet("Canales geo-bloqueados (solo funcionan en ciertos paises)")
    pdf.bullet("Servidores temporalmente caidos")
    pdf.bullet("URLs expiradas o con tokens vencidos")
    pdf.bullet("Canales que solo transmiten en ciertos horarios")

    pdf.tip_box(
        "Un 70-80% de canales funcionando es un resultado tipico para listas IPTV publicas."
    )

    # =====================================================
    # 10. TROUBLESHOOTING
    # =====================================================
    pdf.section_title("10. Solucionar problemas")

    pdf.sub_title("'python' no se reconoce como comando")
    pdf.body_text("Asegurate de que Python esta en el PATH del sistema. En Windows, reinstala Python marcando 'Add to PATH'.")

    pdf.sub_title("Error de codificacion (UnicodeError)")
    pdf.body_text("El script ya maneja esto automaticamente en Windows. Si persiste, ejecuta:")
    pdf.code_block("set PYTHONIOENCODING=utf-8\npython m3u_unifier.py")

    pdf.sub_title("Muchos canales fallan al testear")
    pdf.body_text("Las listas IPTV publicas cambian frecuentemente. Actualiza tus URLs fuente o busca listas nuevas.")

    pdf.sub_title("El archivo .m3u no abre en mi reproductor")
    pdf.body_text(
        "Verifica que tu reproductor soporte M3U extendido (#EXTM3U). "
        "Reproductores recomendados: VLC, IPTV Smarters, TiviMate, Kodi."
    )

    # =====================================================
    # 11. QUICK REFERENCE
    # =====================================================
    pdf.add_page()
    pdf.section_title("11. Referencia rapida")

    pdf.sub_title("Comandos esenciales")

    widths3 = [95, 95]
    pdf.table_row(["Tarea", "Comando"], widths3, bold=True, fill=True)
    pdf.table_row(["Primera ejecucion", "python m3u_unifier.py"], widths3)
    pdf.table_row(["Regenerar lista", "python m3u_unifier.py --config m3u_config.json"], widths3)
    pdf.table_row(["Con test de canales", "...--config m3u_config.json --test"], widths3)
    pdf.table_row(["URLs personalizadas", "...--urls mis_urls.txt"], widths3)
    pdf.table_row(["Otro nombre de salida", "...--output mi_lista.m3u"], widths3)

    pdf.ln(5)
    pdf.sub_title("Formato de seleccion de categorias")

    widths4 = [50, 140]
    pdf.table_row(["Entrada", "Resultado"], widths4, bold=True, fill=True)
    pdf.table_row(["1,2,3,5", "Selecciona categorias 1, 2, 3 y 5"], widths4)
    pdf.table_row(["all", "Selecciona todas las categorias"], widths4)
    pdf.table_row(["none", "No selecciona ninguna (solo para paises)"], widths4)
    pdf.table_row(["all-3,7", "Todas excepto la 3 y la 7"], widths4)

    pdf.ln(5)
    pdf.sub_title("Automatizar con archivo .bat (Windows)")
    pdf.code_block(
        '@echo off\n'
        'echo Actualizando lista M3U...\n'
        'python m3u_unifier.py --config m3u_config.json --test\n'
        'echo.\n'
        'echo Lista actualizada!\n'
        'pause'
    )
    pdf.body_text("Guarda esto como 'actualizar.bat' y ejecutalo con doble clic.")

    pdf.ln(5)
    pdf.sub_title("Automatizar con cron (Linux/Mac)")
    pdf.body_text("Para actualizar automaticamente cada dia a las 6 AM:")
    pdf.code_block("crontab -e\n# Agregar esta linea:\n0 6 * * * cd /ruta/al/proyecto && python3 m3u_unifier.py --config m3u_config.json")

    # Save
    output_path = "manual_m3u_unifier.pdf"
    pdf.output(output_path)
    print(f"Manual generado: {output_path}")
    return output_path


if __name__ == "__main__":
    create_manual()
