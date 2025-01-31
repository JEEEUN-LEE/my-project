import os
import requests

# API 엔드포인트
url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"

service_key = "jYmQgKsPeM/KffLGjHFgvyTBGB/6ODgIGe2qZjXfsd6NG9d4jMtfl7gmx1MUZHpc65LVhAG3ChnTrqHlBr3AHQ=="
gu_code = "11215"  # 서울 광진구
base_date = "202401"  # 조회 연월 (YYYYMM)

# API 요청 파라미터
params = {
    "LAWD_CD": gu_code,
    "DEAL_YMD": base_date,
    "serviceKey": service_key  # Decoding된 인증키 사용
}

# API 호출
res = requests.get(url, params=params)

# 응답 코드 및 내용 확인
print(f"응답 코드: {res.status_code}")
print(res.text)

import pandas as pd
import xml.etree.ElementTree as ET

def get_items(response):
    root = ET.fromstring(response.content)
    item_list = []
    for child in root.find('body').find('items'):
        elements = child.findall('*')
        data = {}
        for element in elements:
            tag = element.tag.strip()
            text = element.text.strip()
            # print(tag, text)
            data[tag] = text
        item_list.append(data)  
    return item_list
    
items_list = get_items(res)
items = pd.DataFrame(items_list) 
items.head()

code_file = r"C:\my-project\my-project\아파트실거래가예측\법정동코드 전체자료.txt"
code = pd.read_csv(code_file, sep='\t', encoding='utf-8')

# 데이터 확인
print(code.head())

code.columns = ['code', 'name', 'is_exist']
code = code [code['is_exist'] == '존재']

print(code['code'][0])
print(type(code['code'][0])) ## int64타입

## string으로 변경
code['code'] = code['code'].apply(str) 

# 2015-2024년도까지의 데이터를 수집하기 위한 연월 리스트 생성
year = [str("%02d" %(y)) for y in range(2015, 2024)]
month = [str("%02d" %(m)) for m in range(1, 13)]
base_date_list = ["%s%s" %(y, m) for y in year for m in month ]

gu = "강남구"
gu_code = code[ (code['name'].str.contains(gu) )]
gu_code = gu_code['code'].reset_index(drop=True)
gu_code = str(gu_code[0])[0:5]
print(gu_code)

import datetime

def get_data(gu_code, base_date):
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    service_key = "jYmQgKsPeM/KffLGjHFgvyTBGB/6ODgIGe2qZjXfsd6NG9d4jMtfl7gmx1MUZHpc65LVhAG3ChnTrqHlBr3AHQ=="
    params = {
    "LAWD_CD": gu_code,
    "DEAL_YMD": base_date,
    "serviceKey": service_key  # Decoding된 인증키 사용
    }

    res = requests.get(url, params=params)
    return res
    
items_list = []
for base_date in base_date_list:
    res = get_data(gu_code, base_date)
    items_list += get_items(res)
    
len(items_list)

import pandas as pd
import os

# items_list의 길이 확인
print("Length of items_list:", len(items_list))

# items_list의 일부 내용 확인
print("First 5 items in items_list:", items_list[:5])

# 데이터프레임 생성
items = pd.DataFrame(items_list)
print("DataFrame shape:", items.shape)
print("First 5 rows of DataFrame:")
print(items.head())

# 저장할 경로와 파일 이름 지정
save_path = r"C:\my-project\my-project\아파트실거래가예측\api_data_collection"
file_name = "%s_%s~%s.csv" % (gu, year[0], year[-1])
full_path = os.path.join(save_path, file_name)

# 데이터프레임을 CSV 파일로 저장
items.to_csv(full_path, index=False, encoding="euc-kr")

# 저장된 파일의 내용 확인
saved_items = pd.read_csv(full_path, encoding="euc-kr")
print("Saved DataFrame shape:", saved_items.shape)
print("First 5 rows of saved DataFrame:")
print(saved_items.head())

