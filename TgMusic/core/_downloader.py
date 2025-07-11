#  Copyright (c) 2025 AshokShau
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the TgMusicBot project. All rights reserved where applicable.

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from pytdbot import types
from ._config import config
from ._dataclass import PlatformTracks, TrackInfo


class MusicService(ABC):
    @abstractmethod
    def is_valid(self, url: str) -> bool: ...

    @abstractmethod
    async def get_info(self) -> Union[PlatformTracks, types.Error]: ...

    @abstractmethod
    async def search(self) -> Union[PlatformTracks, types.Error]: ...

    @abstractmethod
    async def get_track(self) -> Union[TrackInfo, types.Error]: ...

    @abstractmethod
    async def download_track(
        self, track_info: TrackInfo, video: bool = False
    ) -> Union[Path, types.Error]: ...


class DownloaderWrapper(MusicService):
    def __init__(self, query: Optional[str] = None) -> None:
        self.query = query
        self.service = self._get_service()

    def _get_service(self) -> MusicService:
        from ._youtube import YouTubeData
        from ._api import ApiData
        from ._jiosaavn import JiosaavnData

        services = [YouTubeData, JiosaavnData, ApiData]
        for service_cls in services:
            if service_cls().is_valid(self.query):
                return service_cls(self.query)

        fallback_map = {
            "youtube": YouTubeData,
            "spotify": ApiData,
            "jiosaavn": JiosaavnData,
        }
        fallback_cls = fallback_map.get(config.DEFAULT_SERVICE, YouTubeData)
        return (
            ApiData(self.query)
            if fallback_cls == ApiData and config.API_URL and config.API_KEY
            else fallback_cls(self.query)
        )

    def is_valid(self, url: str) -> bool:
        return self.service.is_valid(url)

    async def get_info(self) -> Union[PlatformTracks, types.Error]:
        return await self.service.get_info()

    async def search(self) -> Union[PlatformTracks, types.Error]:
        return await self.service.search()

    async def get_track(self) -> Union[TrackInfo, types.Error]:
        return await self.service.get_track()

    async def download_track(
        self, track_info: TrackInfo, video: bool = False
    ) -> Union[Path, types.Error]:
        return await self.service.download_track(track_info, video)
