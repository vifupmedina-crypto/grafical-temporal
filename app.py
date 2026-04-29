"""
Gráfica Temporal Biográfica — versión Streamlit
Ejecutar con:  streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.ticker import MultipleLocator
import json
import io


# ════════════════════════════════════════════════════════════
#   CONFIGURACIÓN DE PÁGINA
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Gráfica Temporal Biográfica",
    page_icon="⏱",
    layout="wide",
)

# ════════════════════════════════════════════════════════════
#   DATOS INICIALES
# ════════════════════════════════════════════════════════════
PERSONAS_INIT = [
    dict(nombre="Pedro",   nac=1800, muer=1875, nac_aprox=False, muer_aprox=False, genero="H", notas=""),
    dict(nombre="Jose",    nac=1810, muer=1890, nac_aprox=False, muer_aprox=False, genero="H", notas=""),
    dict(nombre="Miguel",  nac=1818, muer=1900, nac_aprox=False, muer_aprox=False, genero="H", notas=""),
    dict(nombre="Antonio", nac=1825, muer=1910, nac_aprox=False, muer_aprox=False, genero="H", notas=""),
    dict(nombre="Luis",    nac=1835, muer=1920, nac_aprox=False, muer_aprox=False, genero="H", notas=""),
    dict(nombre="Maria",   nac=1805, muer=1878, nac_aprox=False, muer_aprox=False, genero="M", notas=""),
    dict(nombre="Ana",     nac=1812, muer=1895, nac_aprox=False, muer_aprox=False, genero="M", notas=""),
    dict(nombre="Isabel",  nac=1820, muer=1905, nac_aprox=False, muer_aprox=False, genero="M", notas=""),
    dict(nombre="Laura",   nac=1830, muer=1915, nac_aprox=False, muer_aprox=False, genero="M", notas=""),
    dict(nombre="Bea",     nac=1840, muer=1928, nac_aprox=False, muer_aprox=False, genero="M", notas=""),
]

SUCESOS_INIT = [
    dict(nombre="Evento 1", año=1852, personajes=["Pedro", "Jose", "Miguel"], notas=""),
    dict(nombre="Evento 2", año=1861, personajes=["Ana", "Laura"], notas=""),
    dict(nombre="Evento 3", año=1868, personajes=["Antonio", "Maria"], notas=""),
]

FAMILIAS_INIT = [
    dict(nombre="Pérez",  miembros=["Pedro", "Jose", "Maria"], notas=""),
    dict(nombre="García", miembros=["Miguel", "Antonio", "Luis"], notas=""),
    dict(nombre="López",  miembros=["Luis", "Ana", "Isabel"], notas=""),
]

# ════════════════════════════════════════════════════════════
#   COLORES
# ════════════════════════════════════════════════════════════
COLOR_H   = "#2E86AB"   # azul acero  — hombres
COLOR_M   = "#9B59B6"   # púrpura     — mujeres
COLOR_EVT = "#E74C3C"   # rojo        — sucesos
ROW_H     = 1.0
ARROW_SC  = 9

# Paleta para familias (distinta de H, M y EVT)
PALETA_FAMILIAS = [
    "#27AE60",  # verde esmeralda
    "#F39C12",  # ámbar
    "#E91E63",  # magenta
    "#1ABC9C",  # turquesa
    "#FF5722",  # naranja profundo
    "#795548",  # marrón
    "#607D8B",  # gris azulado
    "#CDDC39",  # lima
]

def color_familia(nombre_familia, lista_familias):
    """Devuelve siempre el mismo color para una familia dada."""
    nombres = [f["nombre"] for f in lista_familias]
    idx = nombres.index(nombre_familia) if nombre_familia in nombres else 0
    return PALETA_FAMILIAS[idx % len(PALETA_FAMILIAS)]

# ════════════════════════════════════════════════════════════
#   SESSION STATE  (memoria entre interacciones)
# ════════════════════════════════════════════════════════════
if "personas" not in st.session_state:
    st.session_state.personas = [p.copy() for p in PERSONAS_INIT]
if "sucesos" not in st.session_state:
    st.session_state.sucesos  = [s.copy() for s in SUCESOS_INIT]
if "familias" not in st.session_state:
    st.session_state.familias = [f.copy() for f in FAMILIAS_INIT]
if "titulo" not in st.session_state:
    st.session_state.titulo = "Mi Gráfica Temporal"
if "yr_from" not in st.session_state:
    st.session_state.yr_from = 1790
if "yr_to" not in st.session_state:
    st.session_state.yr_to = 1940

personas = st.session_state.personas
sucesos  = st.session_state.sucesos
familias = st.session_state.familias

# ════════════════════════════════════════════════════════════
#   BARRA LATERAL (controles)
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⏱ Gráfica Temporal")
    # =====================================================
    # NUEVO: MENÚ PLEGABLES (EXPANDERS)
    # Sustituye SOLO la estructura visual.
    # Todo tu código interno se mantiene igual.
    # =====================================================

    # ── Título y años en formulario ───────────────────────
    with st.expander("⚙️ Configuración general", expanded=True):
        with st.form("form_config"):
            st.markdown("### 📌 Título")
            nuevo_titulo = st.text_input("Título de la gráfica",value=st.session_state.titulo)
            st.markdown("### 📅 Rango de años")
            col1, col2 = st.columns(2)
            nuevo_yr_from = col1.number_input("Desde", value=st.session_state.yr_from, min_value=0, max_value=2100, step=10)
            nuevo_yr_to   = col2.number_input("Hasta", value=st.session_state.yr_to, min_value=0, max_value=2100, step=10)
            st.markdown("### 🔀 Orden de personajes")
            opciones_orden = ["Orden de entrada", "Fecha de nacimiento", "Fecha de muerte", "GÃ©nero (â™‚ primero)", "GÃ©nero (â™€ primero)", "Familia"]
            nuevo_orden = st.selectbox("Ordenar por", opciones_orden, index=opciones_orden.index(st.session_state.get("orden", "Orden de entrada")))
            submitted = st.form_submit_button("🔄 Actualizar gráfica",type="primary", use_container_width=True)
            if submitted:
                st.session_state.titulo  = nuevo_titulo
                st.session_state.yr_from = int(nuevo_yr_from)
                st.session_state.yr_to   = int(nuevo_yr_to)
                st.session_state.orden   = nuevo_orden
                st.rerun()

        titulo  = st.session_state.titulo
        yr_from = st.session_state.yr_from
        yr_to   = st.session_state.yr_to

    # ── Filtros rápidos ───────────────────────────────────
    with st.expander("🔍 Filtros rápidos", expanded=False):
        st.markdown("### 🔍 Filtros rápidos")

    # Fila 1: Todos / Ninguno / Solo H / Solo M
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("✓ Todos",   use_container_width=True):
            st.session_state["filtro_rapido"] = "todos"
        if c2.button("✗ Ninguno", use_container_width=True):
            st.session_state["filtro_rapido"] = "ninguno"
        if c3.button("♂ H",       use_container_width=True):
            st.session_state["filtro_rapido"] = "hombres"
        if c4.button("♀ M",       use_container_width=True):
            st.session_state["filtro_rapido"] = "mujeres"

     # Filtro por familia
        nombres_familias = [f["nombre"] for f in familias]
        fam_sel = st.multiselect(
        "🏠 Mostrar familias",
            options=nombres_familias,
            placeholder="Selecciona una o varias familias...",
            key="filtro_familias"
        )
        mostrar_sin_familia = st.checkbox(
            "Incluir personas sin familia",
            value=True,
            key="filtro_sin_familia"
        )
        if st.button("Aplicar filtro familiar", use_container_width=True):
            st.session_state["filtro_rapido"] = "familia"

        # Aplicar filtro rápido a los checkboxes
        filtro = st.session_state.pop("filtro_rapido", None)

        def persona_familias(nombre):
            return [f["nombre"] for f in familias if nombre in f["miembros"]]

        for p in personas:
            key = f"p_{p['nombre']}"
            if key not in st.session_state:
                st.session_state[key] = True
            if filtro == "todos":
                st.session_state[key] = True
            elif filtro == "ninguno":
                st.session_state[key] = False
            elif filtro == "hombres":
                st.session_state[key] = p["genero"] == "H"
            elif filtro == "mujeres":
                st.session_state[key] = p["genero"] == "M"
            elif filtro == "familia":
                p_fams = persona_familias(p["nombre"])
                tiene_familia = len(p_fams) > 0
                en_fam_sel = any(f in fam_sel for f in p_fams)

                if fam_sel:
                    st.session_state[key] = en_fam_sel or (
                        not tiene_familia and mostrar_sin_familia
                    )
                else:
                    st.session_state[key] = (
                        not tiene_familia and mostrar_sin_familia
                    )

    # ── Personajes: checkboxes + botones editar/borrar ────
    with st.expander("👤 Personajes", expanded=False):
        st.markdown("### 👤 Personajes")
        sel_p    = {}
        borrar_p = None
        editar_p = None
        for p in personas:
            sym  = "♂" if p["genero"] == "H" else "♀"
            key  = f"p_{p['nombre']}"
            if key not in st.session_state:
                st.session_state[key] = True
            fams    = persona_familias(p["nombre"])
            fam_tag = f" ({', '.join(fams)})" if fams else ""
            c1, c2, c3 = st.columns([5, 1, 1])
            sel_p[p["nombre"]] = c1.checkbox(
                f"{sym} {p['nombre']}{fam_tag}",
                value=st.session_state[key],
                key=key
            )
            if c2.button("✏️", key=f"edit_p_{p['nombre']}", help=f"Editar {p['nombre']}"):
                st.session_state["editing_persona"] = p["nombre"]
            if c3.button("🗑", key=f"del_p_{p['nombre']}", help=f"Borrar {p['nombre']}"):
                borrar_p = p["nombre"]

        if borrar_p:
            st.session_state.personas = [p for p in personas if p["nombre"] != borrar_p]
            for f in st.session_state.familias:
                f["miembros"] = [m for m in f["miembros"] if m != borrar_p]
            if f"p_{borrar_p}" in st.session_state:
                del st.session_state[f"p_{borrar_p}"]
            st.rerun()

        # Formulario de edición de personaje
        ep_nombre = st.session_state.get("editing_persona")
        if ep_nombre:
            ep = next((p for p in personas if p["nombre"] == ep_nombre), None)
            if ep:
                st.markdown(f"##### ✏️ Editando: **{ep_nombre}**")
                with st.form("form_edit_persona"):
                    ep_nom_new  = st.text_input("Nombre",          value=ep["nombre"])
                    c1, c2      = st.columns(2)
                    ep_nac_new  = c1.number_input("Año nacimiento", value=ep["nac"]  or 1600, step=1)
                    ep_muer_new = c2.number_input("Año muerte",     value=ep["muer"] or 1700, step=1)
                    ep_gen_new  = st.radio("Género",
                                        ["♂ Hombre", "♀ Mujer"],
                                        index=0 if ep["genero"] == "H" else 1,
                                        horizontal=True)
                    c3, c4      = st.columns(2)
                    ep_nac_ap   = c3.checkbox("Nac. aprox. (?)",  value=ep.get("nac_aprox",  False))
                    ep_muer_ap  = c4.checkbox("Muer. aprox. (?)", value=ep.get("muer_aprox", False))
                    # Familias actuales
                    fams_actuales = [f["nombre"] for f in st.session_state.familias
                                    if ep_nombre in f["miembros"]]
                    ep_fams_new = st.multiselect(
                        "Familias",
                        options=[f["nombre"] for f in st.session_state.familias],
                        default=fams_actuales
                    )
                    ep_notas_new = st.text_area("📝 Notas", value=ep.get("notas", ""),
                                                height=100, placeholder="Observaciones, fuentes, datos biográficos...")
                    c_ok, c_cancel = st.columns(2)
                    submitted = c_ok.form_submit_button("💾 Guardar", type="primary",
                                                        use_container_width=True)
                    cancelled = c_cancel.form_submit_button("✗ Cancelar",
                                                            use_container_width=True)

                if submitted:
                    # Actualizar datos del personaje
                    for p in st.session_state.personas:
                        if p["nombre"] == ep_nombre:
                            p["nombre"]     = ep_nom_new.strip()
                            p["nac"]        = int(ep_nac_new)
                            p["muer"]       = int(ep_muer_new)
                            p["genero"]     = "H" if "Hombre" in ep_gen_new else "M"
                            p["nac_aprox"]  = ep_nac_ap
                            p["muer_aprox"] = ep_muer_ap
                            p["notas"]      = ep_notas_new.strip()
                            break
                    # Actualizar familias: quitar de todas y añadir a las seleccionadas
                    for f in st.session_state.familias:
                        if ep_nombre in f["miembros"]:
                            f["miembros"].remove(ep_nombre)
                        if ep_nom_new.strip() in f["miembros"]:
                            f["miembros"].remove(ep_nom_new.strip())
                        if f["nombre"] in ep_fams_new:
                            f["miembros"].append(ep_nom_new.strip())
                    # Limpiar checkbox viejo si cambió el nombre
                    if ep_nom_new.strip() != ep_nombre:
                        if f"p_{ep_nombre}" in st.session_state:
                            del st.session_state[f"p_{ep_nombre}"]
                    del st.session_state["editing_persona"]
                    st.rerun()

                if cancelled:
                    del st.session_state["editing_persona"]
                    st.rerun()

    # ── Familias: lista + botones editar/borrar ────────────
    with st.expander("🏠 Familias", expanded=False):
        st.markdown("### 🏠 Familias")
        borrar_f = None
        for f in familias:
            miembros_str = ", ".join(f["miembros"]) if f["miembros"] else "sin miembros"
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.markdown(f"**{f['nombre']}**: {miembros_str}")
            if c2.button("✏️", key=f"edit_f_{f['nombre']}", help=f"Editar familia {f['nombre']}"):
                st.session_state["editing_familia"] = f["nombre"]
            if c3.button("🗑", key=f"del_f_{f['nombre']}", help=f"Borrar familia {f['nombre']}"):
                borrar_f = f["nombre"]

        if borrar_f:
            st.session_state.familias = [f for f in familias if f["nombre"] != borrar_f]
            st.rerun()

        # Formulario de edición de familia
        ef_nombre = st.session_state.get("editing_familia")
        if ef_nombre:
            ef = next((f for f in familias if f["nombre"] == ef_nombre), None)
            if ef:
                st.markdown(f"##### ✏️ Editando familia: **{ef_nombre}**")
                with st.form("form_edit_familia"):
                    ef_nom_new  = st.text_input("Nombre de la familia", value=ef["nombre"])
                    ef_miem_new = st.multiselect(
                        "Miembros",
                        options=[p["nombre"] for p in personas],
                        default=ef["miembros"]
                    )
                    ef_notas_new = st.text_area(
                        "📝 Descripción / Notas",
                        value=ef.get("notas", ""),
                        height=120
                    )
                    c_ok, c_cancel = st.columns(2)
                    submitted_f = c_ok.form_submit_button("💾 Guardar", type="primary",
                                                            use_container_width=True)
                    cancelled_f = c_cancel.form_submit_button("✗ Cancelar",
                                                            use_container_width=True)

                if submitted_f:
                    for f in st.session_state.familias:
                        if f["nombre"] == ef_nombre:
                            f["nombre"]   = ef_nom_new.strip()
                            f["miembros"] = list(ef_miem_new)
                            f["notas"] = ef_notas_new.strip()
                            break
                    del st.session_state["editing_familia"]
                    st.rerun()

                if cancelled_f:
                    del st.session_state["editing_familia"]
                    st.rerun()

    # ── Sucesos: checkbox mostrar + editar + borrar ────────
    with st.expander("⚡ Sucesos", expanded=False):
        st.markdown("### ⚡ Sucesos")
        sel_s    = {}
        borrar_s = None
        editar_s = None
        for s in sucesos:
            key = f"s_{s['nombre']}"
            if key not in st.session_state:
                st.session_state[key] = True
            c1, c2, c3 = st.columns([5, 1, 1])
            sel_s[s["nombre"]] = c1.checkbox(
                f"🔴 {s['nombre']} ({s['año']})",
                value=st.session_state[key],
                key=key
            )
            if c2.button("✏️", key=f"edit_s_{s['nombre']}", help=f"Editar {s['nombre']}"):
                st.session_state["editing_suceso"] = s["nombre"]
            if c3.button("🗑", key=f"del_s_{s['nombre']}", help=f"Borrar {s['nombre']}"):
                borrar_s = s["nombre"]

        if borrar_s:
            st.session_state.sucesos = [s for s in sucesos if s["nombre"] != borrar_s]
            if f"s_{borrar_s}" in st.session_state:
                del st.session_state[f"s_{borrar_s}"]
            st.rerun()

        # Formulario de edición de suceso
        es_nombre = st.session_state.get("editing_suceso")
        if es_nombre:
            es = next((s for s in sucesos if s["nombre"] == es_nombre), None)
            if es:
                st.markdown(f"##### ✏️ Editando suceso: **{es_nombre}**")
                with st.form("form_edit_suceso"):
                    es_nom_new  = st.text_input("Nombre del suceso", value=es["nombre"])
                    es_año_new  = st.number_input("Año", value=es["año"], step=1)
                    es_pers_new = st.multiselect(
                        "Personajes afectados",
                        options=[p["nombre"] for p in personas],
                        default=es["personajes"]
                    )
                    es_notas_new = st.text_area(
                        "📝 Descripción / Notas",
                        value=es.get("notas", ""),
                        height=120
                    )
                    c_ok, c_cancel = st.columns(2)
                    submitted_s = c_ok.form_submit_button("💾 Guardar", type="primary",
                                                        use_container_width=True)
                    cancelled_s = c_cancel.form_submit_button("✗ Cancelar",
                                                            use_container_width=True)
                if submitted_s:
                    for s in st.session_state.sucesos:
                        if s["nombre"] == es_nombre:
                            old_key = f"s_{es_nombre}"
                            s["nombre"]    = es_nom_new.strip()
                            s["año"]       = int(es_año_new)
                            s["personajes"] = list(es_pers_new)
                            s["notas"] = es_notas_new.strip()
                            break
                    # Actualizar key si cambió el nombre
                    if es_nom_new.strip() != es_nombre:
                        if f"s_{es_nombre}" in st.session_state:
                            st.session_state[f"s_{es_nom_new.strip()}"] = \
                                st.session_state.pop(f"s_{es_nombre}")
                    del st.session_state["editing_suceso"]
                    st.rerun()
                if cancelled_s:
                    del st.session_state["editing_suceso"]
                    st.rerun()

    st.markdown("---")
   
    # AÑADIR DATOS
    
    with st.expander("➕ Añadir datos", expanded=False):
    # ── Añadir personaje ──────────────────────────────────
    
        with st.expander("➕ Añadir personaje"):
            np_nombre = st.text_input("Nombre", key="np_nombre")
            c1, c2 = st.columns(2)
            np_nac  = c1.number_input("Año nacimiento", value=1600, step=1, key="np_nac")
            np_muer = c2.number_input("Año muerte",     value=1680, step=1, key="np_muer")
            np_gen  = st.radio("Género", ["♂ Hombre", "♀ Mujer"], horizontal=True, key="np_gen")
            c3, c4  = st.columns(2)
            np_nac_ap  = c3.checkbox("Nac. aprox. (?)", key="np_nac_ap")
            np_muer_ap = c4.checkbox("Muer. aprox. (?)", key="np_muer_ap")
            np_familias = st.multiselect(
                "Familias (opcional)",
                options=[f["nombre"] for f in st.session_state.familias],
                key="np_familias"
            )
            np_notas = st.text_area("📝 Notas (opcional)", key="np_notas", height=80,
                                    placeholder="Observaciones, fuentes, datos biográficos...")
            if st.button("Añadir personaje", type="primary"):
                if np_nombre.strip():
                    personas.append(dict(
                        nombre=np_nombre.strip(),
                        nac=int(np_nac), muer=int(np_muer),
                        nac_aprox=np_nac_ap, muer_aprox=np_muer_ap,
                        genero="H" if "Hombre" in np_gen else "M",
                        notas=np_notas.strip()
                    ))
                    # Añadir a las familias seleccionadas
                    for f in st.session_state.familias:
                        if f["nombre"] in np_familias:
                            f["miembros"].append(np_nombre.strip())
                    st.success(f"✅ '{np_nombre}' añadido")
                    st.rerun()
                else:
                    st.error("El nombre es obligatorio")

        # ── Añadir suceso ─────────────────────────────────────
        with st.expander("➕ Añadir suceso"):
            ns_nombre = st.text_input("Nombre del suceso", key="ns_nombre")
            ns_año    = st.number_input("Año", value=1650, step=1, key="ns_año")
            ns_pers   = st.multiselect(
                "Personajes afectados",
                options=[p["nombre"] for p in personas],
                key="ns_pers"
            )
            ns_notas = st.text_area(
                "📝 Descripción / Notas",
                key="ns_notas",
                height=100
            )
            if st.button("Añadir suceso", type="primary"):
                if ns_nombre.strip():
                    sucesos.append(dict(
                        nombre=ns_nombre.strip(),
                        año=int(ns_año),
                        personajes=ns_pers,
                        notas=ns_notas.strip()
                    ))
                    st.success(f"✅ Suceso '{ns_nombre}' añadido")
                    st.rerun()
                else:
                    st.error("El nombre es obligatorio")

        # ── Añadir familia ────────────────────────────────────
        with st.expander("➕ Añadir familia"):
            nf_nombre = st.text_input("Nombre de la familia", key="nf_nombre")
            nf_miembros = st.multiselect(
                "Miembros",
                options=[p["nombre"] for p in personas],
                key="nf_miembros"
            )
            nf_notas = st.text_area(
                "📝 Descripción / Notas",
                key="nf_notas",
                height=100
            )
            if st.button("Añadir familia", type="primary"):
                if nf_nombre.strip():
                    # Comprobar si ya existe
                    nombres_fam = [f["nombre"] for f in st.session_state.familias]
                    if nf_nombre.strip() in nombres_fam:
                        st.error("Ya existe una familia con ese nombre")
                    else:
                        st.session_state.familias.append(dict(
                            nombre=nf_nombre.strip(),
                            miembros=list(nf_miembros),
                            notas=nf_notas.strip()
                        ))
                        st.success(f"✅ Familia '{nf_nombre}' añadida")
                        st.rerun()
                else:
                    st.error("El nombre es obligatorio")


    # ── Exportar ──────────────────────────────────────────
    with st.expander("💾 Exportar / Importar", expanded=False):
        st.markdown("### 💾 Exportar / Importar")

        datos_export = json.dumps({
            "titulo":   st.session_state.titulo,
            "yr_from":  st.session_state.yr_from,
            "yr_to":    st.session_state.yr_to,
            "personas": st.session_state.personas,
            "sucesos":  st.session_state.sucesos,
            "familias": st.session_state.familias,
        }, ensure_ascii=False, indent=2)

        st.download_button(
            label="📥 Exportar mis datos (.json)",
            data=datos_export,
            file_name="grafica_temporal.json",
            mime="application/json",
            use_container_width=True,
        )

        # ── Importar ──────────────────────────────────────────
        archivo = st.file_uploader(
            "📤 Importar datos (.json)",
            type="json",
            help="Sube un archivo exportado anteriormente"
        )
        if archivo is not None:
            file_id = archivo.name + str(archivo.size)
            if st.session_state.get("last_imported") != file_id:
                try:
                    datos = json.load(archivo)
                    st.session_state.personas = datos["personas"]
                    st.session_state.sucesos  = datos["sucesos"]
                    st.session_state.familias = datos.get("familias", [])
                    st.session_state.titulo   = datos.get("titulo",  "Gráfica Temporal")
                    st.session_state.yr_from  = datos.get("yr_from", 1500)
                    st.session_state.yr_to    = datos.get("yr_to",   1800)
                    for k in list(st.session_state.keys()):
                        if k.startswith("p_") or k.startswith("s_"):
                            del st.session_state[k]
                    st.session_state.last_imported = file_id
                    st.success("✅ Datos importados correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al leer el archivo: {e}")

    # ── Resetear datos ────────────────────────────────────

    with st.expander("🔄 Restablecer", expanded=False):
        if st.button("🔄 Restablecer datos originales"):
            st.session_state.personas = [p.copy() for p in PERSONAS_INIT]
            st.session_state.sucesos  = [s.copy() for s in SUCESOS_INIT]
            st.session_state.familias = [f.copy() for f in FAMILIAS_INIT]
            st.session_state.titulo   = "Mi Gráfica Temporal"
            st.session_state.yr_from  = 1790
            st.session_state.yr_to    = 1940
            for k in list(st.session_state.keys()):
                if k.startswith("p_") or k.startswith("s_"):
                    del st.session_state[k]
            st.rerun()

# ════════════════════════════════════════════════════════════
#   DIBUJO DE LA GRÁFICA
# ════════════════════════════════════════════════════════════
span = max(yr_to - yr_from, 1)

# Filtrar personajes visibles
visibles = []
for p in personas:
    if not sel_p.get(p["nombre"], True):
        continue
    nac_e  = p["nac"]  if p["nac"]  is not None else (yr_from - 50)
    muer_e = p["muer"] if p["muer"] is not None else (yr_to   + 50)
    if muer_e < yr_from or nac_e > yr_to:
        continue
    visibles.append(p)

# Ordenar según preferencia
orden = st.session_state.get("orden", "Orden de entrada")
if orden == "Fecha de nacimiento":
    visibles.sort(key=lambda p: p["nac"]  or 0)
elif orden == "Fecha de muerte":
    visibles.sort(key=lambda p: p["muer"] or 0)
elif orden == "Género (♂ primero)":
    visibles.sort(key=lambda p: (0 if p["genero"] == "H" else 1, p["nac"] or 0))
elif orden == "Género (♀ primero)":
    visibles.sort(key=lambda p: (0 if p["genero"] == "M" else 1, p["nac"] or 0))
elif orden == "Familia":
    def sort_familia(p):
        fams = [f["nombre"] for f in familias if p["nombre"] in f["miembros"]]
        return (fams[0] if fams else "zzz", p["nac"] or 0)
    visibles.sort(key=sort_familia)

n_rows = len(visibles)

# ── Constantes de dibujo ──────────────────────────────────
GAP_FAM = 0.5
ROW_H2  = 1.5

y_positions = []  # y central de cada fila
grupo_cambio = [] # True si hay salto de grupo antes de esta fila

if orden == "Familia" and n_rows > 0:
    grupos = []
    for p in visibles:
        fams = [f["nombre"] for f in familias if p["nombre"] in f["miembros"]]
        grupos.append(fams[0] if fams else "__sin_familia__")
    y = 0.4
    prev = None
    for i in range(n_rows - 1, -1, -1):
        if prev is not None and grupos[i] != prev:
            y += GAP_FAM
            grupo_cambio.insert(0, True)
        else:
            grupo_cambio.insert(0, False)
        y_positions.insert(0, y + ROW_H2 * 0.4)
        y += ROW_H2
        prev = grupos[i]
    total_h = y + 0.4
else:
    for i in range(n_rows):
        y_positions.append(0.4 + (n_rows - 1 - i) * ROW_H2 + ROW_H2 * 0.4)
        grupo_cambio.append(False)
    total_h = max(n_rows, 1) * ROW_H2 + 0.8

fig_h = max(5.0, n_rows * 0.7 + 2.5)
fig, ax = plt.subplots(figsize=(14, fig_h))
fig.patch.set_facecolor("white")
# Margen izquierdo amplio para etiquetas de nombre
fig.subplots_adjust(left=0.20, right=0.97, top=0.93, bottom=0.18)

if n_rows == 0:
    ax.text(0.5, 0.5, "Sin personajes en el rango seleccionado",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=13, color="#999")
else:
    ax.set_xlim(yr_from, yr_to)
    ax.set_ylim(0, total_h)
    ax.set_facecolor("#f8f9fb")

    tick_major = 10 if span <= 150 else (25 if span <= 300 else 50)
    tick_minor = tick_major // 2
    ax.xaxis.set_major_locator(MultipleLocator(tick_major))
    ax.xaxis.set_minor_locator(MultipleLocator(tick_minor))
    ax.tick_params(axis="x", which="major", length=6, labelsize=9,
                   top=True, bottom=True, labeltop=True, labelbottom=True,
                   direction="out", color="#555")
    ax.tick_params(axis="x", which="minor", length=3,
                   top=True, bottom=True, direction="out", color="#aaa")
    ax.yaxis.set_visible(False)

    for spine in ["top", "bottom", "left", "right"]:
        ax.spines[spine].set_edgecolor("#5b9bd5")
        ax.spines[spine].set_linewidth(1.8)

    # Cuadrícula vertical
    for yr in range(yr_from, yr_to + 1, tick_major):
        ax.axvline(yr, color="#e2e5ea", linewidth=0.6, zorder=0)

    # Bandas alternas base
    for i, y_c in enumerate(y_positions):
        yb = y_c - ROW_H2 * 0.45
        yt = y_c + ROW_H2 * 0.55
        if i % 2 == 0:
            ax.axhspan(yb, yt, color="#f0f3f8", zorder=0)

    # Bandas de familia (A)
    for i, p in enumerate(visibles):
        p_fams = [f["nombre"] for f in familias if p["nombre"] in f["miembros"]]
        if not p_fams:
            continue
        y_c = y_positions[i]
        yb  = y_c - ROW_H2 * 0.45
        yt  = y_c + ROW_H2 * 0.55
        h_f = (yt - yb) / len(p_fams)
        for j, fam in enumerate(p_fams):
            col_f = color_familia(fam, familias)
            ax.axhspan(yb + j * h_f, yb + (j + 1) * h_f,
                       color=col_f, alpha=0.13, zorder=1)

    # Línea separadora entre grupos de familia
    if orden == "Familia":
        for i, cambio in enumerate(grupo_cambio):
            if cambio and i > 0:
                y_sep = (y_positions[i] + ROW_H2 * 0.6 + y_positions[i-1] - ROW_H2 * 0.45) / 2
                ax.axhline(y_sep, color="#aaa", linewidth=0.8,
                           linestyle="--", zorder=1, alpha=0.5)

    def draw_arrow(x0, x1, y, color, lw=2.2):
        ax.plot([x0, x1], [y, y], color=color, linewidth=lw,
                linestyle=(0, (7, 4)), zorder=2, solid_capstyle="butt")
        ax.annotate("", xy=(x1, y), xytext=(max(x0, x1 - span * 0.003), y),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                   mutation_scale=ARROW_SC), zorder=3)
        ax.annotate("", xy=(x0, y), xytext=(min(x1, x0 + span * 0.003), y),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                   mutation_scale=ARROW_SC), zorder=3)

    for i, p in enumerate(visibles):
        y_c   = y_positions[i]
        color = COLOR_H if p["genero"] == "H" else COLOR_M
        sym   = "♂" if p["genero"] == "H" else "♀"

        nac_r   = p["nac"]
        muer_r  = p["muer"]
        nac_ap  = p.get("nac_aprox",  False) or (nac_r  is None)
        muer_ap = p.get("muer_aprox", False) or (muer_r is None)

        x0 = max(nac_r  if nac_r  is not None else yr_from - 50, yr_from)
        x1 = min(muer_r if muer_r is not None else yr_to   + 50, yr_to)

        draw_arrow(x0, x1, y_c, color)

        # Marcadores de fecha aproximada
        if nac_ap and nac_r is not None and yr_from <= nac_r <= yr_to:
            ax.plot(nac_r, y_c, "o", color=color, markersize=5, zorder=4)
            ax.text(nac_r - span*0.004, y_c + 0.1, "?", color=color,
                    fontsize=8, ha="right", va="bottom", zorder=4)
        if muer_ap and muer_r is not None and yr_from <= muer_r <= yr_to:
            ax.plot(muer_r, y_c, "o", color=color, markersize=5, zorder=4)
            ax.text(muer_r + span*0.004, y_c + 0.1, "?", color=color,
                    fontsize=8, ha="left", va="bottom", zorder=4)

        nac_str  = (str(nac_r)+"?")  if (nac_ap  and nac_r)  else (str(nac_r)  if nac_r  else "?")
        muer_str = (str(muer_r)+"?") if (muer_ap and muer_r) else (str(muer_r) if muer_r else "?")

        # ── Nombre + símbolo a la IZQUIERDA (fuera del eje) ──
        ax.text(yr_from - span * 0.012, y_c + 0.12,
                f"{sym} {p['nombre']}",
                color=color, fontsize=11, fontweight="bold",
                ha="right", va="center", zorder=5, clip_on=False)
        # Años debajo del nombre
        ax.text(yr_from - span * 0.012, y_c - 0.22,
                f"{nac_str} – {muer_str}",
                color="#333", fontsize=8.5,
                ha="right", va="center", zorder=5, clip_on=False)

        # 📝 Icono si tiene notas
        if p.get("notas", "").strip():
            ax.text(yr_from - span * 0.002, y_c + 0.28, "📝",
                    fontsize=8, ha="left", va="center", zorder=5, clip_on=False)

        # ── D) Puntos de familia sobre la línea ──────────────
        p_fams = [f["nombre"] for f in familias if p["nombre"] in f["miembros"]]
        for k_f, fam in enumerate(p_fams):
            col_f  = color_familia(fam, familias)
            x_dot  = x0 + (x1 - x0) * (0.15 + k_f * 0.12)
            ax.plot(x_dot, y_c, "o", color=col_f, markersize=9,
                    markeredgecolor="white", markeredgewidth=1.2,
                    zorder=5)

    # ── Sucesos ───────────────────────────────────────────
    for s in sucesos:
        n = s["nombre"]
        if not sel_s.get(n, True):
            continue
        año = s["año"]
        if not (yr_from <= año <= yr_to):
            continue
        aff = [i for i, p in enumerate(visibles) if p["nombre"] in s["personajes"]]
        if aff:
            y_bot = y_positions[max(aff)] - ROW_H2 * 0.35
            y_top = y_positions[min(aff)] + ROW_H2 * 0.5
        else:
            y_bot, y_top = 0.1, total_h - 0.1

        ax.plot([año, año], [y_bot, y_top], color=COLOR_EVT, linewidth=2.5, zorder=4)
        for i, p in enumerate(visibles):
            if p["nombre"] in s["personajes"]:
                y_c = y_positions[i]
                ax.plot(año, y_c, "o", color=COLOR_EVT, markersize=8, zorder=6,
                        markeredgecolor="white", markeredgewidth=1.2)
        # Nombre del evento en horizontal encima de la línea
        ax.text(año, y_top + 0.12, n,
                color=COLOR_EVT, fontsize=8, rotation=0,
                ha="center", va="bottom", fontweight="bold", zorder=7,
                bbox=dict(boxstyle="round,pad=0.18", fc="#fff8f7",
                          ec=COLOR_EVT, alpha=0.85, linewidth=0.8))

    # ── Título grande ─────────────────────────────────────
    ax.set_title(titulo, pad=14, fontsize=18, fontweight="bold", color="#1e2030")
    ax.set_xlabel("")

    # ── Leyenda horizontal debajo del gráfico ────────────
    legend_handles = [
        mlines.Line2D([0, 1], [0, 0], color="#888", linewidth=2,
                      linestyle=(0, (6, 3)), label="Línea de vida"),
        mpatches.Patch(color=COLOR_H,  linewidth=0, label="♂  Hombre"),
        mpatches.Patch(color=COLOR_M,  linewidth=0, label="♀  Mujer"),
        mlines.Line2D([0], [0], color=COLOR_EVT, linewidth=2,
                      marker="o", markersize=7,
                      markeredgecolor=COLOR_EVT, markeredgewidth=0,
                      label="Suceso"),
    ]
    for f in familias:
        col_f = color_familia(f["nombre"], familias)
        legend_handles.append(
            mpatches.Patch(color=col_f, linewidth=0, alpha=0.8, label=f"{f['nombre']}")
        )

    ax.legend(handles=legend_handles,
              loc="upper center",
              bbox_to_anchor=(0.5, -0.10),
              ncol=len(legend_handles),
              fontsize=9,
              frameon=True,
              framealpha=0.9,
              edgecolor="#ccc")



st.pyplot(fig, use_container_width=True)

# ── Exportar gráfica como imagen ─────────────────────────
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
st.download_button(
    label="📷 Descargar gráfica como PNG",
    data=buf,
    file_name=f"{titulo}.png",
    mime="image/png",
)
plt.close(fig)

# ════════════════════════════════════════════════════════════
# PANEL DE INFORMACIÓN GENERAL
# ════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### 🔎 Panel de información")

modo = st.radio(
    "Mostrar ficha de:",
    ["Persona", "Familia", "Suceso"],
    horizontal=True
)

# PERSONA
if modo == "Persona":
    nombres_visibles = [p["nombre"] for p in visibles]

    if nombres_visibles:
        idx = st.selectbox(
            "Selecciona persona:",
            range(len(visibles)),
            format_func=lambda i: visibles[i]["nombre"]
        )

        p = visibles[idx]

        p_fams = [f["nombre"] for f in familias if p["nombre"] in f["miembros"]]
        p_sucs = [s["nombre"] for s in sucesos if p["nombre"] in s["personajes"]]

        st.markdown(f"## {'♂' if p['genero']=='H' else '♀'} {p['nombre']}")
        st.write(f"**Nacimiento:** {p['nac']}")
        st.write(f"**Muerte:** {p['muer']}")
        st.write(f"**Familias:** {', '.join(p_fams) if p_fams else 'Ninguna'}")
        st.write(f"**Sucesos:** {', '.join(p_sucs) if p_sucs else 'Ninguno'}")

        notas = p.get("notas", "").strip()
        if notas:
            st.markdown("### 📝 Biografía")
            st.info(notas)

# FAMILIA
elif modo == "Familia":

    if familias:
        idx = st.selectbox(
            "Selecciona familia:",
            range(len(familias)),
            format_func=lambda i: familias[i]["nombre"]
        )

        f = familias[idx]

        st.markdown(f"## 🏠 {f['nombre']}")
        st.write(f"**Miembros:** {', '.join(f['miembros']) if f['miembros'] else 'Sin miembros'}")

        notas = f.get("notas", "").strip()
        if notas:
            st.markdown("### 📝 Descripción")
            st.info(notas)

# SUCESO
else:

    if sucesos:
        idx = st.selectbox(
            "Selecciona suceso:",
            range(len(sucesos)),
            format_func=lambda i: sucesos[i]["nombre"]
        )

        s = sucesos[idx]

        st.markdown(f"## ⚡ {s['nombre']}")
        st.write(f"**Año:** {s['año']}")
        st.write(f"**Afectados:** {', '.join(s['personajes']) if s['personajes'] else 'Nadie'}")

        notas = s.get("notas", "").strip()
        if notas:
            st.markdown("### 📝 Descripción")
            st.info(notas)

# Pie
st.markdown(
    "<div style='text-align:center; color:#aaa; font-size:12px; margin-top:8px'>"
    "Gráfica Temporal Biográfica · Edita los datos en el panel izquierdo"
    "</div>",
    unsafe_allow_html=True
)
