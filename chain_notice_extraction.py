"""
Представьте, что вы работаете в крупной девелоперской компании, которая ежедневно получает сотни писем от регуляторов 
и других организаций по действующим стройкам. Например, может прийти уведомление от инспектора о нарушении техники безопасности.

Ваша задача - создать инструмент, который будет читать такие письма, извлекать из них важную информацию и уведомлять нужную команду. 
Первый шаг — построить цепочку LangChain, использующую LLM для извлечения структурированных данных из письма. 
Для этого вы сначала определяете Pydantic BaseModel с нужными полями.
"""

from datetime import datetime, date
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, computed_field
from llm.factory import get_llm
import json


"""
    Этот класс описывает структурированную модель данных на основе Pydantic, 
    которая предназначена для извлечения информации из писем с уведомлениями, 
    например, от регуляторов на стройке. Такая модель используется в пайплайнах с LLM, чтобы упорядочить результаты извлечения.

    Что делает модель NoticeEmailExtract:
        - Каждое поле описывает один тип информации, которую нужно извлечь из письма:
        - entity_name — название организации-отправителя
        - project_id — ID проекта
        - violation_type — тип нарушения
        - required_changes — какие изменения требуются
        - и т.д.

    Поля, заканчивающиеся на _str (например, date_of_notice_str), содержат даты в виде строки, извлеченные из текста письма. 
    Эти строки не выводятся при сериализации (exclude=True) и преобразуются в реальные объекты date через @computed_field.

    Зачем нужны @computed_field:
    - Методы date_of_notice и compliance_deadline возвращают готовые объекты даты, 
    чтобы потом было удобно сравнивать дедлайны, фильтровать по дате и т.д.
    - Для преобразования используется datetime.strptime с форматом "YYYY-mm-dd".

    Таким образом, эта модель данных позволяет LLM или другой системе извлекать из неструктурированного текста письма 
    четко определенные поля, чтобы автоматически передавать их другим частям системы 
    (например, для уведомления нужной команды или записи в базу данных).
"""
class NoticeEmailExtract(BaseModel):

    date_of_notice_str: str | None = Field(
        default=None,
        exclude=True,  # you won’t see date_of_notice_str when you serialize or display NoticeEmailExtract
        repr=False,  # you won’t see date_of_notice_str when you serialize or display NoticeEmailExtract
        description="Дата уведомления (если указана), отформатированная как YYYY-mm-dd",
    )
    entity_name: str | None = Field(
        default=None,
        description="Название организации, отправившей уведомление (если указано в сообщении)",
    )

    entity_phone: str | None = Field(
        default=None,
        description="Телефон организации, отправившей уведомление (если указан в сообщении)",
    )

    entity_email: str | None = Field(
        default=None,
        description="Email организации, отправившей уведомление (если указан в сообщении)",
    )

    project_id: int | None = Field(
        default=None,
        description="ID проекта (если указан в сообщении) — должен быть целым числом",
    )

    site_location: str | None = Field(
        default=None,
        description="Адрес строительной площадки (если указан в сообщении). По возможности использовать полный адрес.",
    )

    violation_type: str | None = Field(
        default=None,
        description="Тип нарушения (если указан в сообщении)",
    )

    required_changes: str | None = Field(
        default=None,
        description="Необходимые изменения, указанные в уведомлении (если присутствуют)",
    )

    compliance_deadline_str: str | None = Field(
        default=None,
        exclude=True,
        repr=False,
        description="Срок устранения нарушения (если указан), отформатированный как YYYY-mm-dd",
    )

    max_potential_fine: float | None = Field(
        default=None,
        description="Максимально возможный штраф (если указан)",
    )

    @staticmethod
    def _convert_string_to_date(date_str: str | None) -> date | None:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception as e:
            print(e)
            return None

    @computed_field
    @property
    def date_of_notice(self) -> date | None:
        # Автоматическое преобразование строки в дату уведомления
        return self._convert_string_to_date(self.date_of_notice_str)

    @computed_field
    @property
    def compliance_deadline(self) -> date | None:
        # Автоматическое преобразование строки в дату дедлайна
        return self._convert_string_to_date(self.compliance_deadline_str)
    

# генерируем JSON-схему и сериализуем с читаемыми символами
raw_schema = NoticeEmailExtract.model_json_schema()
pretty_schema = json.dumps(raw_schema, ensure_ascii=False, indent=2)

# экранируем скобки для LangChain-подстановки
escaped_schema = pretty_schema.replace("{", "{{").replace("}", "}}")
    
# Next, you create a chain to parse notice emails:
info_parse_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
            Извлеки из уведомления следующую информацию и верни ее строго в формате JSON, 
            соответствующем этой модели:
            {escaped_schema}

            Если какие-либо поля отсутствуют — не включай их в результат.
            Пример допустимого результата:
            Ответь только JSON, без комментариев и пояснений.

            Вот текст уведомления:
            {{message}}
            """
    )
])

NOTICE_PARSER_CHAIN = (info_parse_prompt | get_llm("gigachat:GigaChat-2-Max"))
