import requests
import base64
from requests.exceptions import ConnectionError, HTTPError, Timeout, RequestException
import streamlit as st

# Настройка страницы
st.set_page_config(
    page_title="Weather App",
    page_icon="🛰️",
    layout='wide'
)

# CSS
st.markdown("""
    <style>
    /* Ограничение ширины всего контента */
    .block-container {
        max-width: 1100px !important;
    }
    /* Карточки метрик */
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.3) !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        background-color: rgba(128, 128, 128, 0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Словарь языков для API 
LANGUAGES = {
    "Русский": "ru",
    "English": "en",
    "Deutsch": "de"
}

# Словарь фраз для интерфейса
TEXTS = {
    "ru": {
        "title": "🛰️ Прогноз погоды",
        "enter_city": "Введите название города ниже:",
        "weather_in": "Погода в городе",
        "city_hint": "💡 Указывайте город с регионом или страной (например: «Уфа, Башкортостан»), иначе сервис может выдать одноименный город из другой страны.",
        "desc": "Состояние",
        "wind": "Ветер",
        "humidity": "Влажность",
        "visibility": "Видимость",
        "temp": "Температура",
        "feel": "Ощущается как",
        "rain_chance": "Вероятность дождя",
        "sun_cycle": "Рассвет / Закат",
        "err_city": "Введите корректное название города",
        "err_img": "Не удалось загрузить изображение погоды",
        "show_img": "Показать графический прогноз",
        "kmh": "км/ч",
        "km": "км"
    },
    "en": {
        "title": "🛰️ Weather Forecast",
        "enter_city": "Enter city name below:",
        "city_hint": "💡 Specify the city with region or country (e.g. 'Ufa, Bashkortostan'), otherwise the service might pick another location with the same name.",
        "weather_in": "Weather in",
        "desc": "Condition",
        "wind": "Wind",
        "humidity": "Humidity",
        "visibility": "Visibility",
        "temp": "Temperature",
        "feel": "Feels like",
        "rain_chance": "Rain chance",
        "sun_cycle": "Sunrise / Sunset",
        "err_city": "Please enter a valid city name",
        "err_img": "Failed to load weather image",
        "show_img": "Show visual forecast image",
        "kmh": "km/h",
        "km": "km"
    },
    "de": {
        "title": "🛰️ Wettervorhersage",
        "enter_city": "Geben Sie unten den Stadtnamen ein:",
        "city_hint": "💡 Geben Sie die Stadt mit Region oder Land an (z. B. „Ufa, Baschkortostan“), da sonst ein anderer Ort gewählt werden kann.",
        "weather_in": "Wetter in",
        "desc": "Zustand",
        "wind": "Wind",
        "humidity": "Luftfeuchtigkeit",
        "visibility": "Sichtweite",
        "temp": "Temperatur",
        "feel": "Gefühlt",
        "rain_chance": "Regenwahrscheinlichkeit",
        "sun_cycle": "Sonnenaufgang / -untergang",
        "err_city": "Bitte geben Sie einen gültigen Stadtnamen ein",
        "err_img": "Wetterbild konnte nicht geladen werden",
        "show_img": "Grafische Vorhersage anzeigen",
        "kmh": "km/h",
        "km": "km"
    }
}

# --Кэшируемые функции--
@st.cache_data(ttl=900) # запрос остаётся в кэше 900 секунд (15 минут)
def get_weather(location: str="Уфа, Башкортостан", lang: str="ru") -> None:
    """"
    Функция получает данные из указанного города (по умолчанию: Уфа)
    :param location: Название города
    :param lang: Язык вывода
    """
    
    url = f"https://wttr.in/{location}?lang={lang}&format=j1"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
    }

    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status() 
    return response.json()

@st.cache_data(ttl=900)
def get_weather_image(location: str, lang: str) -> bytes:      
    """Отдельная функция для загрузки PNG-картинки с погодой"""
    encoded_location = location.replace(" ", "+")
    url = f"https://wttr.in/{encoded_location}.png?m&lang={lang}"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    if not response.headers.get("Content-Type", "").startswith("image"):
        raise ValueError("Сервер не вернул картинку")

    return response.content

# --Интерфейс--
selected_lang = st.sidebar.selectbox("Язык / Language", list(LANGUAGES.keys()))
lang_code = LANGUAGES[selected_lang]
t=TEXTS.get(lang_code)

st.title(t['title'])
st.markdown(f"### {t['enter_city']}")
location = st.text_input("", value="Уфа, Башкортостан")
st.caption(t["city_hint"]) # Вывод понятной подсказки под полем ввода
  
if location:
    try:
        data = get_weather(location=location, lang=lang_code)
        current = data["current_condition"][0]

        lang_key = f"lang_{lang_code}"
        chance_of_rain = data["weather"][0]["hourly"][0]["chanceofrain"]
        sunrise = data["weather"][0]["astronomy"][0]["sunrise"]
        sunset = data["weather"][0]["astronomy"][0]["sunset"]
        feels_like = current["FeelsLikeC"]
        wind_speed = current["windspeedKmph"]
        humidity = current["humidity"]
        visibility = current['visibility']
        temperature = current['temp_C']
        
        if lang_key in current:
            # краткое описание погоды
            description = current[lang_key][0]["value"] 
        else:
            description = current["weatherDesc"][0]["value"]

        # Основной вывод
        st.markdown(f"## {t['weather_in']} **{location.title()}**")
        st.info(f"**{t['desc']}:** {description}")

        # Блок 1: Температура
        col1, col2 = st.columns(2)
        col1.metric(label=t["temp"], value=f"{temperature} °C")
        col2.metric(label=t["feel"], value=f"{feels_like} °C")

        st.markdown("---")

        # Блок 2: Осадки, Влажность и Ветер
        col3, col4, col5 = st.columns(3)
        col3.metric(label=t["rain_chance"], value=f"{chance_of_rain}%")
        col4.metric(label=t["humidity"], value=f"{humidity}%")
        col5.metric(label=t["wind"], value=f"{wind_speed} {t['kmh']}")

        st.markdown("---")

        # Блок 3: Рассвет/Закат 
        col6, col7 = st.columns(2)
        col6.metric(label=t["sun_cycle"], value=f"{sunrise} / {sunset}")
        col7.metric(label=t["visibility"], value=f"{visibility} {t['km']}")

        st.markdown("---")

        if st.checkbox(t["show_img"]):
            try:
                img_bytes = get_weather_image(location=location, lang=lang_code)
                img_b64 = base64.b64encode(img_bytes).decode()
                st.markdown(
                    f'<img src="data:image/png;base64,{img_b64}" style="width:100%">',
                    unsafe_allow_html=True,
                )
                st.caption(f"{t['weather_in']} {location.title()}")

            except Exception as e:
                st.error(f"[x] {t['err_img']}: {e}")

    except (ConnectionError, Timeout):
        st.error("[X] Ошибка сети или превышено время ожидания.")
    except (HTTPError, RequestException, KeyError):
        st.error(f"[X] {t['err_city']}")
