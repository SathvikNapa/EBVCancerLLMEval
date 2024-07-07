import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from mcqa.domain.response_generator import GeneratorRequest
from mcqa.mcqa import Mcqa

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

logger.setLevel(logging.DEBUG)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: str


@app.post("/generate_response")
def generate_response(user_query: GeneratorRequest):
    """Endpoint to generate a response for a given user query.

    Args:
        user_query (GeneratorRequest): The request containing the user query.

    Returns:
        QueryResponse: The response generated by the MCQA system.
    """
    mcqa = Mcqa(request=user_query)
    return mcqa.generate_query_response()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles HTTP exceptions and returns a JSON response.

    Args:
        request (Request): The incoming request.
        exc (HTTPException): The HTTP exception raised.

    Returns:
        JSONResponse: The JSON response containing the error message.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )
