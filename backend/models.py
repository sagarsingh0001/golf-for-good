"""Pydantic models."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    charity_id: Optional[str] = None
    charity_percentage: float = 10.0


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    role: str
    subscription_status: str
    subscription_plan: Optional[str] = None
    subscription_end: Optional[str] = None
    charity_id: Optional[str] = None
    charity_percentage: float = 10.0
    created_at: Optional[str] = None


class ScoreCreate(BaseModel):
    value: int = Field(ge=1, le=45)
    date: str  # YYYY-MM-DD


class ScoreUpdate(BaseModel):
    value: int = Field(ge=1, le=45)


class CharityCreate(BaseModel):
    name: str
    short_description: str
    description: str
    image_url: str
    category: Optional[str] = "General"
    events: List[dict] = []
    featured: bool = False


class CharityUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    events: Optional[List[dict]] = None
    featured: Optional[bool] = None


class CheckoutRequest(BaseModel):
    plan: str  # "monthly" | "yearly"
    origin_url: str


class DrawConfig(BaseModel):
    month: str  # YYYY-MM
    logic_type: str = "random"  # random | algorithmic


class DrawPublishRequest(BaseModel):
    draw_id: str


class CharitySelection(BaseModel):
    charity_id: str
    charity_percentage: float = Field(ge=10.0, le=100.0)


class WinnerVerify(BaseModel):
    winner_id: str
    action: str  # approve | reject
    note: Optional[str] = None


class WinnerPayoutUpdate(BaseModel):
    winner_id: str
    payout_status: str  # pending | paid


class NotificationOut(BaseModel):
    id: str
    title: str
    body: str
    type: str
    read: bool
    created_at: str
