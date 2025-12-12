import chainlit as cl
from agents.opener.agent import SurgicalOpenerAgent
from agents.opener.glpi_service import GLPIService
from agents.analyst.analyst_agent import GLPIAnalystAgent
from agents.opener.schemas import TicketContext

# Inicializa os agentes
opener_agent = SurgicalOpenerAgent()
analyst_agent = GLPIAnalystAgent()
glpi_service = GLPIService()

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Suporte Técnico",
            markdown_description="Abra chamados, relate problemas e solicite ajuda técnica.",
            icon="🛠️",
        ),
        cl.ChatProfile(
            name="Analista de Dados",
            markdown_description="Faça perguntas sobre os dados do GLPI (ex: 'Quantos chamados abertos?').",
            icon="📊",
        ),
    ]

@cl.on_chat_start
async def start():
    # Identifica o perfil selecionado
    chat_profile = cl.user_session.get("chat_profile")
    
    # Inicia sessão no GLPI se for suporte
    if chat_profile == "Suporte Técnico":
        cl.user_session.set("ticket_context", TicketContext(original_complaint=""))
        if glpi_service.init_session():
            print(">> Conectado ao GLPI Teste")
        else:
            print(">> Falha ao conectar no GLPI Teste")
        await cl.Message(content="Olá! Sou o Assistente de Suporte. Qual o seu problema hoje?").send()
        
    elif chat_profile == "Analista de Dados":
        await cl.Message(content="Olá! Sou o Analista de Dados do GLPI. Pergunte sobre tickets, urgências ou locais.").send()

@cl.on_message
async def main(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    
    if chat_profile == "Suporte Técnico":
        # Lógica do Opener Agent
        current_context = cl.user_session.get("ticket_context")
        updated_context = opener_agent.process_ticket(message.content, current_context=current_context)
        cl.user_session.set("ticket_context", updated_context)
        
        async with cl.Step(name="Pensamento do Agente") as step:
            step.output = updated_context.model_dump_json(indent=2)
        
        if updated_context.response_to_user:
            await cl.Message(content=updated_context.response_to_user).send()
        else:
            await cl.Message(content="... (Processando)").send()
            
        if updated_context.ready_to_submit:
            # Snapshot para evitar repetição visual
            current_snapshot = f"{updated_context.summary}|{updated_context.location}|{updated_context.urgency}|{updated_context.impact}"
            last_snapshot = cl.user_session.get("last_summary_snapshot")

            if current_snapshot != last_snapshot:
                cl.user_session.set("last_summary_snapshot", current_snapshot)
                
                resumo = (
                    f"**Resumo do Ticket**\n\n"
                    f"**Título:** {updated_context.summary}\n"
                    f"**Local:** {updated_context.location}\n"
                    f"**Urgência:** {updated_context.urgency}\n"
                    f"**Impacto:** {updated_context.impact}\n\n"
                    f"**Descrição Técnica:**\n{updated_context.description}"
                )
                actions = [
                    cl.Action(name="confirm_ticket", value="confirm", label="✅ Confirmar e Abrir Chamado", payload={})
                ]
                await cl.Message(content=resumo, actions=actions).send()
            
    elif chat_profile == "Analista de Dados":
        # Lógica do Analyst Agent
        msg = cl.Message(content="")
        await msg.send()
        
        async with cl.Step(name="Analisando Dados") as step:
            step.input = message.content
            # Executa a análise
            response = analyst_agent.run(message.content)
            step.output = f"Resposta Gerada: {response}"
            
        msg.content = response
        await msg.update()

@cl.action_callback("confirm_ticket")
async def on_action(action: cl.Action):
    ctx = cl.user_session.get("ticket_context")
    await cl.Message(content="⏳ Abrindo chamado no GLPI...").send()
    
    result = glpi_service.create_ticket(
        title=ctx.summary,
        description=ctx.description,
        location=ctx.location,
        urgency=ctx.urgency
    )
    
    if "id" in result:
        ticket_id = result.get("id")
        msg = f"✅ Chamado aberto com sucesso! **Ticket ID: {ticket_id}**"
    else:
        msg = f"❌ Erro ao abrir chamado: {result.get('error')}"
        
    await cl.Message(content=msg).send()
