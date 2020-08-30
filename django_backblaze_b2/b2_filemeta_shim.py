from typing import Dict

from b2sdk.v1 import B2Api, Bucket


class FileMetaShim:
    """
    Shim until you can get file info by name:
    https://github.com/Backblaze/b2-sdk-python/issues/143

    Internally, does a HEAD on the file's url.
    Caches the result in-memory for the lifetime of this object's existence
    """

    def __init__(self, b2Api: B2Api, bucketInstance: Bucket, filename: str) -> None:
        self._b2Api = b2Api
        self._bucket = bucketInstance
        self._filename = filename

    @property
    def id(self) -> str:
        return self.as_dict()["x-bz-file-id"]

    @property
    def contentLength(self) -> int:
        return self.as_dict()["Content-Length"]

    def as_dict(self) -> Dict:
        if not hasattr(self, "_meta"):
            downloadUrl = self._b2Api.session.get_download_url_by_name(
                self._bucket.name, self._filename
            )
            downloadAuthorization = self._bucket.get_download_authorization(
                self._filename, 30
            )
            response = self._b2Api.raw_api.b2_http.session.head(
                downloadUrl, headers={"Authorization": downloadAuthorization}
            )
            response.raise_for_status()
            self._meta = response.headers
        return self._meta
