import os
import zipfile
import requests
import sys

# 解決 Windows 終端機 Emoji 輸出問題
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def zip_frontend(frontend_dir, zip_path):
    print(f"📦 正在打包前端資料夾...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(frontend_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, frontend_dir)
                zipf.write(file_path, arcname)

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip()
    return env_vars

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    frontend_dir = os.path.join(base_dir, 'frontend')
    zip_path = os.path.join(base_dir, 'frontend.zip')
    
    env_vars = load_env()
    site_id = env_vars.get('NETLIFY_SITE_ID')
    token = env_vars.get('NETLIFY_TOKEN')
    
    if not site_id or not token:
        print("❌ 【設定錯誤】找不到 .env 檔案或資料不完整！")
        print("請在 backend 資料夾內建立一個 .env 檔案，並填入以下內容：")
        print("NETLIFY_SITE_ID=填入您的 Site ID")
        print("NETLIFY_TOKEN=填入您的 Token")
        sys.exit(1)
        
    zip_frontend(frontend_dir, zip_path)
    
    print("☁️ 正在連線至 Netlify 伺服器...")
    url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/zip'
    }
    
    try:
        with open(zip_path, 'rb') as f:
            res = requests.post(url, headers=headers, data=f)
            
        if res.status_code in [200, 201]:
            data = res.json()
            # Netlify 有時會提供 url 或 deploy_ssl_url
            deploy_url = data.get('deploy_ssl_url') or data.get('url') or data.get('ssl_url')
            print("\n=========================================")
            print("🚀 自動化部署大成功！")
            print(f"👉 您的雲端儀表板網址：{deploy_url}")
            print("=========================================\n")
            print("現在您可以關掉電腦，用手機隨時查看這個網址了！")
        else:
            print("\n❌ 【上傳失敗】請檢查您的 Site ID 與 Token 是否正確。")
            print(f"伺服器回傳代碼: {res.status_code}")
            print(f"錯誤訊息: {res.text}")
    except Exception as e:
        print(f"\n❌ 【連線異常】發生例外狀況：{e}")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == "__main__":
    main()
