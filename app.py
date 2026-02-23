import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Grumpy Mari | Аллерго-радар", page_icon="😠", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
    .grumpy-header { font-size: 42px; font-weight: 800; color: #000; margin-bottom: 5px; }
    .grumpy-subtitle { font-size: 18px; color: #5C5C5C; margin-bottom: 30px; }
    .grumpy-card { background-color: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.2s; text-align: center; border: 1px solid #f0f0f0; margin-bottom: 20px; }
    .grumpy-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.12); }
    .emoji-icon { font-size: 50px; margin-bottom: 10px; }
    .grumpy-title { font-size: 20px; font-weight: 700; color: #000; margin: 0; }
    .grumpy-desc { font-size: 14px; color: #5C5C5C; margin: 8px 0 16px 0; min-height: 40px; }
    .grumpy-value { font-size: 28px; font-weight: 800; }
    .val-low { color: #00B36B; } 
    .val-med { color: #FF6900; } 
    .val-high { color: #E32636; } 
    .grumpy-btn { background-color: rgba(255, 105, 0, 0.1); color: #FF6900; border: none; border-radius: 9999px; padding: 12px 24px; font-weight: 700; font-size: 16px; width: 100%; display: inline-block; transition: 0.2s; }
    .grumpy-btn:hover { background-color: #FF6900; color: #fff; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="grumpy-header">😠 Grumpy Mari</div>', unsafe_allow_html=True)
st.markdown('<div class="grumpy-subtitle">Ваш личный радар аллергенов. Потому что чихать — это не круто. Скебоб.</div>', unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_pollen_data(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat, "longitude": lon,
        "current": ["alder_pollen", "birch_pollen", "grass_pollen", "mugwort_pollen", "olive_pollen", "ragweed_pollen"],
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

allergens = {
    "birch_pollen": {"name": "Береза", "emoji": "🍃", "desc": "Главный враг весны."},
    "grass_pollen": {"name": "Злаки", "emoji": "🌾", "desc": "Луговые травы и газоны."},
    "alder_pollen": {"name": "Ольха", "emoji": "🌳", "desc": "Цветет одной из первых."},
    "mugwort_pollen": {"name": "Полынь", "emoji": "🌱", "desc": "Опасна в конце лета."},
    "ragweed_pollen": {"name": "Амброзия", "emoji": "🍂", "desc": "Мощный осенний аллерген."},
    "olive_pollen": {"name": "Олива", "emoji": "🫒", "desc": "Для южных регионов."}
}

# Расширенная база городов для покрытия всей России
cities = {
    "Москва": (55.7512, 37.6184), "Санкт-Петербург": (59.9386, 30.3141),
    "Краснодар": (45.0448, 38.976), "Сочи": (43.5855, 39.7231),
    "Калининград": (54.7065, 20.511), "Казань": (55.7963, 49.1088),
    "Екатеринбург": (56.838, 60.5975), "Новосибирск": (55.0084, 82.9357),
    "Красноярск": (56.0153, 92.8932), "Владивосток": (43.1198, 131.8869)
}

# --- БЛОК 1: ДЕТАЛЬНАЯ СТАТИСТИКА ПО ГОРОДУ И ГЕОЛОКАЦИЯ ---
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("**🧭 Где вы находитесь?**")
    # Кнопка запроса геолокации из браузера
    geo = streamlit_geolocation()
    
    # Если кнопка нажата и координаты получены:
    if geo and geo.get('latitude') is not None:
        lat = geo['latitude']
        lon = geo['longitude']
        selected_city = "Ваша гео-позиция"
        st.success("Радар зафиксировал вас!")
    # Если кнопка не нажата, показываем стандартный список:
    else:
        selected_city = st.selectbox("📍 Выберите город из списка:", list(cities.keys()))
        lat, lon = cities[selected_city]

st.markdown("---")
data = fetch_pollen_data(lat, lon)

if data and "current" in data:
    current_data = data["current"]
    st.markdown(f"### 📊 Активность аллергенов: {selected_city}")
    cols = st.columns(3)
    
    for idx, (key, info) in enumerate(allergens.items()):
        # Защита от пустых данных (None)
        value = current_data.get(key)
        value = 0 if value is None else value
        
        if value < 10: css_class, status = "val-low", "Чисто"
        elif value < 50: css_class, status = "val-med", "Терпимо"
        else: css_class, status = "val-high", "Опасно!"
            
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="grumpy-card">
                <div class="emoji-icon">{info['emoji']}</div>
                <h3 class="grumpy-title">{info['name']}</h3>
                <p class="grumpy-desc">{info['desc']}</p>
                <div class="grumpy-value {css_class}">{value} <span style="font-size: 14px; color: #aaa;">зерен/м³</span></div>
                <div style="margin-top: 15px;"><div class="grumpy-btn">{status}</div></div>
            </div>
            """, unsafe_allow_html=True)

# --- БЛОК 2: ГЛОБАЛЬНАЯ КАРТА (ВСЯ РОССИЯ) ---
st.markdown("---")
st.markdown("### 🗺 Национальный радар")
st.caption("Мари сканирует крупные хабы по всей стране. Вы можете двигать и приближать карту.")

m = folium.Map(location=[60.0, 90.0], zoom_start=3, tiles="CartoDB positron")

with st.spinner('Спутник собирает данные по регионам РФ...'):
    for city_name, coords in cities.items():
        city_lat, city_lon = coords
        city_data = fetch_pollen_data(city_lat, city_lon)
        
        if city_data and "current" in city_data:
            c_data = city_data["current"]
            
            max_val = 0
            worst_alg = "Чисто"
            for k, info in allergens.items():
                # Защита от пустых данных (None) для карты
                val = c_data.get(k)
                val = 0 if val is None else val
                
                if val >= max_val:
                    max_val = val
                    worst_alg = info['name']
            
            if max_val < 10: zone_color = "#00B36B" # Зеленый
            elif max_val < 50: zone_color = "#FF6900" # Оранжевый
            else: zone_color = "#E32636" # Красный
            
            folium.Circle(
                location=[city_lat, city_lon],
                radius=150000, 
                color=zone_color,
                fill=True,
                fill_color=zone_color,
                fill_opacity=0.4,
                tooltip=f"<b>{city_name}</b><br>Худший фон: {worst_alg} ({max_val} зерен/м³)"
            ).add_to(m)

st_folium(m, use_container_width=True, height=500, returned_objects=[])

