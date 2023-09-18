import hashlib
from google.cloud import secretmanager

# create secret manager client
client = secretmanager.SecretManagerServiceClient()

def get(secret_id, version_id="latest"):
    # build resoutce name of the secret version
    name = f"projects/gym-bot-390016/secrets/{secret_id}/versions/{version_id}"
    # access secret version
    response = client.access_secret_version(name=name)
    # return decoded payload
    return response.payload.data.decode("UTF-8")

line_channel_secret = get("LINE_CHANNEL_SECRET")
line_channel_access_token = get("LINE_CHANNEL_ACCESS_TOKEN")
