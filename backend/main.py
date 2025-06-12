from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import random
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from keycloak import KeycloakOpenID
from settings import settings

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reports API",
    description="API for generating and managing reports",
    version="1.0.0",
)

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

keycloak_openid = KeycloakOpenID(
    server_url=settings.keycloak_url,
    client_id=settings.keycloak_client_id,
    realm_name=settings.keycloak_realm,
    client_secret_key=settings.keycloak_client_secret,
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверка роли пользователя и подписи токена"""
    try:
        token = credentials.credentials
        payload = keycloak_openid.decode_token(
            token,
            options={"verify_signature": True, "verify_aud": True, "verify_exp": True},
        )

        if settings.required_role not in payload.get("realm_access", {}).get(
            "roles", []
        ):
            logger.warning(
                f"User does not have required role '{settings.required_role}'"
            )
            raise HTTPException(
                status_code=403,
                detail=f"User does not have required role '{settings.required_role}'",
            )

        return payload
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


def generate_report_data() -> List[Dict]:
    """Генерация тестовых данных для отчетов"""
    reports = []
    statuses = ["completed", "in_progress", "pending"]
    types = ["daily", "weekly", "monthly"]

    for i in range(10):
        report_date = datetime.now() - timedelta(days=i)
        reports.append(
            {
                "id": i + 1,
                "title": f"Report {i + 1}",
                "type": random.choice(types),
                "status": random.choice(statuses),
                "created_at": report_date.isoformat(),
                "data": {
                    "metrics": {
                        "total_users": random.randint(100, 1000),
                        "active_users": random.randint(50, 500),
                        "revenue": random.randint(1000, 10000),
                    },
                    "details": {
                        "region": random.choice(["North", "South", "East", "West"]),
                        "category": random.choice(["A", "B", "C"]),
                        "priority": random.choice(["high", "medium", "low"]),
                    },
                },
            }
        )
    return reports


@app.get("/reports", response_model=List[Dict])
async def get_reports(token: Dict = Depends(verify_token)):
    """Получение списка отчетов"""
    logger.info("Getting reports")
    return generate_report_data()


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port)
