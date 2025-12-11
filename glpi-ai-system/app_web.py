import chainlit as cl
from agents.opener.agent import SurgicalOpenerAgent
from agents.opener.glpi_service import GLPIService
from agents.opener.schemas import TicketContext

# Inicializa o agente e o serviço
agent = SurgicalOpenerAgent()
glpi_service = GLPIService()

@cl.on_chat_start
async def start():
    # Inicializa o contexto vazio na sessão
    cl.user_session.set("ticket_context", TicketContext(original_complaint=""))
    
    # Inicia sessão no GLPI (Lazy load ou startup)
    if glpi_service.init_session():
        print(">> Conectado ao GLPI Teste")
    else:
        print(">> Falha ao conectar no GLPI Teste")
        
    await cl.Message(content="Olá! Sou o Assistente de Suporte. Qual o seu problema hoje?").send()

@cl.on_message
async def main(message: cl.Message):
    # Recupera o contexto atual
    current_context = cl.user_session.get("ticket_context")
    
    # Processa a mensagem usando o agente
    updated_context = agent.process_ticket(message.content)
    
    # Atualiza a sessão
    cl.user_session.set("ticket_context", updated_context)
    
    # Mostra o pensamento (JSON) em um elemento expansível para debug
    async with cl.Step(name="Pensamento do Agente") as step:
        step.output = updated_context.model_dump_json(indent=2)
    
    # Resposta ao usuário
    if updated_context.response_to_user:
        await cl.Message(content=updated_context.response_to_user).send()
    
    # Se estiver pronto, encerra ou mostra ação final
    if updated_context.ready_to_submit:
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
