import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="RegLab Tool Starter", layout="wide")

# --- PROFESSIONAL STYLING ---
# This CSS hides the Streamlit "hamburger" menu and footer for a cleaner look
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# --- AUTHENTICATION ---
def get_secret(key):
    """Helper to get secrets from Streamlit secrets or Environment Variables."""
    try:
        # 1. Try Streamlit Secrets (local secrets.toml or Streamlit Cloud)
        if key in st.secrets:
            return st.secrets[key]
        if key.upper() in st.secrets:
            return st.secrets[key.upper()]
    except Exception:
        pass

    # 2. Fallback to Environment Variables (Railway, Render, etc.)
    return os.environ.get(key) or os.environ.get(key.upper())


def check_password():
    """Returns `True` if the user had the correct password."""
    master_password = get_secret("password")

    if not master_password:
        return True

    # If already authenticated, just return True
    if st.session_state.get("password_correct"):
        return True

    # Show the login form
    st.subheader("🔒 Password Required")
    user_password = st.text_input("Please enter the password", type="password")

    if user_password:
        if str(user_password).strip() == str(master_password).strip():
            st.session_state["password_correct"] = True
            st.rerun()  # Refresh the app to show the content
        else:
            st.error("😕 Password incorrect")

    return False


# --- APP START ---

# 1. AUTHENTICATION CHECK
# We use our helper to check for the password
if not check_password():
    st.stop()

# 2. HEADER SECTION
st.title("🧪 Researcher's Web App Starter")
st.markdown("""
Welcome! This app is a template to help you turn your data scripts into interactive tools.
Edit `app.py` to customize this.
""")

# 3. SIDEBAR - INPUTS
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV or JSON file", type=["csv", "json"])

    st.info("💡 **Pro-tip:** Use `st.sidebar` to keep controls organized.")

# 4. MAIN CONTENT - Create tabs that are always visible
tab1, tab2, tab3 = st.tabs(["📊 Data Analysis", "🗺️ Santa Map", "📈 Statistics"])

# Helper function to create Santa map
def create_santa_map():
    """Creates the US map with animated Santa GIF"""
    st.subheader("🎅 Santa's Journey Across America")
    
    # Create a base map of the US using Plotly
    fig = go.Figure()
    
    # Add a simple US outline using scattergeo (centered on continental US)
    fig.add_trace(go.Scattergeo(
        lon=[-125, -66, -66, -125, -125],  # US bounding box
        lat=[25, 25, 49, 49, 25],
        mode='lines',
        line=dict(width=0, color='rgba(0,0,0,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Configure the map layout
    fig.update_geos(
        visible=True,
        resolution=50,
        scope='usa',
        showcountries=False,
        showcoastlines=True,
        coastlinecolor="LightGray",
        showland=True,
        landcolor="WhiteSmoke",
        showocean=True,
        oceancolor="LightBlue",
        projection_type='albers usa',
        lonaxis_range=[-125, -66],
        lataxis_range=[25, 49]
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            lakecolor='LightBlue',
            rivercolor='LightBlue'
        )
    )
    
    # Santa GIF URL
    santa_gif_url = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnJ1eTJpaWlyaTVkZ3E1anZlamExOWM5OHZjbWhoN3ZvemVjYjl3NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mATqoqwcLzqNKkLcOR/giphy.gif"
    
    # Create a container with Santa positioned to overlay the map
    # Using a wrapper div that will be positioned relative to the map
    santa_overlay_html = f"""
    <div style="
        position: relative;
        width: 100%;
        margin-bottom: -600px;
        height: 600px;
        z-index: 1000;
        pointer-events: none;
    ">
        <div id="santa-flyer" style="
            position: absolute;
            top: 50%;
            left: 95%;
            width: 80px;
            height: 80px;
            pointer-events: none;
            z-index: 1001;
            animation: santaFlyEastWest 15s linear infinite;
            transform: translate(-50%, -50%);
        ">
            <img src="{santa_gif_url}" alt="🎅 Santa flying east to west" style="width: 100%; height: 100%; object-fit: contain;" />
        </div>
    </div>
    
    <style>
    @keyframes santaFlyEastWest {{
        0% {{ 
            left: 95%;
        }}
        100% {{ 
            left: 5%;
        }}
    }}
    </style>
    """
    
    st.markdown(santa_overlay_html, unsafe_allow_html=True)
    
    # Display the map (600px height) - Santa overlay positioned above it
    st.plotly_chart(fig, use_container_width=True, key="santa_map")

# Load data if file uploaded
df = None
filtered_df = None
if uploaded_file is not None:
    # Determine file type and load accordingly
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)
    filtered_df = df

# TAB 2: Santa Map (always visible)
with tab2:
    create_santa_map()
    
    # If file is uploaded, also show data points
    if df is not None and "Latitude" in df.columns and "Longitude" in df.columns:
        st.divider()
        st.subheader("Your Data Points")
        st.map(filtered_df, latitude="Latitude", longitude="Longitude")

# TAB 1 & 3: Data Analysis and Statistics (only when file uploaded)
if uploaded_file is not None:
    with tab1:
        st.subheader("Data Overview")
        st.write(f"Showing {len(df)} rows:")
        st.dataframe(df, use_container_width=True)

        # FILTERING
        st.divider()
        st.subheader("Interactive Analysis")

        col1, col2 = st.columns(2)

        with col1:
            if "Category" in df.columns:
                categories = df["Category"].unique()
                selected_cat = st.multiselect(
                    "Filter by Category", options=categories, default=categories
                )
                filtered_df = df[df["Category"].isin(selected_cat)]
            else:
                filtered_df = df
                st.warning("No 'Category' column found for filtering.")

        with col2:
            if "Value" in df.columns:
                min_val, max_val = int(df["Value"].min()), int(df["Value"].max())
                val_range = st.slider(
                    "Filter by Value Range", min_val, max_val, (min_val, max_val)
                )
                filtered_df = filtered_df[
                    (filtered_df["Value"] >= val_range[0])
                    & (filtered_df["Value"] <= val_range[1])
                ]
            else:
                filtered_df = df

        # VISUALIZATION
        st.write(f"Filtered results: {len(filtered_df)} rows")

        if not filtered_df.empty:
            fig = px.bar(
                filtered_df,
                x=filtered_df.index,
                y="Value",
                color="Date",
                title="Values by Category",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the current filters.")

    with tab3:
        st.write("Summary Statistics:")
        st.write(filtered_df.describe())

else:
    # No file uploaded - show placeholder content in tabs
    with tab1:
        st.info(
            "Please upload a file to get started. You can find sample data in the `sample_data` folder."
        )
        if st.checkbox("Show Example Data"):
            example_path = "sample_data/example.csv"
            if os.path.exists(example_path):
                df_example = pd.read_csv(example_path)
                st.write("This is what `example.csv` looks like:")
                st.dataframe(df_example.head())
                if "Latitude" in df_example.columns and "Longitude" in df_example.columns:
                    st.map(df_example, latitude="Latitude", longitude="Longitude")
                else:
                    st.warning("No 'Latitude' or 'Longitude' columns found for mapping.")
            else:
                st.error("Example file not found.")

    with tab3:
        st.info("Upload a file to see statistics here.")

# --- FOOTER ---
st.divider()
st.caption("Built by Salil • 2025 Researcher Workshop")

# --- SUMMARY OF COMMON COMMANDS ---
# 1. st.write() - The Swiss Army knife: prints text, dataframes, objects.
# 2. st.dataframe() - Displays interactive tables.
# 3. st.selectbox() / st.multiselect() - For dropdown menus.
# 4. st.slider() - For numeric range input.
# 5. st.file_uploader() - To let users upload their own data.
# 6. st.columns() - To layout your app side-by-side.
# 7. st.sidebar - To put controls in the left panel.
# 8. st.plotly_chart() - For beautiful interactive charts.
# 9. st.map() - For quick geospatial visualization.
# 10. st.secrets - For accessing API keys or passwords securely.
