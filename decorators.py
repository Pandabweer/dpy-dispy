from discord import Interaction


def is_bot_owner(interaction: Interaction) -> bool:
    return interaction.user.id == interaction.client.owner_id
