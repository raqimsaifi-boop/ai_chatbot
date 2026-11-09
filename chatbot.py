
import json

from client import client
from tools import search_document
from websearchtool import web_search


# --------------------------------------------------
# 1. MODEL CONFIGURATION
# --------------------------------------------------

MODEL = "openai/gpt-oss-120b"
MAX_TOOL_ROUNDS = 3


# --------------------------------------------------
# 2. TOOL DEFINITIONS
# --------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": (
                "Search the internal knowledge base containing "
                "The Last Signal fictional series guide. "
                "Use this tool for questions about characters, "
                "episodes, locations, events, clues, and timelines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A specific question to search "
                            "within the series guide."
                        )
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the internet for external information, "
                "general knowledge, news, release dates, and "
                "other information not limited to the internal "
                "series guide. Use when external information "
                "is requested or relevant."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A clear search query describing "
                            "the information needed."
                        )
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    }
]


# --------------------------------------------------
# 3. SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are an intelligent assistant for The Last Signal,
a fictional mystery series.

You have access to two tools:

1. search_document:
   Searches the internal series guide.

2. web_search:
   Searches the internet for external information.

TOOL SELECTION RULES:

- For questions about characters, episodes, locations,
  clues, events, and timelines in The Last Signal,
  use search_document.

- For general knowledge, current information, news,
  release dates, and external information, use web_search.

- If the user explicitly requests an internet search,
  use web_search.

- Do not use web_search as a substitute for missing
  information in the internal series guide unless
  the user requests external verification.

ANSWERING RULES:

- For series-specific questions, answer only using
  retrieved information from the series guide.

- Never invent characters, events, dates, or facts.

- If the series guide does not contain the answer,
  clearly explain that the information is unavailable
  in the guide.

- Mention episode numbers whenever possible.

- For web searches, answer using the retrieved web
  information and distinguish external facts from
  information in the series guide.

- If a tool returns an error or insufficient information,
  be transparent with the user.

- Give clear, relevant, and concise answers.
"""


# --------------------------------------------------
# 4. TOOL EXECUTION FUNCTION
# --------------------------------------------------

def execute_tool(function_name, arguments):

    try:
        # Parse tool arguments
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object.")

        query = arguments.get("query")

        if not isinstance(query, str) or not query.strip():
            raise ValueError("A valid search query is required.")

        query = query.strip()

        # Execute the requested tool
        if function_name == "search_document":

            print("\n[TOOL CALLED] Searching document...")

            result = search_document(query)

        elif function_name == "web_search":

            print("\n[TOOL CALLED] Searching the web...")

            result = web_search(query)

        else:
            raise ValueError(f"Unknown tool: {function_name}")

        # Convert tool output into JSON
        return json.dumps(
            result,
            ensure_ascii=False,
            default=str
        )

    except Exception as error:

        print(f"\n[TOOL ERROR] {function_name}: {error}")

        return json.dumps({
            "error": str(error),
            "tool": function_name
        })


# --------------------------------------------------
# 5. MAIN CHATBOT FUNCTION
# --------------------------------------------------

def run_chatbot(user_question, conversation_history=None):

    # Start or restore conversation history
    if conversation_history is None:
        conversation_history = []

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(conversation_history)

    messages.append({
        "role": "user",
        "content": user_question
    })

    # Allow a maximum of 3 tool-calling rounds
    for round_number in range(MAX_TOOL_ROUNDS):

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
                max_completion_tokens=2048
            )

        except Exception as error:

            print(f"\n[API ERROR] {error}")

            return (
                "Sorry, I encountered an API error.",
                conversation_history
            )

        assistant_message = response.choices[0].message

        # ------------------------------------------
        # CASE 1: No tool call, return final answer
        # ------------------------------------------

        if not assistant_message.tool_calls:

            answer = assistant_message.content or (
                "Sorry, I could not generate an answer."
            )

            messages.append(
                assistant_message.model_dump(exclude_none=True)
            )

            # Save conversation without system prompt
            updated_history = messages[1:]

            return answer, updated_history

        # ------------------------------------------
        # CASE 2: Assistant requested tool execution
        # ------------------------------------------

        # Preserve assistant's tool-call message
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        # Execute all requested tools
        for tool_call in assistant_message.tool_calls:

            function_name = tool_call.function.name

            arguments = tool_call.function.arguments

            tool_result = execute_tool(
                function_name,
                arguments
            )

            # Send tool result back to the LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

    # ------------------------------------------
    # CASE 3: Maximum tool rounds reached
    # ------------------------------------------

    return (
        "I could not complete the answer within "
        "the allowed tool-calling rounds.",
        messages[1:]
    )


# --------------------------------------------------
# 6. CHAT INTERFACE
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 45)
    print("       THE LAST SIGNAL RAG CHATBOT")
    print("=" * 45)

    print("Type 'exit' to stop the chatbot.")

    # Maintain conversation history
    conversation_history = []

    while True:

        question = input("\nYou: ").strip()

        if not question:
            continue

        if question.lower() in ["exit", "quit", "bye"]:
            print("\nAssistant: Goodbye!")
            break

        answer, conversation_history = run_chatbot(
            question,
            conversation_history
        )

        print("\nAssistant:", answer)
