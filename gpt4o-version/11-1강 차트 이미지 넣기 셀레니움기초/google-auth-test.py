from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

# 클라이언트 시크릿 파일 경로와 요청할 권한 범위 설정
CLIENT_SECRETS_FILE = r"C:\Users\sminpark\Downloads\client_secret_929030140737-lmcn34f4krhe9a5rokco9fu95k1uq7l9.apps.googleusercontent.com.json"  # Google Cloud Console에서 받은 JSON 파일
SCOPES = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]

# 토큰 파일이 존재하면 로드하고, 존재하지 않으면 새로 발급
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

    # 발급된 토큰을 저장해두면 이후 재인증 필요 없음
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

print("인증이 성공적으로 완료되었습니다. 액세스 토큰:", creds.token)
