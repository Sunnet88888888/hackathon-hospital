import os

from agents import Agent, Runner
from agents.mcp import MCPServerSse

from app.config import settings


async def ai_runner(user_token: str, context: list[dict[str, str]]) -> str:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OpenAI API key is not configured.")
    if not context:
        raise ValueError("Conversation context must contain at least one message.")

    os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY)
    history = "\n".join(
        f"{('Пользователь' if message['role'] == 'user' else 'Ассистент')}: {message['content']}"
        for message in context[:-1]
    )
    latest_message = context[-1]["content"]
    agent_input = (
        f"История разговора:\n{history}\n\nНовое сообщение пользователя:\n{latest_message}"
        if history
        else latest_message
    )

    mcp_server = MCPServerSse(
        params={
            "url": settings.MCP_SERVER_URL,
            "headers": {
                "Authorization": f"Bearer {user_token}"
            },
        }
    )

    async with mcp_server as server:
        agent = Agent(
            name="FastAPI Integrator Agent",
            model="gpt-4o",
            instructions="""You are a healthcare AI assistant. 
            Help the user with their requests clearly and accurately. Use available MCP tools whenever the user's request requires information or an action in the healthcare system. Never invent information or claim an action was completed unless the corresponding tool successfully completed it.

Use the conversation history to understand context and avoid unnecessary questions.

Protect user privacy and only access information necessary for the request.

For medical questions, provide general information and recommend consulting a healthcare professional when appropriate. In emergencies, advise seeking urgent medical care.

Keep responses concise, clear, and professional. """,
            mcp_servers=[server],
        )
        result = await Runner.run(agent, agent_input)
        return str(result.final_output)


