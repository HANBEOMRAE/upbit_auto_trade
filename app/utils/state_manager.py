import json
import os

# 현재 파일 위치 기준 절대 경로로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "../../state.json")

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ state.json 파일이 없습니다. 빈 상태로 시작합니다.")
        return {}
    except json.JSONDecodeError:
        print("❌ state.json 파싱 실패. JSON 구조 오류입니다.")
        return {}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"❌ 상태 저장 실패: {e}")
