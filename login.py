import os

from uptime_kuma_api import UptimeKumaApi

if uptime_kuma_url := os.environ.get("UPTIME_KUMA_URL", ""):
    with UptimeKumaApi(uptime_kuma_url) as api:
        username = input("Username: ")
        password = input("Password: ")
        otp_code = input("OTP code: ")
        try:
            login = api.login(username, password, otp_code)
        except Exception as e:
            print(f"Login failed: {e}")
            exit(1)
        jwt = login.get("token", None)
        print("Your JWT is:")
        print(jwt)
else:
    print("UPTIME_KUMA_URL environment variable not set")
    exit(1)
