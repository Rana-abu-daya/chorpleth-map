import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide", page_title="Washington State Map")
############ counties #########
# Streamlit app title
st.title("Washington State Counties - Voter turnout (Nov 2024)")

# Load processed data
data_path = "Voter_Counties_data.csv"  # Replace with your data file path
data = pd.read_csv(data_path)

# Ensure County column matches GeoJSON field
data["County"] = data["County"].str.strip().str.title()

# Calculate non-voter counts if not included in the CSV
if "Non_Voters" not in data.columns:
    data["Non_Voters"] = data["total_population"] - data["voters"]

# Load GeoJSON file for Counties
geojson_path = "WA_County_Boundaries.geojson"  # Replace with your GeoJSON file path
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Extract county centroids for labeling
county_centroids = []
for feature in geojson_data["features"]:
    # Get the county name and calculate the center of the polygon
    county_name = feature["properties"]["JURISDICT_NM"]
    coordinates = feature["geometry"]["coordinates"]

    # For MultiPolygon, use the first polygon's centroid
    if feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0]

    # Calculate the centroid (average of all coordinates)
    lon = sum([point[0] for point in coordinates[0]]) / len(coordinates[0])
    lat = sum([point[1] for point in coordinates[0]]) / len(coordinates[0])

    # Add to centroids list
    county_centroids.append({"county": county_name, "lon": lon, "lat": lat})

# Create a DataFrame for centroids
centroid_df = pd.DataFrame(county_centroids)

# Define the updated color scale
colorscale = [
    [0, "darkred"],        # Very low voter rate
    [0.25, "red"],         # Moderate red
    [0.49, "lightcoral"],  # Light red approaching 50%
    [0.50, "lightgreen"],  # Neutral green for exactly 50%
    [0.75, "green"],       # Moderate green
    [1, "darkgreen"]       # High voter rate
]

# Create a Choropleth map for voter rate
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["County"],  # Match data column
    z=data["voter_rate"],  # Voter rate for coloring
    featureidkey="properties.JURISDICT_NM",  # Match GeoJSON key
    colorscale=colorscale,
    zmin=0,
    zmax=1,
    marker_opacity=0.8,  # Set transparency
    marker_line_width=1.2,  # Set boundary width for better clarity
    name="Voter Rate (%)",
    hovertemplate=(
        "<b>%{location}</b><br>"  # Displays the district name
        "Voter Rate: %{z:.2%}<br>"  # Converts voter rate (0-1) to percentage
        "<extra></extra>"  # Removes default "trace" name in hover
    )
))

# Add county labels and hover text
for _, row in centroid_df.iterrows():
    matching_data = data[data["County"] == row["county"]]
    if not matching_data.empty:
        voter_rate = matching_data["voter_rate"].values[0]
        voters = matching_data["voters"].values[0]
        non_voters = matching_data["non_voters"].values[0]

        # Add text labels
        fig.add_trace(go.Scattermapbox(
            lon=[row["lon"]],
            lat=[row["lat"]],
            mode="text",  # Only text is displayed
            text=[row["county"]],  # Display county name
            textfont=dict(size=10, color="black"),  # Adjust font size and color
            hoverinfo="text",  # Configure hover information
            hovertext=(
                f"<b>{row['county']}</b><br>"
                f"Voter Rate: {voter_rate:.2%}<br>"
                f"Voters: {voters}<br>"
                f"Non-Voters: {non_voters}"
            ),
            showlegend=False  # Hide legend for text
        ))

# Adjust map layout for Washington State
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,  # Zoom level for WA
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center on WA
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=800,  # Increased height for better visualization
    width=1000,  # Increased width for better visualization
    coloraxis_colorbar=dict(
        title="Voter Rate (%)",
        ticksuffix="%",
    ),
    legend=dict(orientation="h", y=-0.2)  # Adjust legend position
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)
  ################ City #################
# Streamlit app title
st.title("Washington State Cities - Voter turnout (Nov 2024)")
# Load the data
data_path = "preprocessed_ld_data_City.csv"  # Replace with your CSV file path
data = pd.read_csv(data_path)
data["City"] = data["City"].str.title()

# Calculate non-voter counts if not already included
if "non_voters" not in data.columns:
    data["non_voters"] = data["total_population"] - data["voters"]

# Load GeoJSON file for cities
geojson_path = "CityLimits.geojson"  # Replace with your GeoJSON file path
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Define color scale for voter rates
colorscale = [
    [0, "darkred"],        # Very low voter rate
    [0.25, "red"],         # Moderate red
    [0.49, "lightcoral"],  # Light red approaching 50%
    [0.50, "lightgreen"],  # Neutral green for exactly 50%
    [0.75, "green"],       # Moderate green
    [1, "darkgreen"]       # High voter rate
]

# Create a Choropleth map for voter rate
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["City"],  # Column from CSV
    z=data["voter_rate"],  # Voter rate for coloring
    featureidkey="properties.CITY_NM",  # Match GeoJSON key
    colorscale=colorscale,
    zmin=0,
    zmax=1,
    marker_opacity=0.8,  # Adjust transparency
    marker_line_width=1.2,  # Boundary width
    name="Voter Rate (%)",
    hovertemplate=(
        "<b>%{location}</b><br>"  # Displays the district name
        "Voter Rate: %{z:.2%}<br>"  # Converts voter rate (0-1) to percentage
        "<extra></extra>"  # Removes default "trace" name in hover
    )
))

# Add city labels with hover text
for feature in geojson_data["features"]:
    city_name = feature["properties"]["CITY_NM"]
    matching_data = data[data["City"] == city_name.title()]
    if not matching_data.empty:
        voter_rate = matching_data["voter_rate"].values[0]
        voters = matching_data["voters"].values[0]
        non_voters = matching_data["non_voters"].values[0]

        # Get the centroid of the city geometry
        coordinates = feature["geometry"]["coordinates"]
        if feature["geometry"]["type"] == "MultiPolygon":
            coordinates = coordinates[0]

        lon = sum([point[0] for point in coordinates[0]]) / len(coordinates[0])
        lat = sum([point[1] for point in coordinates[0]]) / len(coordinates[0])

        # Add scatter point for city
        fig.add_trace(go.Scattermapbox(
            lon=[lon],  # Longitude
            lat=[lat],  # Latitude
            mode="text",  # Only text displayed
            text=[city_name],  # City name
            textfont=dict(size=9, color="black"),  # Adjust font size and color
            hoverinfo="text",  # Configure hover information
            hovertext=(
                f"<b>{city_name}</b><br>"
                f"Voter Rate: {voter_rate:.2%}<br>"
                f"Voters: {voters}<br>"
                f"Non-Voters: {non_voters}"
            ),
            showlegend=False  # Hide legend for text
        ))

# Adjust map layout
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,  # Adjust zoom level
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center the map on Washington State
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=800,  # Increased height for better visualization
    width=1000,  # Increased width for better visualization
    coloraxis_colorbar=dict(
        title="Voter Rate (%)",
        ticksuffix="%",
    )
)

# Display the map in Streamlit
st.plotly_chart(fig, use_container_width=True)



############ School District #############

st.title("Washington State School District-  Voter turnout (Nov 2024)")

# Step 1: Load CSV data
data_path = "Voter_SD_data.csv"  # Replace with your CSV file path
data = pd.read_csv(data_path)

# Ensure School District column matches GeoJSON field
data["School District"] = data["School District"].str.strip().str.title()

# Calculate non-voter counts if not already included
if "non_voters" not in data.columns:
    data["non_voters"] = data["total_population"] - data["voters"]

# Step 2: Load GeoJSON for School Districts
geojson_path = "Washington_School_Districts_2024.geojson"  # Replace with your GeoJSON file path
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Step 3: Define color scale for voter rates
colorscale = [
    [0, "darkred"],        # Very low voter rate
    [0.25, "red"],         # Moderate red
    [0.49, "lightcoral"],  # Light red approaching 50%
    [0.50, "lightgreen"],  # Neutral green for exactly 50%
    [0.75, "green"],       # Moderate green
    [1, "darkgreen"]       # High voter rate
]

# Step 4: Create the Choropleth map
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["School District"],  # Match data column
    z=data["voter_rate"],  # Voter rate for coloring
    featureidkey="properties.LEAName",  # Match GeoJSON key for school districts
    colorscale=colorscale,
    zmin=0,
    zmax=1,
    marker_opacity=0.8,  # Set transparency
    marker_line_width=1.2,  # Set boundary width
    name="Voter Rate (%)",
    hovertemplate=(
        "<b>%{location}</b><br>"  # Displays the district name
        "Voter Rate: %{z:.2%}<br>"  # Converts voter rate (0-1) to percentage
        "<extra></extra>"  # Removes default "trace" name in hover
    )
))

# Step 5: Add School District Labels
# Extract centroids for labeling
district_centroids = []
for feature in geojson_data["features"]:
    district_name = feature["properties"]["LEAName"]
    coordinates = feature["geometry"]["coordinates"]

    # For MultiPolygon, use the first polygon's centroid
    if feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0]

    # Calculate the centroid (average of all coordinates)
    lon = sum([point[0] for point in coordinates[0]]) / len(coordinates[0])
    lat = sum([point[1] for point in coordinates[0]]) / len(coordinates[0])

    # Add to centroids list
    district_centroids.append({"district": district_name, "lon": lon, "lat": lat})

# Create a DataFrame for centroids
centroid_df = pd.DataFrame(district_centroids)

# Add district labels as text
for _, row in centroid_df.iterrows():
    # Check if the district exists in the data
    matching_data = data[data['School District'] == row['district']]
    if not matching_data.empty:
        voter_rate = matching_data["voter_rate"].values[0]
        voters = matching_data["voters"].values[0]
        non_voters = matching_data["non_voters"].values[0]

        fig.add_trace(go.Scattermapbox(
            lon=[row["lon"]],  # Longitude of the centroid
            lat=[row["lat"]],  # Latitude of the centroid
            mode="text",  # Only text is displayed on the map
            text=[f"{row['district']}"],  # Display only the school district name on the map
            textfont=dict(size=9, color="black"),  # Adjust font size and color
            hoverinfo="text",  # Configure hover information
            hovertext=(
                f"<b>{row['district']}</b><br>"
                f"Voter Rate: {voter_rate:.2%}<br>"
                f"Voters: {voters}<br>"
                f"Non-Voters: {non_voters}"
            ),
            showlegend=False  # Hide legend for text
        ))

fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,  # Zoom level for WA
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center on WA
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=600,
    width=800,  # Adjust map width
    coloraxis_colorbar=dict(
        title="Voter Rate (%)",  # Add a clear title
        ticksuffix="%",
    )
)

# Step 7: Display the map in Streamlit
st.plotly_chart(fig, use_container_width=True)
########################### LD #########################
# Streamlit app title
st.title("Washington State Legislative District - Voter turnout (Nov 2024)")

# Load data
data_path = "preprocessed_ld_data.csv"  # Replace with your CSV file
data = pd.read_csv(data_path)

# Ensure columns are correct
data["Legislative District"] = data["Legislative District"].apply(
    lambda x: f"Legislative (House) District {int(float(x))}" if pd.notna(x) else None
)
data["non_voters"] = data["total_population"] - data["voters"]

# Load GeoJSON file
geojson_path = "wa_legislative_districts.geojson"  # Replace with your GeoJSON file
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Calculate centroids for districts
centroids = []
for feature in geojson_data["features"]:
    district_name = feature["properties"]["NAMELSAD"]
    coordinates = feature["geometry"]["coordinates"]

    # Handle MultiPolygon
    if feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0]

    # Centroid calculation
    lon = sum([point[0] for point in coordinates[0]]) / len(coordinates[0])
    lat = sum([point[1] for point in coordinates[0]]) / len(coordinates[0])
    centroids.append({"district": district_name, "lon": lon, "lat": lat})

centroid_df = pd.DataFrame(centroids)

# Create a custom colorscale for voter rate
# Green for voter turnout >= 50%, red for turnout < 50%
colorscale = [
    [0, "darkred"],        # Very low voter rate
    [0.25, "red"],         # Moderate red
    [0.49, "lightcoral"],  # Light red approaching 50%
    [0.50, "lightgreen"],  # Neutral green for exactly 50%
    [0.75, "green"],       # Moderate green
    [1, "darkgreen"]       # High voter rate
]

# Create a choropleth map for the voter rate
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["Legislative District"],  # Match column in data
    z=data["voter_rate"],  # Voter rate for coloring
    featureidkey="properties.NAMELSAD",  # Match GeoJSON key
    colorscale=colorscale,
    zmin=0,
    zmax=1,
    marker_opacity=0.8,
    marker_line_width=1.2,
    name="Voter Rate (%)",
    hovertemplate=(
        "<b>%{location}</b><br>"  # Displays the district name
        "Voter Rate: %{z:.2%}<br>"  # Converts voter rate (0-1) to percentage
        "<extra></extra>"  # Removes default "trace" name in hover
    )
    # Configure hover information


))

# Add district names as text labels on the map
for _, row in centroid_df.iterrows():
    matching_data = data[data["Legislative District"] == row["district"]]
    if not matching_data.empty:
        voter_rate = matching_data["voter_rate"].values[0]
        voters = matching_data["voters"].values[0]
        non_voters = matching_data["non_voters"].values[0]

        # Add text labels
        fig.add_trace(go.Scattermapbox(
            lon=[row["lon"]],
            lat=[row["lat"]],
            mode="text",  # Only text is displayed
            text=[row["district"]],  # Display district name
            textfont=dict(size=10, color="black"),  # Adjust font size and color
            hoverinfo="text",  # Configure hover information
            hovertext=(
                f"<b>{row['district']}</b><br>"
                f"Voter Rate: {voter_rate:.2f}%<br>"
                f"Voters: {voters}<br>"
                f"Non-Voters: {non_voters}"
            ),
            showlegend=False  # Hide legend for text
        ))

# Update map layout
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,
    mapbox_center={"lat": 47.7511, "lon": -120.7401},
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=800,  # Increased height for better visualization
    width=1000,  # Increased width for better visualization
    coloraxis_colorbar=dict(
        title="Voter Rate (%)",
        tickvals=[0, 0.25, 0.5, 0.75, 1],  # Tick points for the colorbar
        ticktext=["0%", "25%", "50%", "75%", "100%"],  # Tick labels
    ),
    legend=dict(orientation="h", y=-0.2)  # Adjust legend position
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)


############### CD ################################


# Streamlit app title
st.title("Washington State Congressional Districts - Voter turnout (Nov 2024)")

# Load CSV data
csv_path = "preprocessed_ld_data_Congressional District.csv"  # Replace with your CSV file
data = pd.read_csv(csv_path)

# Ensure Congressional District names match GeoJSON keys
data["Congressional District"] = data["Congressional District"].str.strip().str.title()

# Load GeoJSON data
geojson_path = "Congressional District.geojson"  # Replace with your GeoJSON file
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Debug to verify matching keys
geojson_keys = [feature["properties"]["NAMELSAD"] for feature in geojson_data["features"]]
data_keys = data["Congressional District"].unique()
if not set(data_keys).issubset(set(geojson_keys)):
    st.write("Warning: Mismatch between CSV and GeoJSON district names.")
    st.write(f"CSV Keys: {data_keys}")
    st.write(f"GeoJSON Keys: {geojson_keys}")

# Define color scale (same as LD)
colorscale = [
    [0, "darkred"],        # Very low voter rate
    [0.25, "red"],         # Moderate red
    [0.49, "lightcoral"],  # Light red approaching 50%
    [0.50, "lightgreen"],  # Neutral green for exactly 50%
    [0.75, "green"],       # Moderate green
    [1, "darkgreen"]       # High voter rate
]

# Create the map
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["Congressional District"],  # Column in the CSV
    z=data["voter_rate"],  # Voter rate for color scale
    featureidkey="properties.NAMELSAD",  # GeoJSON key to match with locations
    colorscale=colorscale,  # Use the LD color scale
    zmin=0,
    zmax=1,
    colorbar_title="Voter Rate (%)",  # Title for the color bar
    marker_opacity=0.8,  # Adjust opacity
    marker_line_width=1.2 ,
    hovertemplate=(
        "<b>%{location}</b><br>"  # Displays the district name
        "Voter Rate: %{z:.2%}<br>"  # Converts voter rate (0-1) to percentage
        "<extra></extra>"  # Removes default "trace" name in hover
    )
    # Boundary width
))

# Add district labels (optional)
district_labels = []
for feature in geojson_data["features"]:
    name = feature["properties"]["NAMELSAD"]
    coordinates = feature["geometry"]["coordinates"]

    # Handle both Polygon and MultiPolygon
    if feature["geometry"]["type"] == "Polygon":
        coordinates = coordinates[0]
    elif feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0][0]

    # Calculate the centroid
    lon = sum([point[0] for point in coordinates]) / len(coordinates)
    lat = sum([point[1] for point in coordinates]) / len(coordinates)

    # Add to district_labels
    district_labels.append({"district": name, "lon": lon, "lat": lat})

# Add district labels to the map
for label in district_labels:
    matching_data = data[data["Congressional District"] == label["district"]]
    if not matching_data.empty:
        voter_rate = matching_data["voter_rate"].values[0]
        voters = matching_data["voters"].values[0]
        non_voters = matching_data["non_voters"].values[0]

        fig.add_trace(go.Scattermapbox(
            lon=[label["lon"]],
            lat=[label["lat"]],
            mode="text",
            text=label["district"].split()[-1],  # Display only the district number
            textfont=dict(size=12, color="black"),
            hoverinfo="text",
            hovertext=(
                f"<b>{label['district']}</b><br>"
                f"Voter Rate: {voter_rate:.2%}<br>"
                f"Voters: {voters}<br>"
                f"Non-Voters: {non_voters}"
            ),
            showlegend=False
        ))

# Update map layout
fig.update_layout(
    mapbox_style="carto-positron",  # Map style
    mapbox_zoom=6,  # Zoom level
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center on Washington State
    margin={"r": 0, "t": 0, "l": 0, "b": 0},  # Remove margins
    height=600,
    width=800,
    coloraxis_colorbar=dict(
        title="Voter Rate (%)",
        ticksuffix="%",
    )
)

# Display the map
st.plotly_chart(fig, use_container_width=True)

