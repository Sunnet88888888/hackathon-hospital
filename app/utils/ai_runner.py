import os


os.environ["OPENAI_API_KEY"] = "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"

from agents import Agent, Runner
from agents.mcp import MCPServerSse

async def ai_runner(user_token: str, context):
   
    token = user_token
    
    # 1. Объявляем конфигурацию сервера
    mcp_server = MCPServerSse(
        params={
            "url": "http://127.0.0.1:8000/mcp", 
            "headers": {
                "Authorization": f"Bearer {token}"
            }
        }
    )

    # 2. Инициализируем сервер через контекстный менеджер `async with`
    # Это решает проблему "Server not initialized"
    async with mcp_server as server:
        
        # 3. Передаем запущенный сервер агенту
        agent = Agent(
            name="FastAPI Integrator Agent",
            model="gpt-4o", 
            instructions="Ты ассистент, использующий инструменты нашего бэкенда на FastAPI.",
            mcp_servers=[server]
        )
        context=context
        user_message = context.get("user_message", "Привет, как дела?")
        print(f"Пользователь: {user_message}\n")

        # 4. Запускаем диалог
        result = await Runner.run(agent, user_message, context=context)

        print(f"Агент: {result.final_output}")
        return result.final_output


