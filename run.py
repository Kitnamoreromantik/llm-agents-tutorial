
# from chain_notice_extraction import NOTICE_PARSER_CHAIN
# from example_emails import EMAILS

# res = NOTICE_PARSER_CHAIN.invoke({"message": EMAILS[0]})
# print(res.content)




# from chain_escalation_check import ESCALATION_CHECK_CHAIN

# escalation_criteria = "В настоящее время зафиксировано наличие или вероятность протечек воды."
# message = "Выявлены несколько трещин в фундаменте, а также утечки воды."
# res = ESCALATION_CHECK_CHAIN.invoke({"message": message, "escalation_criteria": escalation_criteria})
# print(res.content)




# from graph_notice_extraction import NOTICE_EXTRACTION_GRAPH
# image_data = NOTICE_EXTRACTION_GRAPH.get_graph().draw_mermaid_png()
# # Save the workflow visualization to a PNG file:
# with open("notice_extraction_conditional_graph.png", "wb") as f:
#     f.write(image_data)

# from example_emails import EMAILS
# import json
# import re
# # Initialization:
# initial_state_no_escalation = {
#     "notice_message": EMAILS[0],
#     "notice_email_extract": None,
#     "escalation_text_criteria": "Существует риск пожара или протечек.",
#     "escalation_money_criteria": 10_000_000,
#     "needs_escalation": False,
#     "escalation_emails": ["brog@abc.ru", "bigceo@company.ru"],
# }

# initial_state_escalation = {
#     "notice_message": EMAILS[0],
#     "notice_email_extract": None,
#     "escalation_text_criteria": "Работники нарушают правила безопасности.",
#     "escalation_money_criteria": 10_000_000,
#     "needs_escalation": False,
#     "escalation_emails": ["brog@abc.ru", "bigceo@company.ru"],
# }

# # Result:
# no_esc_result = NOTICE_EXTRACTION_GRAPH.invoke(initial_state_no_escalation)
# print(f"Need of escalation: {no_esc_result["needs_escalation"]}\n")

# no_esc_result = NOTICE_EXTRACTION_GRAPH.invoke(initial_state_escalation)
# print(f"Need of escalation: {no_esc_result["needs_escalation"]}\n")

# # Prints:
# match = re.search(r"```json\n(.*?)\n```", final_state["notice_email_extract"].content, re.DOTALL)
# json_str = match.group(1)
# parsed = json.loads(json_str)
# print(f"notice_email_extract: {json.dumps(parsed, indent=2, ensure_ascii=False)}\n")

# print(f"Response metadata: {json.dumps(final_state["notice_email_extract"].response_metadata, indent=2, ensure_ascii=False)}\n")



from email_agent import email_agent_graph
from example_emails import EMAILS

image_data = email_agent_graph.get_graph().draw_mermaid_png()
# Save the workflow visualization to a PNG file:
with open("email_graph.png", "wb") as f:
    f.write(image_data)

message_1 = {"messages": [("human", EMAILS[0])]}
for chunk in email_agent_graph.stream(message_1, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
