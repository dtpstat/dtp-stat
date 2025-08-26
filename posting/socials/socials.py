from . import twitter
from . import telegram 
from . import vk

socials = {
    'twitter': twitter.TwitterAccount,
    'telegram': telegram.TelegramAccount,
    'vk': vk.VkAccount,
}

TYPE_CHOICES = [(key, account.full_name) for key, account in socials.items()]
CKEDITOR_CONFIGS = {account.full_name: account.ckeditor_config for _, account in socials.items()}
