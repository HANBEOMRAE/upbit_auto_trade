# app/services/config.py

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")

# 유효성 체크 (선택)
if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
    raise ValueError("Upbit API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")