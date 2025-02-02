import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET

API_URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
SERVICE_KEY = "jYmQgKsPeM/KffLGjHFgvyTBGB/6ODgIGe2qZjXfsd6NG9d4jMtfl7gmx1MUZHpc65LVhAG3ChnTrqHlBr3AHQ=="

# 법정동 코드 로드
code_file = r"C:\my-project\my-project\아파트실거래가예측\법정동코드 전체자료.txt"
code_df = pd.read_csv(code_file, sep='\t', encoding='utf-8', names=['code', 'name', 'is_exist'])
code_df = code_df[code_df['is_exist'] == '존재']
code_df['code'] = code_df['code'].astype(str)  # 코드 문자열 변환

# 데이터 요청 함수
def get_data(gu_code, base_date):
    params = {"LAWD_CD": gu_code, "DEAL_YMD": base_date, "serviceKey": SERVICE_KEY}
    res = requests.get(API_URL, params=params)
    if res.status_code != 200:
        print(f"API 요청 실패: {res.status_code}")
        return None
    return res

# XML 파싱 함수
def get_items(response):
    if response is None:
        return []
    
    root = ET.fromstring(response.content)
    items = []
    
    for item in root.find('body').find('items'):
        data = {elem.tag.strip(): elem.text.strip() for elem in item.findall('*')}
        items.append(data)
    
    return items

# 특정 구 코드 가져오기
def get_gu_code(gu_name):
    gu_code = code_df[code_df['name'].str.contains(gu_name)]['code'].reset_index(drop=True)
    return str(gu_code[0])[:5] if not gu_code.empty else None

# 저장 경로 설정
SAVE_PATH = r"C:\my-project\my-project\아파트실거래가예측\api_data_collection"

# 연월 리스트 생성 (2015~2023)
years = [f"{y:04d}" for y in range(2015, 2024)]
months = [f"{m:02d}" for m in range(1, 13)]
base_date_list = [f"{y}{m}" for y in years for m in months]

# 데이터 수집 및 저장
def collect_and_save(gu_name):
    gu_code = get_gu_code(gu_name)
    if not gu_code:
        print(f"{gu_name} 코드 없음")
        return
    
    all_items = []
    
    for base_date in base_date_list:
        res = get_data(gu_code, base_date)
        all_items.extend(get_items(res))
    
    if all_items:
        df = pd.DataFrame(all_items)
        file_name = f"{gu_name}_{years[0]}~{years[-1]}.csv"
        full_path = os.path.join(SAVE_PATH, file_name)
        df.to_csv(full_path, index=False, encoding="euc-kr")
        print(f"저장 완료: {full_path}")

# 원하는 구 데이터 수집 및 저장
collect_and_save("서대문구")
