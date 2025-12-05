# tools/tts.py

from tts_mcp.clients import MinioClient, MacSSHClient
import tts_mcp.config as config
import hashlib
import os
import tempfile

minio_client = None
mac_ssh_client = None

try:
    minio_client = MinioClient(
        endpoint=config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=config.MINIO_SECURE,
        bucket=config.MINIO_BUCKET,
        logger=config.logger
    )
    minio_client.create_bucket(anonymous=True)
except Exception as e:
    config.logger.error("Failed to initialize Minio client: %s", e)

try:
    mac_ssh_client = MacSSHClient(
        host=config.MAC_HOST,
        user=config.MAC_USER,
        password=config.MAC_PASSWORD,
        key_filename=config.MAC_SSH_FILE,
        port=config.MAC_PORT,
        working_path=config.MAC_WORKING_PATH,
        logger=config.logger
    )
except Exception as e:
    config.logger.error("Failed to initialize Mac SSH client: %s", e)



def _generate_hash(text: str) -> str:
    try:
        return hashlib.md5(text.encode()).hexdigest()
    except Exception as e:
        config.logger.error("Failed to generate hash: %s", e)
        raise e

def _generate_audio(text: str) -> (str, str):
    if not minio_client:
        raise RuntimeError("MinIO client is not initialized. Check server logs for startup errors.")
    if not mac_ssh_client:
        raise RuntimeError("Mac SSH client is not initialized. Check server logs for startup errors.")
    try:
        hash = _generate_hash(text)
        
        # Create temp file for text
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode='w') as tmp_text:
            tmp_text.write(text)
            local_text = tmp_text.name
        config.logger.info("Text saved to temp file: %s", local_text)

        # Create temp file path for audio (we don't create the file yet, just the path)
        # We can use the hash for the audio filename to keep it consistent or use another temp file
        # Let's use a temp directory for the audio file to ensure cleanup
        local_audio = os.path.join(tempfile.gettempdir(), f"{hash}.aiff")

        mac_audio = f"{config.MAC_WORKING_PATH}/{hash}.aiff"
        mac_text = f"{config.MAC_WORKING_PATH}/{hash}.txt"
        minio_audio = f"{config.MINIO_WORKING_PATH}/{hash}.aiff"
        minio_audio = minio_audio[1:] if minio_audio.startswith("/") else minio_audio
        minio_url = f"{config.MINIO_PUBLIC_URL}/{config.MINIO_BUCKET}/{minio_audio}"

        mac_ssh_client.upload_file(local_text, mac_text)
        mac_ssh_client.run_command(f"say -f {mac_text} -o {mac_audio}")
        mac_ssh_client.download_file(mac_audio, local_audio)
        minio_client.upload_file(local_audio, minio_audio)
    except Exception as e:
        config.logger.error("Failed to generate audio: %s", e)
        raise e
    finally:
        if 'local_text' in locals() and os.path.exists(local_text):
            os.remove(local_text)
        if 'local_audio' in locals() and os.path.exists(local_audio):
            os.remove(local_audio)
        if mac_ssh_client.exists_file(mac_text):
            mac_ssh_client.delete_file(mac_text)
        if mac_ssh_client.exists_file(mac_audio):
            mac_ssh_client.delete_file(mac_audio)
    return hash, minio_url

def say(text: str) -> str:
    try:
        _, minio_url = _generate_audio(text)
        config.logger.info("Audio generated: %s", minio_url)
        return minio_url
    except Exception as e:
        config.logger.error("Failed to say: %s", e)
        raise e

def tts(url: str) -> str:
    if not minio_client:
        raise RuntimeError("MinIO client is not initialized. Check server logs for startup errors.")
    try:
        minio_text = url.replace(config.MINIO_PUBLIC_URL, "")
        bucket = minio_text.split("/")[0]
        minio_text = minio_text.replace(bucket, "")
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_text:
            local_text = tmp_text.name
        
        minio_client.download_file(minio_text, local_text, bucket=bucket)
        config.logger.info("Text downloaded to temp file: %s", local_text)

        with open(local_text, "r") as f:
            text = f.read()
        config.logger.info("Text loaded: %s", text)

        _, minio_url = _generate_audio(text)
        config.logger.info("Audio generated: %s", minio_url)
        return minio_url
    except Exception as e:
        config.logger.error("Failed to tts: %s", e)
        raise e
    finally:
        if 'local_text' in locals() and os.path.exists(local_text):
            os.remove(local_text)
