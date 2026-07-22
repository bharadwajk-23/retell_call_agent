"""Read-only access to provider availability reference data (JSON on disk)."""

from typing import Any, Dict, List

from backend.app.core import provider_details_path
from backend.app.utils import load_json_file


class ProviderRepository:
    def list_all(self) -> List[Dict[str, Any]]:
        data = load_json_file(provider_details_path())
        return data if isinstance(data, list) else []

    def get_by_name(self, provider_name: str) -> Dict[str, Any] | None:
        for provider in self.list_all():
            if str(provider.get("provider_name", "")).lower() == provider_name.lower():
                return provider
        return None


provider_repository = ProviderRepository()
