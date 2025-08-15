from posting.accounts.networks import telegram, twitter, vk 

SOCIALS = {
    **telegram.telegram, **twitter.twitter, **vk.vk
    # Добавляй новые соцсети сюда
}

TYPE_CHOICES = [(key, social.verbose_name) for key, social in SOCIALS.items()]

def get_social_network(type_name):
    try:
        return SOCIALS[type_name]
    except KeyError:
        raise ValueError(f"Unknown social network type: {type_name}")