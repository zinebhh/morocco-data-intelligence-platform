from data_engineering.common.minio_client import MinIOClient


def test_minio_connection():

    client = MinIOClient()

    assert client.client.bucket_exists(
        client.raw_bucket
    )

    assert client.client.bucket_exists(
        client.processed_bucket
    )

    assert client.client.bucket_exists(
        client.errors_bucket
    )