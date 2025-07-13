
import os
import json
from dotenv import load_dotenv
from livekit import api
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, AutoSubscribe
from livekit.plugins import (
    openai,
    noise_cancellation,
    silero
)

load_dotenv(dotenv_path=".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful assistant.")


async def entrypoint(ctx: agents.JobContext):

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # If a phone number was provided, then place an outbound call
    dial_info = json.loads(ctx.job.metadata)
    phone_number = dial_info["phone_number"]

    # The participant's identity can be anything you want, but this example uses the phone number itself
    sip_participant_identity = phone_number
    if phone_number is not None:
        # The outbound call will be placed after this method is executed
        try:
            await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
                # This ensures the participant joins the correct room
                room_name=ctx.room.name,

                # This is the outbound trunk ID to use (i.e. which phone number the call will come from)
                # You can get this from LiveKit CLI with `lk sip outbound list`
                sip_trunk_id=os.getenv("SIP_OUTBOUND_TRUNK_ID"),

                # The outbound phone number to dial and identity to use
                sip_call_to=phone_number,
                participant_identity=sip_participant_identity,

                # This will wait until the call is answered before returning
                wait_until_answered=True,
            ))

            print("call picked up successfully")
        except api.TwirpError as e:
            print(f"error creating SIP participant: {e.message}, "
                  f"SIP status: {e.metadata.get('sip_status_code')} "
                  f"{e.metadata.get('sip_status')}")
            ctx.shutdown()

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],

        # Use the LiveKit Cloud plugins for STT, TTS, and LLM
        # You can also use your own plugins e.g. groq, gemini, etc.
        stt=openai.STT(),

        llm=openai.LLM(model="gpt-4o-mini"), 
        
        tts=openai.TTS()
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            # - For other applications, use `BVC` for best results
            noise_cancellation=noise_cancellation.BVCTelephony()
        ),
    )

    if phone_number is not None:
        await session.generate_reply(
            instructions=f"Hello. How can I assist you today?"
        )            

def prewarm(proc: agents.JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="my-telephony-agent",
        prewarm_fnc=prewarm
        ))