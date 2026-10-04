from dataclasses import asdict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..calculator.parser import CalculationError
from ..database.database import clear_history, delete_history_record, list_history
from ..schemas.schemas import CalculationRequest
from ..services.calculator_service import calculate_and_save


router = APIRouter(prefix="/api")


@router.post("/calculate")
def calculate_expression(request: CalculationRequest):
    try:
        result = calculate_and_save(request.expression)
    except CalculationError as error:
        return JSONResponse(status_code=400, content={"success": False, "message": str(error)})
    return {"success": True, "expression": request.expression, "result": result}


@router.get("/history")
def get_history():
    return {"success": True, "data": [asdict(record) for record in list_history()]}


@router.delete("/history/{record_id}")
def delete_history(record_id: int):
    if not delete_history_record(record_id):
        return JSONResponse(status_code=404, content={"success": False, "message": "历史记录不存在"})
    return {"success": True, "message": "删除成功"}


@router.delete("/history")
def delete_all_history():
    count = clear_history()
    return {"success": True, "deleted": count}
