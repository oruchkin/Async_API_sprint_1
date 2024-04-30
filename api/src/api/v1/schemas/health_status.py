from pydantic import BaseModel


class HealthStatus(BaseModel):
    redis: bool
    elasticsearch: bool
