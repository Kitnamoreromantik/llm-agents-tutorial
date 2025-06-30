import time
from chain_notice_extraction import NoticeEmailExtract
from graph_notice_extraction import NOTICE_EXTRACTION_GRAPH
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from llm.factory import get_llm
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from utils.logging_config import LOGGER
# notice imported MessagesState instead of GraphState. 
# MessagesState is a predefined GraphState that has only one attribute called messages


@tool
def forward_email(email_message: str, send_to_email: str) -> bool:
    """
    Пересылает сообщение email_message на адрес send_to_email. 
    Возвращает True, если отправка прошла успешно, иначе - False. 
    Обратите внимание, что инструмент только пересылает письмо во внутренний отдел,
    но не отвечает отправителю.
    """
    LOGGER.info(f"Пересылаем письмо на адрес {send_to_email}...")
    time.sleep(2)
    LOGGER.info("Письмо переслано!")
    return True

@tool
def send_wrong_email_notification_to_sender(
    sender_email: str, correct_department: str
    ):
    """
    Отправляет письмо отправителю, уведомляя его о том,
    что письмо было направлено не по адресу. В письме
    указывается, что следует обратиться в correct_department.
    """
    LOGGER.info(f"Отправляем уведомление о неверном адресе на {sender_email}...")
    time.sleep(2)
    LOGGER.info("Письмо отправлено!")
    return True

@tool
def extract_notice_data(
    email: str, escalation_criteria: str
) -> NoticeEmailExtract:
    """
    Извлекает структурированные поля из регуляторного уведомления.
    Этот инструмент следует использовать, когда письмо поступает
    от регуляторного органа или аудитора и касается объекта
    недвижимости или строительной площадки, с которой работает компания.
    Параметр escalation_criteria описывает, какие типы уведомлений
    требуют немедленной эскалации.
    После вызова этого инструмента не нужно вызывать другие.
    """
    LOGGER.info("Запуск графа извлечения данных из регуляторного уведомления...")
    initial_state = {
        "notice_message": email,
        "notice_email_extract": None,
        "critical_fields_missing": False,
        "escalation_text_criteria": escalation_criteria,
        "escalation_dollar_criteria": 100_000,
        "requires_escalation": False,
        "escalation_emails": ["brog@abc.ru", "bigceo@company.ru"],
    }

    results = NOTICE_EXTRACTION_GRAPH.invoke(initial_state)
    return results["notice_email_extract"]

@tool
def determine_email_action(email: str) -> str:
    """
    Вызывает определение необходимого действия для email-сообщения.
    Использовать только в тех случаях, когда другие инструменты
    не подходят для обработки письма. Не вызывать этот инструмент,
    если уже был вызван extract_notice_data.
    """
    return """
    Если письмо похоже на счет или связано с оплатой, переслать его
    в отдел выставления счетов: billing@company.ru и отправить
    уведомление отправителю о неверном адресе. Указать, что правильный
    отдел это billing@company.ru.

    Если письмо от клиента, переслать его на:
    support@company.ru, cdetuma@company.ru и ctu@abc.ru.
    Обязательно отправить всем трём адресатам.
    Также отправить уведомление клиенту, что правильный отдел это
    support@company.ru.

    Для всех остальных писем отправить уведомление о неверном адресе
    и попытаться определить правильный отдел из списка:
    billing@company.ru, support@company.ru,
    humanresources@company.ru, it@company.ru.
    """



tools = [
    determine_email_action,
    forward_email,
    send_wrong_email_notification_to_sender,
    extract_notice_data,
]

tool_node = ToolNode(tools)

EMAIL_AGENT_MODEL = get_llm("gigachat:GigaChat-2-Max").bind_tools(tools)

def call_agent_model_node(state: MessagesState) -> dict[str, list[AIMessage]]:
    """Node to call the email agent model"""
    messages = state["messages"]
    response = EMAIL_AGENT_MODEL.invoke(messages)
    return {"messages": [response]}

def route_agent_graph_edge(state: MessagesState) -> str:
    """Determine whether to call more tools or exit the graph"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "email_tools"
    return END


workflow = StateGraph(MessagesState)
# Add agent nodes:
workflow.add_node("email_agent", call_agent_model_node)
workflow.add_node("email_tools", tool_node)
# Add agent edges:
workflow.add_edge(START, "email_agent")
workflow.add_conditional_edges(
    "email_agent", route_agent_graph_edge, ["email_tools", END]
)
workflow.add_edge("email_tools", "email_agent")

email_agent_graph = workflow.compile()

