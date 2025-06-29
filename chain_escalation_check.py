"""
Эта цепочка проверяет, требует ли уведомление по электронной почте эскалации внутри компании, 
основываясь на текстовом описании критериев эскалации. 
Например, вы можете захотеть эскалировать сообщение, если в нём говорится об угрозе для сотрудников 
или если уведомление предупреждает о штрафе, превышающем установленный порог.
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm.factory import get_llm
import json

class EscalationCheck(BaseModel):
    """Проверка на эскалацию"""
    needs_escalation: bool = Field(
        description="Требует ли уведомление эскалации в соответствии с заданными критериями."
    )

raw_schema = EscalationCheck.model_json_schema()
pretty_schema = json.dumps(raw_schema, ensure_ascii=False, indent=2)
escaped_schema = pretty_schema.replace("{", "{{").replace("}", "}}")

escalation_prompt = ChatPromptTemplate.from_messages(
    [("system",
      f"""
        Определите, требует ли следующее уведомление, полученное от регулирующего органа, немедленной эскалации.
        Немедленная эскалация требуется, если выполняются следующие условия: {{escalation_criteria}}.

        Извлеки из уведомления следующую информацию и верни ее строго в формате JSON, соответствующем этой модели:
        {escaped_schema}

        Вот текст уведомления:
        {{message}}
        """,
    )])

escalation_check_model = get_llm("gigachat:GigaChat-2-Max")
ESCALATION_CHECK_CHAIN = escalation_prompt | escalation_check_model
