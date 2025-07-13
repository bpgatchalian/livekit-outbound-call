# LiveKit Outbound Caller

Create a environment and install require packages.
```
python -m venv venv
venv/scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python agent.py download-files
```

Required environment environment variables
```
LIVEKIT_URL=YOUR_LIVEKIT_URL_HERE
LIVEKIT_API_KEY=YOUR_LIVEKIT_API_KEY_HERE
LIVEKIT_API_SECRET=YOUR_LIVEKIT_API_SECRET_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
SIP_OUTBOUND_TRUNK_ID=YOUR_SIP_OUTBOUND_TRUNK_ID_HERE
```
to create the SIP_OUTBOUND_TRUNK_ID follow this guide [SIP trunk setup](https://docs.livekit.io/sip/quickstarts/configuring-sip-trunk/)

Run the ai agent
```
python agent.py dev
```

Dispatch an agent
```python

import os
import asyncio
from livekit import api
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")

async def main():
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )

    created_dispatch = await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="my-telephony-agent",
            room="outbound-call-room-1234",
            metadata='{"phone_number": "+1234567890"}'
        )
    )
    print(f"Created agent dispatch: {created_dispatch.id}")


if __name__ == "__main__":
    asyncio.run(main())

```