# coding: utf-8
from pydantic import BaseModel


class GetTokenModel(BaseModel):
    """
    /get_token で受け取るパラメータ
    """
    userName: str
    password: str


class GetTokenResponseModel(BaseModel):
    """
    /get_token で返す
    """
    token: str
    token_type: str = 'bearer'


class GetUserModel(BaseModel):
    """
    /get_user で受け取るパラメータ
    """
    token: str


class TokenData(BaseModel):
    """
    トークン
    """
    userName: str


class GetUserResponseModel(BaseModel):
    """
    ユーザー情報
    """
    userName: str
    userInfo: dict
