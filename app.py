import streamlit as st
import ephem
import datetime
import pytz
import numpy as np
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
from matplotlib import pyplot as plt

# 도시 목록과 좌표 (한국 및 일본 도시 포함)
cities = {
    "서울": (37.5665, 126.9780),
    "부산": (35.1796, 129.0756),
    "제주": (33.4996, 126.5312),
    "도쿄": (35.6762, 139.6503),
    "오사카": (34.6937, 135.5023),
    "후쿠오카": (33.5902, 130.4017),
    "삿포로": (43.0618, 141.3545)
}

def get_visible_stars(lat, lon, date):
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)

    location = wgs84.latlon(lat, lon)
    ts = load.timescale()
    t = ts.from_datetime(date)
    
    visible_stars = []
    for _, star in stars.iterrows():
        if star['magnitude'] <= 4:
            s = Star.from_dataframe(star)
            alt, az, _ = location.at(t).observe(s).apparent().altaz()
            if alt.degrees > 0:
                visible_stars.append((az.degrees, alt.degrees, star['magnitude']))
    
    return visible_stars

def plot_sky(stars):
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(90, 0)
    
    for az, alt, mag in stars:
        size = max(20 * (5 - mag), 1)
        ax.scatter(np.radians(az), 90-alt, s=size, color='white', alpha=0.7)
    
    ax.set_facecolor('black')
    plt.title("밤하늘 별자리")
    return fig

# Streamlit 앱
st.title("도시별 밤하늘 별자리 뷰어")

# 도시 선택
selected_city = st.selectbox("도시를 선택하세요", list(cities.keys()))

if selected_city:
    lat, lon = cities[selected_city]
    date = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))  # 일본 시간대로 변경
    
    stars = get_visible_stars(lat, lon, date)
    fig = plot_sky(stars)
    
    st.write(f"{selected_city}의 {date.strftime('%Y-%m-%d %H:%M')} 기준 밤하늘입니다.")
    st.pyplot(fig)
