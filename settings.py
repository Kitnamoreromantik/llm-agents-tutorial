DEBUG_MODE = False

# Path to the graph schemas:
RELATIONSHIP_SCHEMA_PATH = "../data/out/20250605_150048/ifc_relationships_schema_llm.txt"
NODES_SCHEMA_PATH = "../data/out/20250605_150048/ifc_nodes_schema_llm_short.txt"

# Prompts:
SYSTEM_PROMPT_QUERY_GENERATOR_PATH = "llm/prompts/sys_query_generator.txt"
SYSTEM_PROMPT_QUERY_EVALUATOR_PATH = "llm/prompts/sys_query_evaluator.txt"
USER_PROMPT_QUERY_EVALUATOR_PATH = "llm/prompts/usr_query_evaluator.txt"
SYSTEM_PROMPT_QUERY_INTERPRETER_PATH = "llm/prompts/sys_query_explainer.txt"
