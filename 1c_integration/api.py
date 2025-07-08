import logging
from datetime import datetime
from typing import List, Dict, Optional
from odata_client import ODataClient
from db import save_product_transaction
from config import settings

logger = logging.getLogger(__name__)

class OneCAPI:
    def __init__(self):
        self.client = ODataClient()

    async def _process_document_items(self, doc: Dict, operation_type: str) -> List[Dict]:
        """
        Обработка товаров из документа
        
        Args:
            doc: Документ из 1С
            operation_type: Тип операции (Поступление/Расход)
        """
        operations = []
        try:
            # Получаем организацию
            org = await self.client.get_catalog_item("Организации", doc["Организация_Key"])
            
            # Обрабатываем каждый товар
            for item in doc.get("Товары", []):
                try:
                    # Получаем информацию о номенклатуре
                    product = await self.client.get_catalog_item(
                        "Номенклатура", 
                        item["Номенклатура_Key"]
                    )
                    
                    operation = {
                        "organization": org["Description"],
                        "operation": operation_type,
                        "method": "Закупка" if operation_type == "Поступление" else "Реализация",
                        "item": product["Description"],
                        "date": doc["Date"],
                        "external_id": f"{doc['Ref_Key']}_{item.get('LineNumber', 0)}"
                    }
                    operations.append(operation)
                except Exception as e:
                    logger.error(f"Error processing item in document {doc['Ref_Key']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing document {doc['Ref_Key']}: {str(e)}")
            
        return operations

    async def fetch_product_operations(self, date_from: Optional[datetime] = None) -> List[Dict]:
        """Получение товарных операций"""
        all_operations = []
        
        try:
            # Получаем приходные накладные
            income_docs = await self.client.get_documents(
                settings.DOCUMENT_TYPES["income"], 
                date_from
            )
            
            for doc in income_docs:
                if not doc.get("Posted", False):
                    logger.debug(f"Skipping unposted document {doc.get('Ref_Key')}")
                    continue
                    
                operations = await self._process_document_items(doc, "Поступление")
                all_operations.extend(operations)
            
            # Получаем расходные накладные
            expense_docs = await self.client.get_documents(
                settings.DOCUMENT_TYPES["expense"], 
                date_from
            )
            
            for doc in expense_docs:
                if not doc.get("Posted", False):
                    continue
                    
                operations = await self._process_document_items(doc, "Расход")
                all_operations.extend(operations)
                
        except Exception as e:
            logger.error(f"Error fetching product operations: {str(e)}")
            raise
            
        return all_operations

    async def sync_data(self, date_from: Optional[datetime] = None) -> Dict:
        """
        Синхронизация данных с 1С
        
        Args:
            date_from: Дата, с которой начинать синхронизацию
        """
        logger.info("Starting 1C data synchronization")
        try:
            operations = await self.fetch_product_operations(date_from)
            
            success_count = 0
            error_count = 0
            
            for operation in operations:
                try:
                    await save_product_transaction(operation)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error saving operation: {str(e)}")
                    error_count += 1
            
            logger.info(f"Synchronization completed. Success: {success_count}, Errors: {error_count}")
            
            return {
                "status": "success",
                "total": len(operations),
                "success": success_count,
                "errors": error_count
            }
            
        except Exception as e:
            logger.error(f"Synchronization failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            } 