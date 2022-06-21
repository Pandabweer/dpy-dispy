from log import log
from constants import config

from typing import Literal

from discord import Client

together_apps = {
    "Watch Together": "880218394199220334",
    "Sketch Heads": "902271654783242291",
    "Word Snacks": "879863976006127627",

    "Poker Night (Requires boost level 1)": "755827207812677713",
    "Chess In The Park (Requires boost level 1)": "832012774040141894",
    "Checkers In The Park (Requires boost level 1)": "832013003968348200",
    "Letter League (Requires boost level 1)": "879863686565621790",
    "SpellCast (Requires boost level 1)": "852509694341283871",
    "Blazing 8s (Requires boost level 1)": "832025144389533716",
    "Bobble League (Requires boost level 1)": "947957217959759964",
    "Land-io (Requires boost level 1)": "903769130790969345",

    "Awkword (Requires special privilages)": "879863881349087252",
    "Poker Night Dev (Requires special privilages)": "763133495793942528",
    "Watch Together Dev (Requires special privilages)": "880218832743055411",
    "Chess In The Park Dev (Requires special privilages)": "832012586023256104"
}

together_choices = Literal[
    "Watch Together", "Sketch Heads", "Word Snacks",

    "Poker Night (Requires boost level 1)",
    "Chess In The Park (Requires boost level 1)",
    "Checkers In The Park (Requires boost level 1)",
    "Letter League (Requires boost level 1)",
    "SpellCast (Requires boost level 1)",
    "Blazing 8s (Requires boost level 1)",
    "Bobble League (Requires boost level 1)",
    "Land-io (Requires boost level 1)",

    "Awkword (Requires special privilages)",
    "Poker Night Dev (Requires special privilages)",
    "Watch Together Dev (Requires special privilages)",
    "Chess In The Park Dev (Requires special privilages)"
]


async def create_together_url(client: Client, voice_channel_id: int, app_id: str) -> str:
    data = {
        'max_age': 0,
        'max_uses': 0,
        'target_application_id': app_id,
        'target_type': 2,
        'temporary': False,
        'validate': None
    }

    async with client.http_session.post(
            f"https://discord.com/api/v8/channels/{voice_channel_id}/invites", json=data,
            headers={'Authorization': f'Bot {config.bot.token}', 'Content-Type': 'application/json'}
    ) as resp:
        resp_code = resp.status
        result = await resp.json()

    if resp_code == 429:
        log.warn("I'm getting rate limited smh")
        return "I could not create an activity right now, please try again later."
    elif resp_code == 401 or resp_code == 403:
        log.warn("Authorization header is missing or invalid, check the token")
        return "I can't create an activity right now."

    elif result['code'] == 10003 or (result['code'] == 50035 and 'channel_id' in result['errors']):
        log.debug("Someone passed an invalid voice channel id")
        return "Invalid channel id, did you pass a voice channel?"
    elif result['code'] == 50013:
        log.debug("Missing CREATE_INSTANT_INVITE permissions for that voice channel")
        return "I don't have permission to create and invite in that voice channel."
    elif result['code'] == 130000:
        log.warn("API is overloaded")
        return "I could not create an activity right now, please try again later."

    return f"[Click me ONCE](https://discord.gg/{result['code']} 'Activity url')"
