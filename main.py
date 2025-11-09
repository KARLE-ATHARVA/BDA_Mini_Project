# -------------------------------------------------------------
# 🌤️ Real-Time Weather Tracker 4.2
# Big Data Analytics Mini Project | VS Code Live Dashboard
# -------------------------------------------------------------
# Author: Atharva Karle
# Description:
#   Continuously fetches live weather data, logs it, and shows
#   a real-time temperature chart in a Matplotlib window.
#   Press Ctrl + C anytime to stop logging.
# -------------------------------------------------------------

import requests, pandas as pd, matplotlib.pyplot as plt
import datetime, os, json, time, matplotlib

# Force GUI backend for local run
matplotlib.use("TkAgg")

# -------------------------------
# 🔧 Utility Functions
# -------------------------------

def get_city_coordinates(city_name):
    """Fetch latitude and longitude for a given city using Open-Meteo Geocoding API."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
        res = requests.get(geo_url).json()
        if "results" not in res:
            raise ValueError("City not found.")
        info = res["results"][0]
        return info["latitude"], info["longitude"], info["name"]
    except Exception as e:
        print(f"⚠️ Error fetching city coordinates: {e}")
        return None, None, None


def fetch_weather(lat, lon):
    """Fetch real-time weather data using Open-Meteo API."""
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}&current=temperature_2m,"
               f"relative_humidity_2m,wind_speed_10m")
        data = requests.get(url).json()
        return data.get("current", None)
    except Exception as e:
        print(f"⚠️ Error fetching weather data: {e}")
        return None


def append_to_logs(entry):
    """Append entry to CSV and JSON logs."""
    csv_path, json_path = "weather_log.csv", "weather_log.json"
    pd.DataFrame([entry]).to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
    if os.path.exists(json_path):
        with open(json_path, "r+") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=4)
    else:
        with open(json_path, "w") as f:
            json.dump([entry], f, indent=4)


def show_summary_dashboard(city):
    """Display analytics summary after logging stops."""
    try:
        df = pd.read_csv("weather_log.csv")
        df_city = df[df["city"] == city]

        print("\n📊 Final Weather Analytics Summary:")
        print("-----------------------------------------------------")
        print(f"🌆 City: {city}")
        print(f"🕒 Entries Logged: {len(df_city)}")
        print(f"🌡️ Avg Temp: {df_city['temperature'].mean():.2f}°C")
        print(f"🔥 Max Temp: {df_city['temperature'].max():.2f}°C")
        print(f"❄️ Min Temp: {df_city['temperature'].min():.2f}°C")
        print(f"📈 Temp Variance: {df_city['temperature'].var():.2f}")
        print(f"💧 Avg Humidity: {df_city['humidity'].mean():.2f}%")
        print(f"🌬️ Avg Wind Speed: {df_city['windspeed'].mean():.2f} km/h")
        print("-----------------------------------------------------")

        plt.figure(figsize=(8, 4))
        plt.plot(df_city["timestamp"], df_city["temperature"], 'r-o', label="Temperature (°C)")
        plt.title(f"Historical Temperature Trend - {city}")
        plt.xlabel("Timestamp")
        plt.ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print("⚠️ Could not load summary:", e)


# -------------------------------
# 📊 Continuous Dashboard Loop
# -------------------------------

def live_weather_dashboard(city, interval_seconds=30):
    """Continuously update live dashboard until user stops."""
    lat, lon, cname = get_city_coordinates(city)
    if not lat:
        print("❌ Invalid city name.")
        return

    print(f"\n📍 City: {cname} | Fetch interval: {interval_seconds}s")
    print("Press Ctrl + C to stop logging anytime.\n")

    # Setup live plot
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    times, temps = [], []
    iteration = 0

    try:
        while True:
            iteration += 1
            data = fetch_weather(lat, lon)
            if not data:
                print("⚠️ API error, retrying...")
                time.sleep(interval_seconds)
                continue

            now = datetime.datetime.now()
            temp = data["temperature_2m"]
            entry = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "city": cname,
                "temperature": temp,
                "humidity": data["relative_humidity_2m"],
                "windspeed": data["wind_speed_10m"]
            }
            append_to_logs(entry)

            times.append(now.strftime("%H:%M:%S"))
            temps.append(temp)

            # Update live plot
            ax.clear()
            ax.plot(times, temps, 'r-o', label="Temperature (°C)")
            avg_t = sum(temps)/len(temps)
            ax.set_title(f"🌦️ {cname} | Now: {temp:.1f}°C | Avg: {avg_t:.1f}°C")
            ax.set_xlabel("Timestamp")
            ax.set_ylabel("Temperature (°C)")
            ax.set_xticks(range(len(times)))
            ax.set_xticklabels(times, rotation=45)
            ax.grid(True)
            ax.legend()
            plt.tight_layout()
            plt.pause(0.01)

            # Console update
            print("-----------------------------------------------------")
            print(f"🌦️ {cname} | Iteration: {iteration}")
            print(f"Time: {entry['timestamp']}")
            print(f"Temperature: {temp:.1f}°C | Humidity: {entry['humidity']}% | Wind: {entry['windspeed']} km/h")
            print(f"Average so far: {avg_t:.2f}°C")
            print("-----------------------------------------------------\n")

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n🛑 Logging stopped by user.")
        plt.ioff()
        plt.show()
        show_summary_dashboard(cname)


# -------------------------------
# 🧠 Main Entry Point
# -------------------------------

def main():
    print("-----------------------------------------------------")
    print("📊 Real-Time Weather Tracker 4.2 | VS Code Dashboard")
    print("-----------------------------------------------------\n")

    city = input("🏙️ Enter city name: ").strip()
    live_weather_dashboard(city, interval_seconds=30)


if __name__ == "__main__":
    main()
