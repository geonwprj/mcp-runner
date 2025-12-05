import tts_mcp.config as config
import tts_mcp.clients as clients

def main():
    try:
        minio_client = clients.MinioClient(
            endpoint=config.MINIO_ENDPOINT,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            secure=config.MINIO_SECURE,
            bucket=config.MINIO_BUCKET,
            logger=config.logger
        )
        if minio_client.exists_bucket():
            minio_client.delete_bucket(force=True)
        minio_client.create_bucket(expiration=config.MINIO_BUCKET_EXPIRATION, anonymous=config.MINIO_BUCKET_ANONYMOUS)
    except Exception as e:
        config.logger.error(f"Failed to initialize MinIO bucket: {str(e)}")
        raise

if __name__ == "__main__":
    main()
    