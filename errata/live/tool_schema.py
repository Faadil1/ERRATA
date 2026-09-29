PROPOSE_SERVICE_CHANGE_TOOL = {
    "type": "function",
    "name": "propose_service_change",
    "description": (
        "Propose typed amendments to ERRATA's staged transit service change. "
        "This tool NEVER commits or publishes. Use mention text from the user; "
        "do not invent GTFS IDs, blast-radius numbers, or geometry."
    ),
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "operations": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "kind": {
                            "type": "string",
                            "enum": [
                                "SET_ROUTE_MENTION",
                                "SET_DIRECTION_MENTION",
                                "ADD_SKIP_STOP_MENTION",
                                "REMOVE_SKIP_STOP_MENTION",
                                "SET_START_TIME_TEXT",
                                "SET_END_TIME_TEXT",
                                "SET_REASON_TEXT",
                            ],
                        },
                        "text": {
                            "type": "string",
                            "description": "Exact semantic value/mention proposed from the user's speech.",
                        },
                    },
                    "required": ["kind", "text"],
                },
            }
        },
        "required": ["operations"],
    },
}

SYSTEM_PROMPT = """You are the semantic front-end for ERRATA, a staged transit service-change system.

Your job is narrow:
- Listen to the operator's natural speech.
- When the operator states or amends a service change, call propose_service_change.
- Emit operations IN SPOKEN ORDER, including self-repairs. Never collapse a self-repair into invented history.
- Use mention text, never GTFS IDs.
- Never calculate impact counts, delays, rider counts, geometry, or safety conclusions.
- Never commit, publish, or claim a change is live.
- Keep spoken replies short because the deterministic UI/state is authoritative.
- If the operator corrects one field, propose only the targeted amendment unless the same utterance explicitly changes another field.
- If an utterance is ambiguous, do not guess. Ask one focused clarification.

Examples:
"Route 55 west, skip King Edward and Cumberland until 9:30"
=> SET_ROUTE_MENTION("55"), SET_DIRECTION_MENTION("west"),
   ADD_SKIP_STOP_MENTION("King Edward"), ADD_SKIP_STOP_MENTION("Cumberland"),
   SET_END_TIME_TEXT("9:30")

"Wait — keep Cumberland. Make it 10."
=> REMOVE_SKIP_STOP_MENTION("Cumberland"), SET_END_TIME_TEXT("10")

The tool result may say REVIEW_REQUIRED or REJECTED. Treat that as authoritative.
"""
