import httpx
import uuid
import time

thread_id = str(uuid.uuid4())


def stream_chat(payload):
    print(f"\n--- Sending Payload: {payload} ---")
    with httpx.stream(
        "POST", "http://127.0.0.1:8000/chat", json=payload, timeout=60.0
    ) as r:
        for line in r.iter_lines():
            if line.startswith("event: "):
                print(f"[{line[7:]}]", end=" ")
            elif line.startswith("data: "):
                print(line[6:])


# 1. Ask to book an appointment
print("Step 1: Asking to book an appointment...")
stream_chat(
    {
        "thread_id": thread_id,
        "message": "I want to book a lab appointment for 2026-09-27 10:00.",
    }
)

print(
    "\n(Notice how the stream ended with a 'human_prompt' event asking for the center name!)"
)
time.sleep(2)

# 2. Provide the center name to resume the graph
print("\nStep 2: Resuming graph with the center name...")
stream_chat({"thread_id": thread_id, "center_name": "Downtown Medical Plaza"})

print(
    "\n(Notice how the graph instantly resumed, made the tool call, and returned the verbatim confirmation!)"
)
time.sleep(2)

# 3. Ask a medical guidelines question to verify retrieval
print("\nStep 3: Asking a clinical question to verify retrieval...")
stream_chat(
    {
        "thread_id": str(uuid.uuid4()),
        "message": "What are the fasting rules for an abdominal ultrasound?",
    }
)

print(
    "\n(Notice how the assistant queries the retriever tool and streams the clinical guidelines!)"
)
