# coding: utf-8
import hashlib
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI,  HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import Response, JSONResponse, FileResponse
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

import models

# 乱数を設置
JWT_PASSWORD='8e07629855554c369f12991cc47cec461eee29ab938e47d19b1143148f50672b'
ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = 30

# tokenUrl にはトークンを取得するURLを指定する
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/get_token')

app = FastAPI()

########## 補助ライブラリ ###############
def create_access_token(*, data: dict, expires_delta: timedelta = None):
    """
    ログイン情報を元にトークンを作成する

    Params:
        data: dict
            ユーザー情報

        expires_delta: timedelta
            トークンの有効時間
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)

    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, JWT_PASSWORD, algorithm=ALGORITHM)
    return encode_jwt


def search_user(username: str):
    """
    ユーザー情報を検索するロジック。DBなどによって異なるので省略。
    """
    return {
        'userId': 1,
        'userName': 'ユーザー名'
    }

def search_user_for_token(username: str, password: str):
    """
    トークン発行時にユーザーを検索する
    """
    # パスワードを暗号化している場合
    hashed_password = hashlib.sha512(password.encode()).hexdigest()
    # username と password/hashed_password で検索をかけた結果を返す

    return {
        'userId': 1,
        'userName': 'ユーザー名'
    }


def get_user_data(token: str = Depends(oauth2_scheme)):
    """
    トークンからユーザー情報を検索する

    Params:
        token: str
            トークン
    """

    credentials_exc = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail='Credentialが検証できません',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, JWT_PASSWORD, algorithms=[ALGORITHM])
        user_name: str = payload.get('userName')
        if user_name is None:
            raise credentials_exc
        token_data = models.TokenData(userName=user_name)
    except PyJWTError:
        raise credentials_exc

    user_info = search_user(user_name)
    if user_info is None:
        raise credentials_exc

    return user_info


############## MAIN ################

@app.post('/get_token', response_model=models.GetTokenResponseModel)
def get_token(m: models.GetTokenModel):

    user = search_user_for_token(m.userName, m.password)

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='ユーザー名/パスワードが違います',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    # トークンを作成
    token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'userName': user['userName']},
        expires_delta=token_expires
    )
    return {'token': access_token, 'token_type': 'bearer'}


@app.post('/get_user', response_model=models.GetUserResponseModel)
async def get_user(user_data: models.GetUserResponseModel = Depends(get_user_data)):

    return JSONResponse({'user': user_data})
