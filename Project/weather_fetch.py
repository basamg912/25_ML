#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weather_fetch.py
- 초단기예보(getUltraSrtFcst) 호출
- raw JSON → weather_raw_{base_date}{base_time}.json
- Pivot CSV → weather_{base_date}{base_time}.csv
- CSV 열 순서:
    예보일자, 예보시각,
    낙뢰 확률(%), 강수 형태, 습도(%),
    1시간 강수량(mm), 하늘 상태, 기온(℃),
    동서성분풍속(m/s), 풍향(°), 남북성분풍속(m/s), 풍속(m/s), 강수 확률(%)
- PTY, SKY, POP, LGT 값은 아래 맵핑에 따라 사람이 읽기 쉬운 텍스트로 변환
"""
import os
import math
import requests
import urllib.parse
import json
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────
load_dotenv()
raw_key = "rYR0W%2F%2BXsbw084PGloDk61B2UOE6Sdd0eK%2B5kZmuLNiy1KEtlFoGnMA%2B%2BBOlaHx%2BOrw%2BTfqgC5Ju8pHnyet5Cg%3D%3D"
if not raw_key:
    raise RuntimeError("환경변수 KMA_SERVICE_KEY가 설정되지 않았습니다.")
SERVICE_KEY = urllib.parse.unquote_plus(raw_key)
# ────────────────────────────────────────────────────────

# 컬럼명 매핑
CATEGORY_LABELS = {
    "LGT": "낙뢰 확률(%)",
    "PTY": "강수 형태",
    "REH": "습도(%)",
    "RN1": "1시간 강수량(mm)",
    "SKY": "하늘 상태",
    "T1H": "기온(℃)",
    "UUU": "동서성분풍속(m/s)",
    "VEC": "풍향(°)",
    "VVV": "남북성분풍속(m/s)",
    "WSD": "풍속(m/s)",
    "POP": "강수 확률(%)",
}

# 값 매핑
PTY_MAP = {
    "0": "없음", "1": "비", "2": "진눈깨비",
    "3": "눈", "5": "빗방울", "6": "빗방울·눈날림", "7": "눈날림"
}
SKY_MAP = {"1": "맑음", "3": "구름많음", "4": "흐림"}

def latlon_to_grid(lat_deg: float, lon_deg: float):
    """위경도 → 기상청 격자(nx, ny) 좌표 변환"""
    Re, grid = 6371.00877, 5.0
    slat1, slat2 = 30.0, 60.0
    olon, olat = 126.0, 38.0
    xo, yo = 210 / grid, 675 / grid
    PI, DEGRAD = math.pi, math.pi / 180.0

    slat1_rad, slat2_rad = slat1 * DEGRAD, slat2 * DEGRAD
    olon_rad, olat_rad = olon * DEGRAD, olat * DEGRAD

    re = Re / grid
    sn = math.log(math.cos(slat1_rad) / math.cos(slat2_rad)) / \
         math.log(math.tan(PI * 0.25 + slat2_rad * 0.5) /
                  math.tan(PI * 0.25 + slat1_rad * 0.5))
    sf = (math.tan(PI * 0.25 + slat1_rad * 0.5) ** sn) * math.cos(slat1_rad) / sn
    ro = re * sf / (math.tan(PI * 0.25 + olat_rad * 0.5) ** sn)

    lat_rad, lon_rad = lat_deg * DEGRAD, lon_deg * DEGRAD
    ra = re * sf / (math.tan(PI * 0.25 + lat_rad * 0.5) ** sn)
    theta = lon_rad - olon_rad
    if theta > PI:
        theta -= 2 * PI
    if theta < -PI:
        theta += 2 * PI
    theta *= sn

    x = ra * math.sin(theta) + xo
    y = ro - ra * math.cos(theta) + yo
    return int(x + 1.5), int(y + 1.5)

def fetch_weather(lat: float, lon: float):
    """
    초단기예보(getUltraSrtFcst) 호출 후
    raw items 리스트와 base_date, base_time 반환
    """
    nx, ny = latlon_to_grid(lat, lon)
    now = datetime.now()
    base_dt = now - timedelta(hours=1) if now.minute < 45 else now
    base_date = base_dt.strftime("%Y%m%d")
    base_time = base_dt.strftime("%H") + "00"

    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    params = {
        "serviceKey": SERVICE_KEY,
        "numOfRows":  500,
        "pageNo":     1,
        "dataType":   "JSON",
        "base_date":  base_date,
        "base_time":  base_time,
        "nx":         nx,
        "ny":         ny,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    body = resp.json().get("response", {}).get("body", {})
    return body.get("items", {}).get("item", []), base_date, base_time

def main():
    # 1) 위치 지정
    latitude, longitude = 37.61979324944898, 127.06088872868129

    # 2) 데이터 호출
    raw, base_date, base_time = fetch_weather(latitude, longitude)
    if not raw:
        print("데이터가 없습니다. base_time 등을 확인하세요.")
        exit()

    # 3) raw JSON 저장
    json_fname = f"weather_raw_{base_date}{base_time}.json"
    with open(json_fname, "w", encoding="utf-8") as jf:
        json.dump(raw, jf, ensure_ascii=False, indent=2)
    print(f" Raw JSON 저장: {json_fname}")

    # 4) 모든 category 수집
    all_cats = sorted({item["category"] for item in raw})

    # 5) Pivot 테이블 생성
    table = {}
    for it in raw:
        key = (it["fcstDate"], it["fcstTime"])
        if key not in table:
            # 초기화: 모든 코드 빈 문자열
            table[key] = {c: "" for c in all_cats}
        cat = it["category"]
        val = it["fcstValue"]
        # 값 매핑
        if cat == "PTY":
            val = PTY_MAP.get(val, val)
        elif cat == "SKY":
            val = SKY_MAP.get(val, val)
        # POP, LGT는 숫자 → % 붙여서 처리
        # 나중에 저장 단계에서 추가 처리します
        table[key][cat] = val

    # 6) 원하는 열 순서 정의
    desired_order = [
        "LGT", "PTY", "REH", "RN1", "SKY", "T1H",
        "UUU", "VEC", "VVV", "WSD", "POP"
    ]

    # 7) CSV 저장
    csv_fname = f"weather_{base_date}{base_time}.csv"
    with open(csv_fname, "w", newline="", encoding="utf-8-sig") as cf:
        writer = csv.writer(cf)
        # 헤더: 맵핑된 한글 이름
        header = ["예보일자", "예보시각"] + [
            CATEGORY_LABELS[c] for c in desired_order
        ]
        writer.writerow(header)
        for (date, time_) in sorted(table):
            row = [date, time_]
            for c in desired_order:
                v = table[(date, time_)].get(c, "")
                # POP, LGT에 % 붙이고 빈칸은 안내 문구
                if c in ("POP", "LGT"):
                    if v:
                        v = f"{v}%"
                    else:
                        v = "강수 확률 없음" if c == "POP" else "낙뢰 확률 없음"
                row.append(v)
            writer.writerow(row)
    print(f"Pivot CSV 저장: {csv_fname}")
    return csv_fname
if __name__ =='__main__':
    fname = main()
    print(fname)