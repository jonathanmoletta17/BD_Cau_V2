from agents.opener.fsm_standalone import TicketFSM, TicketContext

fsm = TicketFSM()
ctx = TicketContext(original_complaint="Minha senha está bloqueada")
print(f"Initial CTX Location: {ctx.location}")

msg1 = "Estou na sala 202"
print(f"Processing Msg: '{msg1}'")

# Debug Extract Location directly
extracted = fsm._extract_location(msg1)
print(f"Direct Extract Result: {repr(extracted)}")

# Run Process
ctx = fsm.process_input(ctx, msg1)
print(f"Final CTX Location: {repr(ctx.location)}")
