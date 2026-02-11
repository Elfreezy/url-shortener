from fastapi import FastAPI, status, Response
from fastapi.responses import RedirectResponse
from app.service import service
from loguru import logger

app = FastAPI()

@app.post("/shorten/")
def generate_short_link(url: str, response: Response):
    short_url = None
    try:
        short_url = service.add_short_link(url)
        response.status_code = status.HTTP_201_CREATED
    except Exception as e:
        logger.exception(e)
        response.status_code = status.HTTP_400_BAD_REQUEST
    return short_url

@app.get("/{code}")
def redirect_by_code(code: str, response: Response):
    try:
        short_link = service.get_short_link_by_code(code)
        if short_link:
            return RedirectResponse(
                url=short_link,
                status_code=status.HTTP_302_FOUND,
            )
    except Exception as e:
        logger.exception(e)
        response.status_code = status.HTTP_502_BAD_GATEWAY

@app.get("/links/delete/{code}")
def delete_link_by_code(code: str, response: Response):
    try:
        service.delete_link_by_code(code)
        response.status_code = status.HTTP_200_OK
    except Exception as e:
        logger.exception(e)
        response.status_code = status.HTTP_404_NOT_FOUND

@app.get("/links/")
def get_all_links(response: Response):
    all_links = None
    try:
        all_links = service.get_all_links()
        response.status_code = status.HTTP_200_OK
    except Exception as e:
        logger.exception(e)
        response.status_code = status.HTTP_404_NOT_FOUND
    return all_links