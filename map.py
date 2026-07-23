import json
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("⚡ 전국 전기차 충전소 위치 안내 (카카오맵)")

# 1. API 키 설정
KAKAO_JAVASCRIPT_KEY = "f91c6ad3fd39894c281bea8e20aff238"
SERVICE_KEY = "d3cd66a9fddbec17026376f1335381c3a7391a48b4caabeeefe2554d4b873727"

url = "http://apis.data.go.kr/B552584/EvCharger/getChargerInfo"


# 2. 전국 데이터 전체 로딩 함수 (페이지네이션 반복 수집)
@st.cache_data(ttl=3600)  # 전국 데이터는량이 많으므로 1시간 캐싱
def fetch_all_korea_ev_chargers(max_pages=5):  # default로 5페이지(최대 5만건)까지 예시 제한
    all_stations = []
    seen = set()

    page_no = 1
    num_of_rows = 9999  # 최대 9,999건씩 요청

    progress_bar = st.progress(0)
    status_text = st.empty()

    while page_no <= max_pages:
        status_text.text(f"전국 충전소 데이터 수집 중... ({page_no} 페이지 요청)")

        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "dataType": "JSON",
            "zcode": 11 # zcode를 생략하여 전국 데이터를 조회합니다.
        }

        try:
            response = requests.get(url, params=params, timeout=20)
            data = response.json()

            # 전체 개수 확인
            total_count = int(data.get("totalCount", 0))

            items = data.get("items", {}).get("item", [])
            if not items:
                items = (
                    data.get("response", {})
                    .get("body", {})
                    .get("items", {})
                    .get("item", [])
                )

            if not items:
                break  # 더 이상 가져올 데이터가 없으면 중단

            for item in items:
                name = item.get("statNm", "")
                lat = item.get("lat", "")
                lng = item.get("lng", "")
                addr = item.get("addr", "")
                use_time = item.get("useTime", "")
                output = item.get("output", "")

                if lat and lng:
                    key = (name, lat, lng)
                    if key not in seen:
                        seen.add(key)
                        all_stations.append(
                            {
                                "title": name,
                                "lat": float(lat),
                                "lng": float(lng),
                                "addr": addr,
                                "useTime": use_time,
                                "output": (
                                    f"{output}kW" if output else "정보없음"
                                ),
                            }
                        )

            # 수집 진행도 업데이트
            fetched_so_far = page_no * num_of_rows
            if total_count > 0:
                progress = min(1.0, fetched_so_far / total_count)
                progress_bar.progress(progress)

            if fetched_so_far >= total_count:
                break

            page_no += 1

        except Exception as e:
            st.error(f"데이터 조회 중 오류 발생: {e}")
            break

    status_text.text(f"수집 완료! 총 {len(all_stations):,}개의 충전소 위치")
    progress_bar.empty()
    return all_stations


# 데이터 수집 실행 (속도를 위해 일단 예시로 3개 페이지 = 약 3만건 수집 설정)
stations = fetch_all_korea_ev_chargers(max_pages=3)
stations_json = json.dumps(stations, ensure_ascii=False)

# 3. 카카오 맵 클러스터러 시각화
kakao_map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        html, body {{ width: 100%; height: 100%; margin: 0; padding: 0; }}
        #map {{ width: 100%; height: 100vh; }}
        .info-title {{ font-weight: bold; font-size: 14px; margin-bottom: 5px; color: #1a73e8; }}
        .info-body {{ font-size: 12px; color: #555; line-height: 1.4; }}
    </style>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JAVASCRIPT_KEY}&libraries=clusterer&autoload=false"></script>
</head>
<body>
    <div id="map"></div>
    <script>
        var positions = {stations_json};

        kakao.maps.load(function() {{
            var container = document.getElementById('map');
            var options = {{
                center: new kakao.maps.LatLng(36.5, 127.5), // 대한민국 중앙 부근
                level: 12
            }};

            var map = new kakao.maps.Map(container, options);
            var currentInfoWindow = null;

            // 수만 개의 마커를 안정적으로 렌더링하기 위한 MarkerClusterer
            var clusterer = new kakao.maps.MarkerClusterer({{
                map: map,
                averageCenter: true,
                minLevel: 7
            }});

            var markers = positions.map(function(pos) {{
                var loc = new kakao.maps.LatLng(pos.lat, pos.lng);
                var marker = new kakao.maps.Marker({{ position: loc }});

                var content = `
                    <div style="padding:10px; width:230px;">
                        <div class="info-title">⚡ ${{pos.title}}</div>
                        <div class="info-body">
                            <b>주소:</b> ${{pos.addr}}<br>
                            <b>이용시간:</b> ${{pos.useTime}}<br>
                            <b>충전용량:</b> ${{pos.output}}
                        </div>
                    </div>
                `;

                var infowindow = new kakao.maps.InfoWindow({{
                    content: content,
                    removable: true
                }});

                kakao.maps.event.addListener(marker, 'click', function() {{
                    if (currentInfoWindow) {{
                        currentInfoWindow.close();
                    }}
                    infowindow.open(map, marker);
                    currentInfoWindow = infowindow;
                }});

                return marker;
            }});

            clusterer.addMarkers(markers);
        }});
    </script>
</body>
</html>
"""

components.html(kakao_map_html, height=700)