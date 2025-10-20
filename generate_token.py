#!/usr/bin/env python3
"""
生成有效的 JWT Token 用於 NeuroAgent Demo
執行: python generate_token.py
"""

import jwt
import datetime

# 使用專案的 JWT 密鑰（來自 backend/utils/auth.py）
JWT_SECRET_KEY = "REDACTED"
JWT_ALGORITHM = "HS256"

def generate_demo_token():
    """生成 Demo 用的 JWT token (24小時有效期)"""

    now = datetime.datetime.utcnow()

    payload = {
        "user_id": "demo-physician",
        "username": "demo",
        "iat": now,  # 發行時間
        "exp": now + datetime.timedelta(hours=24),  # 24小時後過期
        "type": "access"  # Token 類型
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token

if __name__ == "__main__":
    token = generate_demo_token()
    print("=" * 80)
    print("✅ NeuroAgent Demo JWT Token (24小時有效)")
    print("=" * 80)
    print(f"\n{token}\n")
    print("=" * 80)
    print("\n使用方式:")
    print("1. 複製上面的 token")
    print("2. 更新 frontend/src/services/api.js 第 23 行")
    print("3. 或者在 Vercel 環境變數設定 REACT_APP_JWT_TOKEN")
    print("\n" + "=" * 80)

    # 驗證 token
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        print("\n✅ Token 驗證成功！")
        print(f"用戶 ID: {decoded['user_id']}")
        print(f"過期時間: {datetime.datetime.fromtimestamp(decoded['exp'])}")
    except Exception as e:
        print(f"\n❌ Token 驗證失敗: {e}")
