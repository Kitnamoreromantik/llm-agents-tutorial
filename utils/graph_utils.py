import random
import time
from pydantic import EmailStr
from chain_notice_extraction import NoticeEmailExtract
from utils.logging_config import LOGGER

def send_escalation_email(
    notice_email_extract: NoticeEmailExtract,
    escalation_emails: list[EmailStr]) -> None:
    """Симуляция отправки писем об эскалации"""
    LOGGER.info("Отправка писем об эскалации...")
    for email in escalation_emails:
        time.sleep(1)
        LOGGER.info(f"Письмо об эскалации отправлено на адрес {email}")

def create_legal_ticket(
    current_follow_ups: dict[str, bool] | None,
    notice_email_extract: NoticeEmailExtract,) -> str | None:
    """Симуляция создания юридического обращения через API вашей компании."""
    LOGGER.info("Создание юридического обращения по уведомлению...")
    time.sleep(2)

    follow_ups = [
        None,
        "Упоминаются ли в сообщении регионы: Москва, Краснодарский край или Свердловская область?",
        "Связано ли уведомление с неисправностью системы вентиляции ООО 'ПсевдоКлимат'?",
    ]

    if current_follow_ups:
        follow_ups = [f for f in follow_ups if f not in current_follow_ups.keys()]
    follow_up = random.choice(follow_ups)
    if not follow_up:
        LOGGER.info("Юридическое обращение успешно создано!")
        return follow_up

    LOGGER.info("Требуется дополнительная информация перед созданием обращения")
    return follow_up

