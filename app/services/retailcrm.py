import httpx
import json
from typing import Optional, Dict, Any
from app.config import settings


class RetailCRMService:
    def __init__(self):
        self.base_url = settings.retailcrm_url.rstrip('/')
        self.api_key = settings.retailcrm_api_key
        self.api_version = "v5"
    
    def _get_url(self, endpoint: str) -> str:
        return f"{self.base_url}/api/{self.api_version}/{endpoint}"
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_param: Optional[str] = None
    ) -> Dict[str, Any]:
        url = self._get_url(endpoint)
        
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                if json_param and data:
                    form_data = {json_param: json.dumps(data, ensure_ascii=False)}
                else:
                    form_data = data or {}
                
                print(f"DEBUG: URL: {url}")
                print(f"DEBUG: Form data: {form_data}")
                
                response = await client.post(
                    url, 
                    params=params,
                    data=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                print(f"DEBUG: Response status: {response.status_code}")
                print(f"DEBUG: Response text: {response.text}")
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
    
    async def get_customers(
        self, 
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        created_at_from: Optional[str] = None,
        created_at_to: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        params = {
            "page": page,
            "limit": limit
        }
        
        filter_params = {}
        if first_name:
            filter_params["firstName"] = first_name
        if last_name:
            filter_params["lastName"] = last_name
        if email:
            filter_params["email"] = email
        if created_at_from:
            filter_params["createdAtFrom"] = created_at_from
        if created_at_to:
            filter_params["createdAtTo"] = created_at_to
        
        if filter_params:
            for key, value in filter_params.items():
                params[f"filter[{key}]"] = value
        
        return await self._make_request("GET", "customers", params=params)
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", "customers/create", data=customer_data, json_param="customer")
    
    async def get_orders(
        self,
        customer_id: Optional[int] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        params = {
            "page": page,
            "limit": limit
        }
        
        if customer_id:
            params["filter[customerId]"] = customer_id
        
        return await self._make_request("GET", "orders", params=params)
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", "orders/create", data=order_data, json_param="order")
    
    async def create_payment(
        self, 
        order_id: int, 
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        payment_data["order"] = {"id": order_id}
        return await self._make_request("POST", "orders/payments/create", data=payment_data, json_param="payment")


retailcrm_service = RetailCRMService()