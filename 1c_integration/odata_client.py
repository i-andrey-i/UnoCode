import requests
from datetime import datetime
from typing import Optional, Dict, List
import logging
from .config import settings

class ODataClient:
    def __init__(self):
        self.base_url = settings.ODATA_BASE_URL
        self.auth = (settings.ODATA_USER, settings.ODATA_PASSWORD)
        self.headers = {
            "Accept": "application/json",
            "DataServiceVersion": settings.ODATA_VERSION,
            "MaxDataServiceVersion": settings.ODATA_VERSION
        }
        self.logger = logging.getLogger(__name__)

    def _build_filter(self, date_from: Optional[datetime] = None) -> str:
        """Построение фильтра OData"""
        if date_from:
            return f"Date ge {date_from.strftime('%Y-%m-%dT%H:%M:%S')}"
        return ""

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Выполнение запроса с обработкой ошибок"""
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                auth=self.auth,
                verify=True  # SSL verification
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"OData request failed: {str(e)}")
            raise

    async def get_documents(self, doc_type: str, date_from: Optional[datetime] = None) -> List[Dict]:
        """
        Получение документов из 1С
        
        Args:
            doc_type: Тип документа (ПриходнаяНакладная, РасходнаяНакладная)
            date_from: Дата, с которой начинать выборку
        """
        url = f"{self.base_url}/Document_{doc_type}"
        params = {
            "$filter": self._build_filter(date_from),
            "$select": "Ref_Key,Number,Date,Posted,Организация_Key",
            "$expand": "Товары",
            "$orderby": "Date desc"
        }

        self.logger.info(f"Fetching documents of type {doc_type}")
        result = self._make_request(url, params)
        return result.get("value", [])

    async def get_catalog_item(self, catalog: str, ref_key: str) -> Dict:
        """
        Получение элемента справочника
        
        Args:
            catalog: Имя справочника (Номенклатура, Контрагенты)
            ref_key: Ключ ссылки на элемент справочника
        """
        url = f"{self.base_url}/Catalog_{catalog}(guid'{ref_key}')"
        
        self.logger.debug(f"Fetching catalog item {catalog} with key {ref_key}")
        result = self._make_request(url)
        return result 