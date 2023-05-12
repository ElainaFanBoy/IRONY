from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """百度翻译配置，见 https://fanyi-api.baidu.com/doc/21"""
    appid: str = "20191124000359961"
    salt: str = "777"
    key: str = "LpX_4Bfx1z09rKn37JbK"
