import json
import os
import sys

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    sa_key_raw = os.environ.get("GDRIVE_SA_KEY")
    file_id = os.environ.get("DRIVE_FILE_ID")

    if not sa_key_raw or not file_id:
        print("GDRIVE_SA_KEY oder DRIVE_FILE_ID fehlt.", file=sys.stderr)
        sys.exit(1)

    sa_info = json.loads(sa_key_raw)
    credentials = service_account.Credentials.from_service_account_info(
        sa_info, scopes=SCOPES
    )
    credentials.refresh(Request())

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    resp = requests.get(
        url,
        params={"alt": "media"},
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=30,
    )
    resp.raise_for_status()

    # Validieren, dass es sich um gültiges JSON handelt, bevor wir committen
    data = resp.json()

    with open("content.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("content.json erfolgreich synchronisiert.")


if __name__ == "__main__":
    main()
