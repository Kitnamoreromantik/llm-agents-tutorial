
from chain_notice_extraction import NOTICE_PARSER_CHAIN
from example_emails import EMAILS

res = NOTICE_PARSER_CHAIN.invoke({"message": EMAILS[0]})
print(res.content)


from chain_escalation_check import ESCALATION_CHECK_CHAIN

escalation_criteria = "В настоящее время зафиксировано наличие или вероятность протечек воды."
message = "Выявлены несколько трещин в фундаменте, а также утечки воды."
res = ESCALATION_CHECK_CHAIN.invoke({"message": message, "escalation_criteria": escalation_criteria})
print(res.content)
