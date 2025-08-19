from . import twitter
from . import telegram 
from . import vk

socials = {
    'twitter': twitter.TwitterAccount,
    'telegram': telegram.TelegramAccount,
    'vk': vk.VkAccount,
}

TYPE_CHOICES = [(key, service.name) for key, service in socials.items()]
