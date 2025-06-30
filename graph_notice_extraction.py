from typing import TypedDict
from chain_escalation_check import ESCALATION_CHECK_CHAIN
from chain_notice_extraction import (NOTICE_PARSER_CHAIN, 
    NoticeEmailExtract)
from langgraph.graph import END, START, StateGraph
from pydantic import EmailStr
from utils.graph_utils import create_legal_ticket, send_escalation_email
from utils.logging_config import LOGGER
import json
import re

class GraphState(TypedDict):
    notice_message: str
    notice_email_extract: NoticeEmailExtract | None
    escalation_text_criteria: str
    escalation_money_criteria: float
    needs_escalation: bool
    escalation_emails: list[EmailStr] | None
    follow_ups: dict[str, bool] | None
    current_follow_up: str | None

workflow = StateGraph(GraphState)


def parse_notice_message_node(state: GraphState) -> GraphState:
    """Use the notice parser chain to extract fields from the notice"""
    LOGGER.info("Parsing notice...")
    notice_email_extract = NOTICE_PARSER_CHAIN.invoke(
        {"message": state["notice_message"]}
    )
    state["notice_email_extract"] = notice_email_extract
    return state

def check_escalation_status_node(state: GraphState) -> GraphState:
    """Determine whether a notice needs escalation"""
    LOGGER.info("Determining escalation status...")
    text_check = ESCALATION_CHECK_CHAIN.invoke(
        { "escalation_criteria": state["escalation_text_criteria"],
        "message": state["notice_message"]})
    print(text_check.content)
    json_text = re.search(r"```json\s*(\{.*?\})\s*```", text_check.content, re.DOTALL)
    json_obj = json.loads(json_text.group(1))
    text_check = json_obj.get("needs_escalation", None)

    # print(f"STATE: {state}\n")
    # json_text = re.search(r"```json\s*(\{.*?\})\s*```", state["notice_email_extract"].content, re.DOTALL)
    json_text = re.search(r"(\{.*?\})", state["notice_email_extract"].content, re.DOTALL)
    # print(f"json_text_2: {json_text}")
    json_obj = json.loads(json_text.group(1))
    max_potential_fine = json_obj.get("max_potential_fine", None)

    if text_check or (max_potential_fine >= state["escalation_money_criteria"]):
        state["needs_escalation"] = True
    else:
        state["needs_escalation"] = False
    return state

def send_escalation_email_node(state: GraphState) -> GraphState:
    """Send an escalation email"""
    # print(f"state: {state}")
    send_escalation_email(
        notice_email_extract=state["notice_email_extract"],
        escalation_emails=state["escalation_emails"],
    )
    return state

def create_legal_ticket_node(state: GraphState) -> GraphState:
    """Node to create a legal ticket"""
    follow_up = create_legal_ticket(
        current_follow_ups=state.get("follow_ups"),
        notice_email_extract=state["notice_email_extract"],
    )
    state["current_follow_up"] = follow_up
    return state

# Router function:
def route_escalation_status_edge(state: GraphState) -> str:
    """Determine whether to send an escalation email or create a legal ticket"""
    if state["needs_escalation"]:
        LOGGER.info("Требуется эскалация!")
        return "send_escalation_email"

    LOGGER.info("Эскалация не требуется")
    return "create_legal_ticket"

# Add nodes:
workflow.add_node("parse_notice_message", parse_notice_message_node)
workflow.add_node("check_escalation_status", check_escalation_status_node)
workflow.add_node("send_escalation_email", send_escalation_email_node)  # alternative 1
workflow.add_node("create_legal_ticket", create_legal_ticket_node)  # alternative 2

# Add edges:
workflow.add_edge(START, "parse_notice_message")
workflow.add_edge("parse_notice_message", "check_escalation_status")
# Conditional:
workflow.add_conditional_edges(
    "check_escalation_status",
    route_escalation_status_edge,
    {
        "send_escalation_email": "send_escalation_email",
        "create_legal_ticket": "create_legal_ticket",
    },
)
workflow.add_edge("send_escalation_email", "create_legal_ticket")
workflow.add_edge("create_legal_ticket", END)

NOTICE_EXTRACTION_GRAPH = workflow.compile()

