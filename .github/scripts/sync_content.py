import json
import os
import sys

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_credentials():
    sa_key_raw = os.environ["GDRIVE_SA_KEY"]
    sa_info = json.loads(sa_key_raw)
    creds = service_account.Credentials.from_service_account_info(
        sa_info, scopes=SCOPES
    )
    creds.refresh(Request())
    return creds


def find_file_id(creds, folder_id, file_name):
    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    params = {
        "q": query,
        "fields": "files(id, name, modifiedTime)",
        "orderBy": "modifiedTime desc",
        "pageSize": 5,
    }
    resp = requests.get(
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {creds.token}"},
        params=params,
    )
    resp.raise_for_status()
    files = resp.json().get("files", [])
    if not files:
        print(f"Keine Datei '{file_name}' im Ordner {folder_id} gefunden.")
        sys.exit(1)
    if len(files) > 1:
        print(
            f"Warnung: {len(files)} Dateien mit Namen '{file_name}' gefunden, "
            f"nehme die zuletzt geänderte ({files[0]['id']})."
        )
    return files[0]["id"]


def download_file(creds, file_id):
    resp = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}",
        headers={"Authorization": f"Bearer {creds.token}"},
        params={"alt": "media"},
    )
    resp.raise_for_status()
    return resp.content


def main():
    folder_id = os.environ["DRIVE_FOLDER_ID"]
    file_name = os.environ["DRIVE_FILE_NAME"]

    creds = get_credentials()
    file_id = find_file_id(creds, folder_id, file_name)
    print(f"Gefundene Datei-ID: {file_id}")

    content = download_file(creds, file_id)

    # Validieren, dass es sich um gültiges JSON handelt, bevor überschrieben wird
    json.loads(content)

    with open("content.json", "wb") as f:
        f.write(content)

    print("content.json erfolgreich aktualisiert.")


if __name__ == "__main__":
    main()
