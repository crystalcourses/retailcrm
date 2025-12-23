import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.models import CustomerFilter, CustomerCreate, CustomerResponse
from app.services.retailcrm import retailcrm_service

router = APIRouter()


@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    created_at_from: Optional[datetime] = Query(None, description="Filter by creation date from"),
    created_at_to: Optional[datetime] = Query(None, description="Filter by creation date to"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    try:
        created_from_str = created_at_from.strftime("%Y-%m-%d %H:%M:%S") if created_at_from else None
        created_to_str = created_at_to.strftime("%Y-%m-%d %H:%M:%S") if created_at_to else None
        
        result = await retailcrm_service.get_customers(
            first_name=first_name,
            last_name=last_name,
            email=email,
            created_at_from=created_from_str,
            created_at_to=created_to_str,
            page=page,
            limit=limit
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch customers")
        
        customers = result.get("customers", [])
        return [
            CustomerResponse(
                id=customer["id"],
                first_name=customer.get("firstName"),
                last_name=customer.get("lastName"),
                email=customer.get("email"),
                phone=customer.get("phones", [{}])[0].get("number") if customer.get("phones") else None,
                created_at=customer.get("createdAt")
            )
            for customer in customers
        ]
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/customers", response_model=dict)
async def create_customer(customer: CustomerCreate):
    try:
        customer_data = {}
        
        if customer.first_name:
            customer_data["firstName"] = customer.first_name
        if customer.last_name:
            customer_data["lastName"] = customer.last_name
        if customer.email:
            customer_data["email"] = customer.email
        if customer.phone:
            customer_data["phones"] = [{"number": customer.phone}]
        
        result = await retailcrm_service.create_customer(customer_data)
        
        if not result.get("success"):
            error_msg = result.get("errorMsg", "Failed to create customer")
            errors = result.get("errors", {})
            detail = f"{error_msg}. Errors: {errors}" if errors else error_msg
            raise HTTPException(status_code=400, detail=detail)
        
        return {
            "success": True,
            "id": result.get("id"),
            "message": "Customer created successfully"
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")