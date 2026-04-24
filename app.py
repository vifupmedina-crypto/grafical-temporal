"""
Gráfica Temporal Biográfica — versión Streamlit
Ejecutar con:  streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator
import json

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
    dict(nombre="Pedro",   nac=1800, muer=1875, nac_aprox=False, muer_aprox=False, genero="H"),
    dict(nombre="Jose",    nac=1810, muer=1890, nac_aprox=False, muer_aprox=False, genero="H"),
    dict(nombre="Miguel",  nac=1818, muer=1900, nac_aprox=False, muer_aprox=False, genero="H"),
    dict(nombre="Antonio", nac=1825, muer=1910, nac_aprox=False, muer_aprox=False, genero="H"),
    dict(nombre="Luis",    nac=1835, muer=1920, nac_aprox=False, muer_aprox=False, genero="H"),
    dict(nombre="Maria",   nac=1805, muer=1878, nac_aprox=False, muer_aprox=False, genero="M"),
    dict(nombre="Ana",     nac=1812, muer=1895, nac_aprox=False, muer_aprox=False, genero="M"),
    dict(nombre="Isabel",  nac=1820, muer=1905, nac_aprox=False, muer_aprox=False, genero="M"),
    dict(nombre="Laura",   nac=1830, muer=1915, nac_aprox=False, muer_aprox=False, genero="M"),
    dict(nombre="Bea",     nac=1840, muer=1928, nac_aprox=False, muer_aprox=False, genero="M"),
]

SUCESOS_INIT = [
    dict(nombre="Evento 1", año=1852, personajes=["Pedro", "Jose", "Miguel"]),
    dict(nombre="Evento 2", año=1861, personajes=["Ana", "Laura"]),
    dict(nombre="Evento 3", año=1868, personajes=["Antonio", "Maria"]),
]

# ════════════════════════════════════════════════════════════
#   COLORES
# ════════════════════════════════════════════════════════════
COLOR_H   = "#d4763b"
COLOR_M   = "#4a90d9"
COLOR_EVT = "#c0392b"
ROW_H     = 1.0
ARROW_SC  = 9

# ════════════════════════════════════════════════════════════
#   SESSION STATE  (memoria entre interacciones)
# ════════════════════════════════════════════════════════════
if "personas" not in st.session_state:
    st.session_state.personas = [p.copy() for p in PERSONAS_INIT]
if "sucesos" not in st.session_state:
    st.session_state.sucesos  = [s.copy() for s in SUCESOS_INIT]
if "titulo" not in st.session_state:
    st.session_state.titulo = "Mi Gráfica Temporal"
if "yr_from" not in st.session_state:
    st.session_state.yr_from = 1790
if "yr_to" not in st.session_state:
    st.session_state.yr_to = 1940

personas = st.session_state.personas
sucesos  = st.session_state.sucesos

# ════════════════════════════════════════════════════════════
#   BARRA LATERAL (controles)
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⏱ Gráfica Temporal")
    st.markdown("---")

    # ── Título y años en formulario ───────────────────────
    with st.form("form_config"):
        st.markdown("### 📌 Título")
        nuevo_titulo = st.text_input("Título de la gráfica",
                                     value=st.session_state.titulo)
        st.markdown("### 📅 Rango de años")
        col1, col2 = st.columns(2)
        nuevo_yr_from = col1.number_input("Desde", value=st.session_state.yr_from,
                                          min_value=0, max_value=2100, step=10)
        nuevo_yr_to   = col2.number_input("Hasta", value=st.session_state.yr_to,
                                          min_value=0, max_value=2100, step=10)
        submitted = st.form_submit_button("🔄 Actualizar gráfica",
                                          type="primary", use_container_width=True)
        if submitted:
            st.session_state.titulo  = nuevo_titulo
            st.session_state.yr_from = int(nuevo_yr_from)
            st.session_state.yr_to   = int(nuevo_yr_to)
            st.rerun()

    titulo  = st.session_state.titulo
    yr_from = st.session_state.yr_from
    yr_to   = st.session_state.yr_to

    # ── Personajes: checkboxes + botón borrar ─────────────
    st.markdown("### 👤 Personajes")
    col_a, col_b = st.columns(2)
    if col_a.button("✓ Todos"):
        st.session_state["sel_todos"] = True
    if col_b.button("✗ Ninguno"):
        st.session_state["sel_todos"] = False

    sel_p = {}
    borrar_p = None
    for p in personas:
        sym = "♂" if p["genero"] == "H" else "♀"
        key = f"p_{p['nombre']}"
        if key not in st.session_state:
            st.session_state[key] = True
        if "sel_todos" in st.session_state:
            st.session_state[key] = st.session_state["sel_todos"]

        c1, c2 = st.columns([5, 1])
        sel_p[p["nombre"]] = c1.checkbox(
            f"{sym} {p['nombre']}",
            value=st.session_state[key],
            key=key
        )
        if c2.button("🗑", key=f"del_p_{p['nombre']}", help=f"Borrar {p['nombre']}"):
            borrar_p = p["nombre"]

    if "sel_todos" in st.session_state:
        del st.session_state["sel_todos"]

    if borrar_p:
        st.session_state.personas = [p for p in personas if p["nombre"] != borrar_p]
        # Limpiar su checkbox del estado
        if f"p_{borrar_p}" in st.session_state:
            del st.session_state[f"p_{borrar_p}"]
        st.rerun()

    # ── Sucesos: checkboxes + botón borrar ────────────────
    st.markdown("### ⚡ Sucesos")
    sel_s = {}
    borrar_s = None
    for s in sucesos:
        key = f"s_{s['nombre']}"
        if key not in st.session_state:
            st.session_state[key] = True

        c1, c2 = st.columns([5, 1])
        sel_s[s["nombre"]] = c1.checkbox(
            f"🔴 {s['nombre']} ({s['año']})",
            value=st.session_state[key],
            key=key
        )
        if c2.button("🗑", key=f"del_s_{s['nombre']}", help=f"Borrar {s['nombre']}"):
            borrar_s = s["nombre"]

    if borrar_s:
        st.session_state.sucesos = [s for s in sucesos if s["nombre"] != borrar_s]
        if f"s_{borrar_s}" in st.session_state:
            del st.session_state[f"s_{borrar_s}"]
        st.rerun()

    st.markdown("---")

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
        if st.button("Añadir personaje", type="primary"):
            if np_nombre.strip():
                personas.append(dict(
                    nombre=np_nombre.strip(),
                    nac=int(np_nac), muer=int(np_muer),
                    nac_aprox=np_nac_ap, muer_aprox=np_muer_ap,
                    genero="H" if "Hombre" in np_gen else "M"
                ))
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
        if st.button("Añadir suceso", type="primary"):
            if ns_nombre.strip():
                sucesos.append(dict(
                    nombre=ns_nombre.strip(),
                    año=int(ns_año),
                    personajes=ns_pers
                ))
                st.success(f"✅ Suceso '{ns_nombre}' añadido")
                st.rerun()
            else:
                st.error("El nombre es obligatorio")

    # ── Exportar ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 Exportar / Importar")

    datos_export = json.dumps({
        "titulo":   st.session_state.titulo,
        "yr_from":  st.session_state.yr_from,
        "yr_to":    st.session_state.yr_to,
        "personas": st.session_state.personas,
        "sucesos":  st.session_state.sucesos,
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
    st.markdown("---")
    if st.button("🔄 Restablecer datos originales"):
        st.session_state.personas = [p.copy() for p in PERSONAS_INIT]
        st.session_state.sucesos  = [s.copy() for s in SUCESOS_INIT]
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

n_rows  = len(visibles)
total_h = max(n_rows, 1) * ROW_H + 0.8

fig_h = max(4.0, n_rows * 0.55 + 1.5)
fig, ax = plt.subplots(figsize=(14, fig_h))
fig.patch.set_facecolor("white")

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
    ax.tick_params(axis="x", which="major", length=6, labelsize=8.5,
                   top=True, bottom=True, labeltop=True, labelbottom=True,
                   direction="out", color="#555")
    ax.tick_params(axis="x", which="minor", length=3,
                   top=True, bottom=True, direction="out", color="#aaa")
    ax.yaxis.set_visible(False)

    for spine in ["top","bottom","left","right"]:
        ax.spines[spine].set_edgecolor("#5b9bd5")
        ax.spines[spine].set_linewidth(1.8)

    for yr in range(yr_from, yr_to + 1, tick_major):
        ax.axvline(yr, color="#e2e5ea", linewidth=0.6, zorder=0)

    for i in range(n_rows):
        yb = total_h - (i + 1) * ROW_H
        if i % 2 == 0:
            ax.axhspan(yb, yb + ROW_H, color="#f0f3f8", zorder=0)

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
        y_c   = total_h - (i + 1) * ROW_H + ROW_H * 0.35
        color = COLOR_H if p["genero"] == "H" else COLOR_M
        sym   = "♂" if p["genero"] == "H" else "♀"

        nac_r  = p["nac"]
        muer_r = p["muer"]
        nac_ap  = p.get("nac_aprox",  False) or (nac_r  is None)
        muer_ap = p.get("muer_aprox", False) or (muer_r is None)

        x0 = max(nac_r  if nac_r  is not None else yr_from - 50, yr_from)
        x1 = min(muer_r if muer_r is not None else yr_to   + 50, yr_to)

        draw_arrow(x0, x1, y_c, color)

        if nac_ap and nac_r is not None and yr_from <= nac_r <= yr_to:
            ax.plot(nac_r, y_c, "o", color=color, markersize=5, zorder=4)
            ax.text(nac_r - span*0.004, y_c+0.08, "?", color=color,
                    fontsize=8, ha="right", va="bottom", zorder=4)
        if muer_ap and muer_r is not None and yr_from <= muer_r <= yr_to:
            ax.plot(muer_r, y_c, "o", color=color, markersize=5, zorder=4)
            ax.text(muer_r + span*0.004, y_c+0.08, "?", color=color,
                    fontsize=8, ha="left",  va="bottom", zorder=4)

        nac_str  = (str(nac_r)+"?")  if (nac_ap  and nac_r)  else (str(nac_r)  if nac_r  else "?")
        muer_str = (str(muer_r)+"?") if (muer_ap and muer_r) else (str(muer_r) if muer_r else "?")
        label = f"{sym} {p['nombre']}  {nac_str}–{muer_str}"

        ax.text((x0+x1)/2, y_c+0.14, label,
                color=color, fontsize=8.5, ha="center", va="bottom",
                fontweight="semibold", zorder=5,
                bbox=dict(boxstyle="round,pad=0.18", fc="#f8f9fb", ec="none", alpha=0.75))

    for s in sucesos:
        n = s["nombre"]
        if not sel_s.get(n, True):
            continue
        año = s["año"]
        if not (yr_from <= año <= yr_to):
            continue
        aff = [i for i, p in enumerate(visibles) if p["nombre"] in s["personajes"]]
        if aff:
            y_bot = total_h - (max(aff)+1)*ROW_H + ROW_H*0.1
            y_top = total_h - (min(aff)+1)*ROW_H + ROW_H*0.6
        else:
            y_bot, y_top = 0.1, total_h-0.1

        ax.plot([año, año], [y_bot, y_top], color=COLOR_EVT, linewidth=2.5, zorder=4)
        for i, p in enumerate(visibles):
            if p["nombre"] in s["personajes"]:
                y_c = total_h - (i+1)*ROW_H + ROW_H*0.35
                ax.plot(año, y_c, "o", color=COLOR_EVT, markersize=7, zorder=6,
                        markeredgecolor="white", markeredgewidth=1)
        ax.text(año + span*0.006, y_top+0.05, n,
                color=COLOR_EVT, fontsize=8, rotation=90,
                ha="left", va="bottom", fontweight="bold", zorder=7,
                bbox=dict(boxstyle="round,pad=0.15", fc="#fff8f7",
                          ec=COLOR_EVT, alpha=0.85, linewidth=0.8))

    # Leyenda
    legend_h = mpatches.Patch(color=COLOR_H, label="♂ Hombre")
    legend_m = mpatches.Patch(color=COLOR_M, label="♀ Mujer")
    legend_e = mpatches.Patch(color=COLOR_EVT, label="⚡ Suceso")
    ax.legend(handles=[legend_h, legend_m, legend_e],
              loc="lower right", fontsize=8, framealpha=0.85)

ax.set_title(titulo, pad=12, fontsize=13, fontweight="bold", color="#1e2030")
ax.set_xlabel("Año", labelpad=5, fontsize=9, color="#555")
fig.tight_layout(rect=[0, 0.02, 1, 0.98])

st.pyplot(fig, use_container_width=True)
plt.close(fig)

# Pie de página
st.markdown(
    "<div style='text-align:center; color:#aaa; font-size:12px; margin-top:8px'>"
    "Gráfica Temporal Biográfica · Edita los datos en el panel izquierdo"
    "</div>",
    unsafe_allow_html=True
)

