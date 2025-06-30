
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
# with open("notice_extraction_graph.png", "wb") as f:
#     f.write(image_data)



from graph_notice_extraction import NOTICE_EXTRACTION_GRAPH
from example_emails import EMAILS
import json
import re
# Initialization:
initial_state = {
    "notice_message": EMAILS[0],
    "notice_email_extract": None,
    "escalation_text_criteria": "Существует риск пожара или протечек.",
    "escalation_money_criteria": 100_000,
    "needs_escalation": False,
    "escalation_emails": ["brog@abc.ru", "bigceo@company.ru"],
}
# Result:
final_state = NOTICE_EXTRACTION_GRAPH.invoke(initial_state)
# Prints:
match = re.search(r"```json\n(.*?)\n```", final_state["notice_email_extract"].content, re.DOTALL)
json_str = match.group(1)
parsed = json.loads(json_str)
print(f"notice_email_extract: {json.dumps(parsed, indent=2, ensure_ascii=False)}\n")
print(f"Need of escalation: {final_state["needs_escalation"]}\n")
print(f"Response metadata: {json.dumps(final_state["notice_email_extract"].response_metadata, indent=2, ensure_ascii=False)}\n")

