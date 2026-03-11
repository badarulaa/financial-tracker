from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str

  WHATSAPP_TOKEN: str
  WHATSAPP_PHONE_NUMBER_ID: str
  WHATSAPP_VERIFY_TOKEN: str
  USER_PHONE_OWNER: str
  USER_PHONE_WIFE: str
  FOLDER_ID: str

  class Config:
    env_file = ".env"

settings = Settings()