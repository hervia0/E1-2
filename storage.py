"""state.json 파일 읽기/쓰기를 담당하는 StateStorage 클래스."""

import json
import os
from pathlib import Path

# 프로젝트 루트(이 파일이 있는 폴더)의 state.json
DEFAULT_STATE_FILE = Path(__file__).resolve().parent / "state.json"


class StateLoadError(Exception):
    """state.json이 손상되었거나 읽을 수 없을 때 발생한다."""


class StateSaveError(Exception):
    """state.json에 저장하지 못했을 때 발생한다."""


class StateStorage:
    """JSON 파일과 파이썬 딕셔너리 사이의 변환만 담당한다. (게임 규칙은 모른다)"""

    def __init__(self, path=DEFAULT_STATE_FILE):
        self.path = Path(path)

    def load(self):
        """파일 내용을 딕셔너리로 반환한다. 파일이 없으면 None을 반환한다."""
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError as error:
            raise StateLoadError(
                f"JSON 형식이 올바르지 않습니다. ({error.lineno}행 {error.colno}열)"
            ) from error
        except UnicodeDecodeError as error:
            raise StateLoadError("UTF-8로 읽을 수 없는 파일입니다.") from error
        except OSError as error:
            raise StateLoadError(f"파일을 읽을 수 없습니다. ({error})") from error

    def save(self, data):
        """임시 파일에 먼저 쓴 뒤 교체하여, 저장 도중 문제가 생겨도 기존 파일을 지킨다."""
        temp_path = self.path.with_name(self.path.name + ".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.path)
        except (OSError, TypeError, ValueError) as error:
            raise StateSaveError(str(error)) from error

    def backup_corrupted(self):
        """손상된 파일을 state.json.bak으로 옮기고 백업 경로를 반환한다. 실패하면 None."""
        backup_path = self.path.with_name(self.path.name + ".bak")
        try:
            os.replace(self.path, backup_path)
        except OSError:
            return None
        return backup_path
