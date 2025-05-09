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
positions_data = []

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

        # Extract relevant data for the tooltip
        name = row['NAME']
        epoch = row['EPOCH']
        inclination = row['INCL']
        raan = row['RAAN']
        eccentricity = row['ECC']
        arg_perigee = row['ARG_PER']
        mean_anomaly = row['MEAN_ANOM']
        mean_motion = row['MEAN_MOTION']
        sma = row['SMA_KM']
        apogee = row['APOGEE_KM']
        perigee = row['PERIGEE_KM']
        mean_motion_deriv = row['MEAN_MOTION_1ST_DER']

        positions_data.append({
            'name': name,
            'type': obj_type,
            'orbit': orbit,
            'epoch': epoch,
            'inclination': inclination,
            'raan': raan,
            'eccentricity': eccentricity,
            'arg_perigee': arg_perigee,
            'mean_anomaly': mean_anomaly,
            'mean_motion': mean_motion,
            'sma_km': sma,
            'apogee_km': apogee,
            'perigee_km': perigee,
            'mean_motion_1st_der': mean_motion_deriv,
            'x': pos[0],
            'y': pos[1],
            'z': pos[2],
        })
    except Exception as e:
        print(f"Error processing row: {e}")
        continue

df_plot = pd.DataFrame(positions_data)

# === Orbit shell helper ===
def make_shell(radius, color, opacity=0.15):
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
    ("LEO", 8371, "lightgray"),
    ("MEO", 26571, "lightsalmon"),
    ("GEO", 42157, "lightgoldenrodyellow"),
    ("HEO", 60000, "plum")
]

for name, radius, color in shells:
    fig.add_trace(make_shell(radius, color))
    fig.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(size=10, color=color),
        name=name,
        hoverinfo='name' # Only show the name on hover for shells
    ))

# Add filtered satellites with hover information
for obj_type in selected_types:
    df_type = df_plot[df_plot['type'] == obj_type]
    for orbit in selected_orbits:
        df_orbit_type = df_type[df_type['orbit'] == orbit]
        if not df_orbit_type.empty:
            fig.add_trace(go.Scatter3d(
                x=df_orbit_type['x'],
                y=df_orbit_type['y'],
                z=df_orbit_type['z'],
                mode='markers',
                marker=dict(size=3, color=type_colors[obj_type]),
                name=f"{obj_type.title()} ({orbit})",
                hovertemplate=(
                    f"<b>Name</b>: %{{customdata[0]}}<br>"
                    f"<b>Type</b>: %{{customdata[1]}}<br>"
                    f"<b>Regime</b>: %{{customdata[2]}}<br>"
                    f"<b>Epoch</b>: %{{customdata[3]}}<br>"
                    f"<b>Inclination</b>: %{{customdata[4]:.2f}} deg<br>"
                    f"<b>RAAN</b>: %{{customdata[5]:.2f}} deg<br>"
                    f"<b>Eccentricity</b>: %{{customdata[6]:.6f}}<br>"
                    f"<b>Arg Per</b>: %{{customdata[7]:.2f}} deg<br>"
                    f"<b>Mean Anom</b>: %{{customdata[8]:.2f}} deg<br>"
                    f"<b>Mean Motion</b>: %{{customdata[9]:.4f}} rev/day<br>"
                    f"<b>SMA</b>: %{{customdata[10]:.2f}} km<br>"
                    f"<b>Apogee</b>: %{{customdata[11]:.2f}} km<br>"
                    f"<b>Perigee</b>: %{{customdata[12]:.2f}} km<br>"
                    f"<b>Mean Motion Deriv</b>: %{{customdata[13]:.8f}}<br>"
                    f"X: %{{x:.2f}} km<br>"
                    f"Y: %{{y:.2f}} km<br>"
                    f"Z: %{{z:.2f}} km<br>"
                    "<extra></extra>"
                ),
                customdata=np.stack([
                    df_orbit_type['name'],
                    df_orbit_type['type'].str.title(),
                    df_orbit_type['orbit'],
                    df_orbit_type['epoch'],
                    df_orbit_type['inclination'],
                    df_orbit_type['raan'],
                    df_orbit_type['eccentricity'],
                    df_orbit_type['arg_perigee'],
                    df_orbit_type['mean_anomaly'],
                    df_orbit_type['mean_motion'],
                    df_orbit_type['sma_km'],
                    df_orbit_type['apogee_km'],
                    df_orbit_type['perigee_km'],
                    df_orbit_type['mean_motion_1st_der'],
                    df_orbit_type['x'],
                    df_orbit_type['y'],
                    df_orbit_type['z']
                ], axis=-1)
            ))

# Layout
fig.update_layout(
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data',
        bgcolor="black",
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
        zaxis=dict(color='white')
    ),
    title=dict(text=f"Satellite Positions on {selected_date}", font=dict(color='white')),
    margin=dict(l=0, r=0, b=0, t=30),
    legend=dict(title='Legend', font=dict(color='white')),
    plot_bgcolor='black',
    paper_bgcolor='black',
    hovermode='closest'  # Add this line
)

st.title("3D Satellite Visualization")
st.plotly_chart(fig, use_container_width=True)