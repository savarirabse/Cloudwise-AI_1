from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import urllib.request
import urllib.error
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.cloudprofile import UserCloudProfile

router = APIRouter(
    prefix="/api/copilot",
    tags=["Cloud Copilot"]
)
security = HTTPBearer()
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "llama3.1:8b"
class ChatMessage(BaseModel):
    role: str
    content: str
class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
SYSTEM_PROMPT = """
You are Cloudwise AI, an AI cloud advisory assistant.

Your ONLY domain is cloud technology and closely related
professional technical topics.

You can answer questions about:

- AWS
- Microsoft Azure
- Google Cloud Platform (GCP)
- Cloud architecture
- Cloud migration
- Cloud readiness
- Cloud cost optimization
- Cloud security
- Compliance
- Reliability
- Disaster recovery
- Cloud networking
- Databases in the cloud
- Kubernetes
- Containers
- DevOps
- Infrastructure
- Cloud monitoring
- Cloud performance
- Cloud governance
- Cloud operations

IMPORTANT RULES:

1. Only answer questions related to cloud computing or closely
   related technical topics.
2. If the user asks something unrelated to cloud technology,
   politely explain that you are Cloudwise AI and specialize
   in cloud technology.
3. Do not pretend that you have access to the user's AWS, Azure,
   or GCP environment unless actual cloud data has been provided.
4. Do not invent cloud resources, costs, configurations,
   security findings, or metrics.
5. If you are uncertain, clearly say that you are uncertain.
6. Give practical and technically useful answers.
7. Use headings, bullet points, steps, or examples when they
   improve clarity.
8. Use the user's cloud profile when it is relevant.
9. Answer only what is necessary to fully answer the question.
10. Keep responses concise and focused.
11. Do not provide unnecessary background, repetition, or filler.
12. For simple questions, give a short direct answer.
13. For technical questions, provide the key explanation and
    the most relevant steps or examples.
14. Prefer 3-7 bullet points when a list is appropriate.
15. Do not repeat the user's question.
16. Do not say things like "I hope this helps."
17. Always complete the answer before stopping.
18. Stop generating once the question has been completely answered.
19. Maintain context from previous messages.
20. If the user asks a follow-up question such as:
    "what about its benefits?"
    "how does it work?"
    "what about Azure?"
    or
    "explain that further"
    use the previous conversation context to understand
    what the user is referring to.
21. Do not restart the explanation unnecessarily when the
    previous conversation already provides the context.
22. If the previous conversation contains a technical term,
    service, architecture, or cloud platform that the user
    refers to using words such as "it", "this", "that",
    "its", or "they", resolve the reference using the
    conversation history.
You are Cloudwise AI, not a general-purpose personal assistant.
"""
def call_ollama_stream(
    message: str,
    history: list[ChatMessage],
    profile_context: str
):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]
    for item in history:
        if item.role not in ["user", "assistant"]:
            continue
        if not item.content.strip():
            continue
        messages.append(
            {
                "role": item.role,
                "content": item.content
            }
        )
    current_message = f"""
{profile_context}
CURRENT USER QUESTION:
{message}
"""
    messages.append(
        {
            "role": "user",
            "content": current_message
        }
    )
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
        "options": {
            "num_predict": 600
        }
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/x-ndjson"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=300
        ) as response:
            for line in response:
                line = line.decode(
                    "utf-8"
                ).strip()
                if not line:
                    continue
                result = json.loads(line)
                if "message" in result:
                    content = result[
                        "message"
                    ].get(
                        "content",
                        ""
                    )
                    if content:
                        yield content
                if result.get("done") is True:
                    break
    except urllib.error.HTTPError as error:
        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )
        print(
            "OLLAMA HTTP ERROR:",
            error.code
        )
        print(
            "OLLAMA ERROR BODY:",
            error_body
        )
        raise RuntimeError(
            f"Ollama returned HTTP {error.code}: "
            f"{error_body}"
        )
    except urllib.error.URLError as error:
        print(
            "OLLAMA CONNECTION ERROR:",
            error
        )
        raise RuntimeError(
            f"Unable to connect to Ollama: {error}"
        )
    except Exception as error:
        print(
            "OLLAMA STREAM ERROR:",
            repr(error)
        )
        raise RuntimeError(
            f"Ollama request failed: {error}"
        )
@router.post("/chat")
def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db)
):
    try:
        user_id = decode_access_token(
            credentials.credentials
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    profile = (
        db.query(UserCloudProfile)
        .filter(
            UserCloudProfile.user_id == user.id
        )
        .first()
    )
    profile_context = ""
    if profile:
        try:
            cloud_platforms = json.loads(
                profile.cloud_platforms
            )
        except Exception:
            cloud_platforms = (
                profile.cloud_platforms
            )
        try:
            goals = json.loads(
                profile.goals
            )
        except Exception:
            goals = profile.goals
        profile_context = f"""
USER CLOUD PROFILE:
Organization:
{profile.organization_name}
Industry:
{profile.industry}
Organization Size:
{profile.organization_size}
Cloud Platforms:
{cloud_platforms}
Current Cloud Usage:
{profile.cloud_usage}
Cloud Goals:
{goals}
"""
    def generate_response():
        try:
            for chunk in call_ollama_stream(
                message=message,
                history=request.history,
                profile_context=profile_context
            ):
                yield chunk
        except RuntimeError as error:
            print(
                "Cloud Copilot streaming error:",
                error
            )
            yield (
                "\n\n[Cloudwise AI Error] "
                + str(error)
            )
        except Exception as error:
            print(
                "Unexpected Cloud Copilot error:",
                error
            )
            yield (
                "\n\n[Cloudwise AI Error] "
                "Unable to generate a response."
            )
    return StreamingResponse(
        generate_response(),
        media_type="text/plain; charset=utf-8"
    )