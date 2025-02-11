from abc import ABC, abstractmethod
from typing import Any, Dict
import time

from project.utils.file_system import write_json


class BaseCrawler(ABC):
    def __init__(self) -> None:
        super().__init__()

        self._save_dir: str
        self._url: str

    def get(self, save: bool = False):
        content = self._get()

        if save:
            path = self._save_dir + "/" + str(int(time.time())) + ".json"
            write_json(path, content)

        return content

    @abstractmethod
    def _build_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    def __str__(self) -> str:
        return f"{type(self).__name__} \n url: {self._url} \n save dir {self._save_dir}"
