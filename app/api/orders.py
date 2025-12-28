from fastapi import APIRouter, HTTPException, Path, Query
from typing import List
import httpx
from app.models import OrderCreate, OrderResponse, PaymentCreate, PaymentResponse
from app.services.retailcrm import retailcrm_service

router = APIRouter()


@router.get("/customers/{customer_id}/orders", response_model=List[OrderResponse])
async def get_customer_orders(
    customer_id: int = Path(..., description="Customer ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=20, le=100, description="Items per page (20, 50, or 100)")
):
    try:
        if limit not in [20, 50, 100]:
            limit = 20
        
        result = await retailcrm_service.get_orders(
            customer_id=customer_id,
            page=page,
            limit=limit
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch orders")
        
        orders = result.get("orders", [])
        return [
            OrderResponse(
                id=order["id"],
                number=order.get("number"),
                customer_id=order.get("customer", {}).get("id"),
                created_at=order.get("createdAt"),
                status=order.get("status"),
                total_sum=order.get("totalSumm")
            )
            for order in orders
        ]
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/orders", response_model=dict)
async def create_order(order: OrderCreate):
    try:
        order_data = {
            "customer": {"id": order.customer_id},
            "items": []
        }
        
        if order.number:
            order_data["number"] = order.number
        
        for item in order.items:
            order_data["items"].append({
                "productName": item.product_name,
                "quantity": item.quantity,
                "initialPrice": item.price
            })
        
        result = await retailcrm_service.create_order(order_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("errorMsg", "Failed to create order")
            )
        
        return {
            "success": True,
            "id": result.get("id"),
            "message": "Order created successfully"
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/orders/{order_id}/payment", response_model=dict)
async def create_order_payment(
    order_id: int = Path(..., description="Order ID"),
    payment: PaymentCreate = None
):
    try:
        payment_data = {
            "type": payment.type,
            "status": payment.status,
            "amount": payment.amount
        }
        
        result = await retailcrm_service.create_payment(order_id, payment_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("errorMsg", "Failed to create payment")
            )
        
        return {
            "success": True,
            "id": result.get("id"),
            "message": "Payment created successfully"
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")