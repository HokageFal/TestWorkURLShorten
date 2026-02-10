import logging
from fastapi import APIRouter, HTTPException, Request

from src.schemas.links import ShortenRequest, ShortenResponse, URLStats
from src.services.shortener import URLShortenerService
from src.database import Database

logger = logging.getLogger(__name__)

router = APIRouter()

db = Database()
service = URLShortenerService(db)


@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest, req: Request):
    try:
        original_url = str(request.url)
        custom_code = request.custom_code
        
        short_code = service.create_short_url(original_url, custom_code)
        
        base_url = f"{req.url.scheme}://{req.url.netloc}"
        short_url = f"{base_url}/{short_code}"
        
        logger.info(f"Создана короткая ссылка: {short_code} -> {original_url}")
        
        return ShortenResponse(
            short_url=short_url,
            original_url=original_url,
            short_code=short_code
        )
    except ValueError as e:
        logger.error(f"Ошибка валидации: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при создании короткой ссылки: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/info/{code}", response_model=URLStats)
async def get_url_info(code: str):
    stats = service.get_url_stats(code)
    
    if not stats:
        logger.warning(f"Запрошена информация для несуществующего кода: {code}")
        raise HTTPException(status_code=404, detail="Короткая ссылка не найдена")
    
    return URLStats(**stats)


@router.delete("/{code}")
async def delete_url(code: str):
    deleted = service.delete_url(code)
    
    if not deleted:
        logger.warning(f"Попытка удалить несуществующий код: {code}")
        raise HTTPException(status_code=404, detail="Короткая ссылка не найдена")
    
    logger.info(f"Удалена короткая ссылка: {code}")
    return {"message": "Ссылка успешно удалена", "short_code": code}
