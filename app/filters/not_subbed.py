from aiogram.filters import Filter


class NotSubbed(Filter):
    """
    Check if user is subbed
    """
    
    async def __call__(self, _, sponsors: list) -> bool:

        return bool(sponsors)
