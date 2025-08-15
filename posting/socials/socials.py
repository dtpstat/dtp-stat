from . import twitter
from . import telegram 
from . import vk

socials = {
    'twitter': twitter.TwitterService,
    'telegram': telegram.TelegramService,
    'vk': vk.VkService,
}

TYPE_CHOICES = [(key, service.name) for key, service in socials.items()]
