from typing import Optional
from pydantic import BaseModel


# Source: https://fastapi.tiangolo.com/tutorial/body/
# The "User" BaseModel describes the format of the expected data
# This data should be passed to the API via the (POST) request's body
class SessionData(BaseModel):
    client_id: str
    client_ip: Optional[str] = None
    client_os: str
    service: str
    active_website: Optional[str] = None
    # This is a list of the in-App notifications such as for Website Transfer
    notifications: Optional[dict] = None


class UserLogin(BaseModel):
    email: str
    client_key: str


class User(BaseModel):
    name: str
    email: str
    password: str
    service: str
    country: str
    locale: str
    notifications: Optional[int] = 1
    promos: Optional[int] = 1


class UserSearch(BaseModel):
    client_key: str
    email: str


class Website(BaseModel):
    domain: str
    domain_exp: Optional[str] = None
    certificate: Optional[str] = None
    certificate_exp: Optional[str] = None


class WebsiteSearch(BaseModel):
    domain: str


class WebsiteUserSearch(BaseModel):
    client_id: str


class WordPress(BaseModel):
    website_id: str
    url: str
    path: Optional[str] = None
    version: Optional[str] = None
    themes: Optional[dict] = None
    plugins: Optional[dict] = None
    permalinks: Optional[str] = None
    size: Optional[str] = None
    inodes: Optional[str] = 0


class Account(BaseModel):
    account_id: str
    website_id: str
    type: str
    hostname: str
    username: str
    password: str
    port: str
    path: Optional[str]


class Backup(BaseModel):
    website_id: str
    backup_id: str
    size: str
    date: str
    path: str
    host: str

