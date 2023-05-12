from pydantic import BaseSettings


class Config(BaseSettings):
    apex_api_token = "5ef950f2bf26401b30a1e611484ef130"

    class Config:
        extra = "ignore"