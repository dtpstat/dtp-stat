import re, copy, os, tempfile, urllib.request
from django import forms
from django.db import models
from django.contrib import admin
from django_cryptography.fields import encrypt
from .base import SocialNetworkBase, SocialNetworkAdminBase, HiddenModelAdmin

import tweepy

class TwitterAccount(SocialNetworkBase):
    full_name = 'Twitter'
    
    consumer_key = encrypt(models.CharField(max_length=255))
    consumer_secret = encrypt(models.CharField(max_length=255))
    access_token = encrypt(models.CharField(max_length=255))
    access_token_secret = encrypt(models.CharField(max_length=255))
    
    ckeditor_config = copy.deepcopy(SocialNetworkBase.ckeditor_config)
    ckeditor_config['toolbar'].append([
        'Image', '-',
        'SpecialChar', 'EmojiPanel', '-',
        'RemoveFormat', '-',
        'TweetSplitter',
    ])
    ckeditor_config['allowedContent'] = (
        'img[!src,alt,width,height];'               # изображения
        'div[*]{*}(tweet-*); span[*]{*}(tweet-*);'  # твиты
        'a[!href];'                                 # твиттер-ссылки
    )
    ckeditor_config['extraPlugins'] += ',tweet_splitter'
    
    def clean_publish_data(self, content):
        
        # 1. Разбиваем на твиты
        tweets = re.split(r'<div class="tweet-separator">.*?</div>', content, flags=re.DOTALL)

        clean_tweets = []
        
        for t in tweets:
            # 2. Находим <img> и сохраняем src
            img_match = re.search(r'<img\s+[^>]*?\bsrc="([^"]+)"[^>]*?>', t)
            image_src = img_match.group(1) if img_match else None
            # Удаляем тег <img>
            t = re.sub(r'<img\s+[^>]*?>', '', t)
            # 3. Убираем <div class="tweet-char-counter">...</div>
            t = re.sub(r'<div class="tweet-char-counter">.*?</div>', '', t, flags=re.DOTALL)
            
            # 4. Убираем <span class="tweet-numbering">...</span>
            t = re.sub(r'<span class="tweet-numbering">.*?</span>', '', t, flags=re.DOTALL)
            
            # 5. Убираем <span class="tweet-arrow">, оставляя текст
            t = re.sub(r'<span class="tweet-arrow">(.*?)</span>', r'\1', t, flags=re.DOTALL)
            
            # 6. Убираем <p> и <br>
            t = re.sub(r'</?p>', '', t)
            t = re.sub(r'<br\s*/?>', '\n', t)
        
            t = t.strip()
            if t:  # пропускаем пустые твиты
                clean_tweets.append((t, image_src))
            
        return clean_tweets
    
    def post(self, post):
        self.log_template = f"[{self.full_name}: {post.account.title}][{post.short}]" + " {0}"

        # v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(
            self.consumer_key, self.consumer_secret,
            self.access_token, self.access_token_secret
        )
        api_v1 = tweepy.API(auth)
        
        # v2 Client for tweet/thread creation
        client = tweepy.Client(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )
        
        clean_tweets = self.clean_publish_data(post.content)
        
        last_tweet_id = None
        
        for content, photo_src in clean_tweets:
            tmp_path = None
            try:
                media_ids = None
                if photo_src:
                    
                    # Скачиваем изображение, если это URL
                    if photo_src.startswith('http'):
                        try:
                            tmp = tempfile.NamedTemporaryFile(delete=False)
                            urllib.request.urlretrieve(photo_src, tmp.name)
                            tmp_path = tmp.name
                            tmp.close()
                            local_path = tmp_path
                        except Exception as e:
                            return self.error(f"Ошибка при скачивании изображения: {e}")
                    else:
                        local_path = photo_src
                        
                    # Загрузка фото (v1.1)
                    try:
                        media = api_v1.media_upload(local_path)
                        media_id = getattr(media, "media_id_string", None) or str(media.media_id)
                        media_ids = [media_id]
                    except Exception as e:
                        return self.error(f"Ошибка при загрузке изображения: {e}")

                # Отправка твита (с фото или без)
                try:
                    params = {}
                    if media_ids:
                        params["media"] = {"media_ids": media_ids}
                    if last_tweet_id:
                        params["reply"] = {"in_reply_to_tweet_id": last_tweet_id}
                    resp = client.create_tweet(text=content, **params)
                except Exception as e:
                    return self.error(f"Ошибка при отправке твита: {e}")
                # сохраняем ID последнего твита для цепочки
                last_tweet_id = resp.data.get("id")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
    
        return self.log("Твит:ы успешно отправлен:ы")

class TwitterAccountForm(forms.ModelForm):
    class Meta:
        model = TwitterAccount
        fields = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']
        widgets = {
            'consumer_key': forms.PasswordInput(render_value=False),
            'consumer_secret': forms.PasswordInput(render_value=False),
            'access_token': forms.PasswordInput(render_value=False),
            'access_token_secret': forms.PasswordInput(render_value=False),
        }

class TwitterAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    name = 'twitter'
    
admin.site.register(TwitterAccount, TwitterAccountAdmin)
