import streamlit as st
import pandas as pd
import requests

# Set WeatherAPI.com API key
API_KEY = '3aa549f4d6f3491ab43202903230212'

# Function to fetch weather data from WeatherAPI.com
def get_weather_data(city, key):
    url = f'http://api.weatherapi.com/v1/current.json?key={key}&q={city}'
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        st.error(f"Error fetching data. Status code: {response.status_code}")
        return None

    data = response.json()
    return data

# Streamlit app
st.sidebar.header("Weather App")
city = st.sidebar.text_input("Enter City", "London")

# Date and time input
selected_date = st.sidebar.date_input("Select a Date", pd.to_datetime('today'))
selected_time = st.sidebar.time_input("Select a Time", pd.to_datetime('12:00 PM'))

# Combine date and time into a single datetime object
selected_datetime = pd.to_datetime(str(selected_date) + ' ' + str(selected_time))
# Fetch weather data
weather_data = get_weather_data(city, API_KEY)
# Temperature unit slider
temperature_unit = st.sidebar.slider("Select Temperature Unit", min_value=0, max_value=1, step=1, format="%d", key="temp_unit")
unit_label = "Celsius" if temperature_unit == 0 else "Fahrenheit"

# Check if data is fetched successfully
if weather_data:
    # Display weather information
    st.title(f"Weather Forecast for {city}")

    # Check if 'current' key is present in the response
    if 'current' in weather_data:
        # Interactive table with current weather details
        st.subheader("Current Weather Details")
        current_weather_df = pd.json_normalize(weather_data['current'])
        st.table(current_weather_df)

        # Area chart for humidity
        st.subheader("Humidity Area Chart")
        st.area_chart(current_weather_df[['humidity']].rename(columns={'humidity': 'Humidity (%)'}))

        # Bar chart for wind speed
        st.subheader("Wind Speed Bar Chart")
        selected_color = st.color_picker("Select Color", "#ff5733")
        st.bar_chart(current_weather_df[['wind_kph']].rename(columns={'wind_kph': 'Wind Speed (kph)'}), color=selected_color)
        

        # Map with points marked on it
        st.subheader("Map with Location")

        # Extract latitude and longitude from the 'location' key
        location = weather_data.get('location', {})
        latitude = location.get('lat', None)
        longitude = location.get('lon', None)

        # Check if latitude and longitude are available
        if latitude is not None and longitude is not None:
            # Create a DataFrame with latitude and longitude columns
            location_df = pd.DataFrame({'LAT': [latitude], 'LON': [longitude]})

            # Display the map
            st.map(location_df)
        else:
            st.warning("Latitude and longitude information is not available.")
    else:
        st.error("Unexpected response format. Please check the API documentation.")
else:
    st.error("Failed to fetch weather data. Please check the API key and try again.")

# Text input for weather condition
weather_condition = st.text_input("Enter Weather Condition", "Clear Sky")
st.write(f"You entered: {weather_condition}")

# Button widget
if st.button("Refresh Data"):
    weather_data = get_weather_data(city, API_KEY)

# Checkbox widget
show_details = st.checkbox("Show Additional Details")

# Essential feedback and messages boxes
if show_details:
    st.success("Data refreshed successfully!")
else:
    st.info("Toggle the checkbox to show additional details.")
