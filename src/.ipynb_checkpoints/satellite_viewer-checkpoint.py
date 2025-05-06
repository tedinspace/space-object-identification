import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from skyfield.api import load, EarthSatellite

# === Load and preprocess CSV ===
@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_csv('../data/large/final_df_v1.csv')
    df = df.dropna(subset=['LINE1', 'LINE2', 'TYPE'])

    # Parse TLE epochs to date
    ts = load.timescale()
    epochs = []
    for i, row in df.iterrows():
        try:
            sat = EarthSatellite(row['LINE1'], row['LINE2'], name='', ts=ts)
            epochs.append(sat.epoch.utc_datetime().date())
        except:
            epochs.append(None)

    df['TLE_DATE'] = epochs
    df = df.dropna(subset=['TLE_DATE'])
    return df

df = load_data()

# === Sidebar Filters ===
available_dates = sorted(df['TLE_DATE'].unique())
selected_date = st.sidebar.selectbox("Select TLE Epoch Date", available_dates)

# Object types
all_types = ['payload', 'rocket body', 'debris']
selected_types = st.sidebar.multiselect(
    "Object Types",
    all_types,
    default=all_types
)

# Orbit regimes
orbit_classes = ['LEO', 'MEO', 'GEO', 'HEO']
selected_orbits = st.sidebar.multiselect(
    "Orbit Regimes",
    orbit_classes,
    default=orbit_classes
)

# === Skyfield setup ===
ts = load.timescale()
t = ts.utc(selected_date.year, selected_date.month, selected_date.day)

# === Orbit classification helper ===
def classify_orbit(radius_km):
    if radius_km < 8371:        # < ~2000 km alt
        return 'LEO'
    elif radius_km < 42157 - 1000:
        return 'MEO'
    elif abs(radius_km - 42157) < 1000:
        return 'GEO'
    else:
        return 'HEO'  # Includes > GEO and > 60000 km

# === Color mapping ===
type_colors = {
    'payload': 'blue',
    'rocket body': 'red',
    'debris': 'green'
}

# === Filter and compute satellite positions ===
positions_by_type_and_orbit = {}

df_filtered = df[df['TLE_DATE'] == selected_date]

for _, row in df_filtered.iterrows():
    try:
        obj_type = row['TYPE'].strip().lower()
        if obj_type not in selected_types:
            continue

        sat = EarthSatellite(row['LINE1'], row['LINE2'], name='', ts=ts)
        pos = sat.at(t).position.km
        radius = np.linalg.norm(pos)
        orbit = classify_orbit(radius)
        if orbit not in selected_orbits:
            continue

        key = (obj_type, orbit)
        positions_by_type_and_orbit.setdefault(key, []).append((pos[0], pos[1], pos[2]))
    except:
        continue

# === Orbit shell helper ===
def make_shell(radius, color, opacity=0.08):
    u, v = np.mgrid[0:2*np.pi:60j, 0:np.pi:30j]
    x = radius * np.cos(u) * np.sin(v)
    y = radius * np.sin(u) * np.sin(v)
    z = radius * np.cos(v)
    return go.Surface(
        x=x, y=y, z=z,
        opacity=opacity,
        colorscale=[[0, color], [1, color]],
        showscale=False,
        hoverinfo='skip'
    )

# === Plot setup ===
fig = go.Figure()

# Orbit shells and dummy legend entries
shells = [
    ("Earth", 6371, "lightblue"),
    ("LEO Shell", 8371, "gray"),
    ("MEO Shell", 26571, "orange"),
    ("GEO Shell", 42157, "gold"),
    ("HEO Shell", 60000, "purple")
]

for name, radius, color in shells:
    fig.add_trace(make_shell(radius, color))
    fig.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(size=10, color=color),
        name=name
    ))

# Add filtered satellites
for (obj_type, orbit), coords in positions_by_type_and_orbit.items():
    x, y, z = zip(*coords)
    label = f"{obj_type.title()} ({orbit})"
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=3, color=type_colors[obj_type]),
        name=label,
        hoverinfo='skip'
    ))

# Layout
fig.update_layout(
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    ),
    title=f"Satellite Positions on {selected_date}",
    margin=dict(l=0, r=0, b=0, t=30),
    legend_title='Legend'
)

st.title("3D Satellite Visualization with Type & Orbit Filters")
st.plotly_chart(fig, use_container_width=True)