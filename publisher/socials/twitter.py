import re, copy, os, tempfile, urllib
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
            img_match = re.search(r'<img [^>]*src="([^"]+)"[^>]*>', t)
            image_src = img_match.group(1) if img_match else None
            # Удаляем тег <img>
            t = re.sub(r'<img [^>]*>', '', t)

            # 3. Убираем <div class="tweet-char-counter">...</div>
            t = re.sub(r'<div class="tweet-char-counter">.*?</div>', '', t, flags=re.DOTALL)
            
            # 4. Убираем <span class="tweet-numbering">...</span>
            t = re.sub(r'<span class="tweet-numbering">.*?</span>', '', t, flags=re.DOTALL)
            
            # 5. Убираем <span class="tweet-arrow">, оставляя текст
            t = re.sub(r'<span class="tweet-arrow">', '', t)
            t = re.sub(r'</span>', '', t)
            
            # 6. Убираем <p> и <br>
            t = re.sub(r'</?p>', '', t)
            t = re.sub(r'<br\s*/?>', '\n', t)
        
            t = t.strip()
            if t:  # пропускаем пустые твиты
                clean_tweets.append((t, image_src))
            
        return clean_tweets
    
    def post(self, post):
        self.log_template = f"[{self.full_name}: {post.account.title}][{post.short}]" + " {0}"

        client = tweepy.Client(
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret
        )
        
        clean_tweets = self.clean_publish_data(post.content)
        
        last_tweet_id = None
        
        for content, photo_src in clean_tweets:
            if photo_src:
                # Скачиваем изображение, если это URL
                if photo_src.startswith('http'):
                    try:
                        tmp = tempfile.NamedTemporaryFile(delete=False)
                        urllib.request.urlretrieve(photo_src, tmp.name)
                        photo_src = tmp.name
                    except Exception as e:
                        return self.error(f"Ошибка при скачивании изображения: {e}")
                    
                # Загрузка фото
                try:
                    media = client.media_upload(photo_src)
                except Exception as e:
                    return self.error(f"Ошибка при загрузке изображения: {e}")
                finally:
                    # Удаляем временный файл
                    if tmp and os.path.exists(tmp.name):
                        os.remove(tmp.name)
                
                # Отправка твита с фото
                try:
                    resp = client.create_tweet(text=content, media_ids=[media.media_id], in_reply_to_status_id=last_tweet_id, auto_populate_reply_metadata=True)
                except Exception as e:
                    return self.error(f"Ошибка при отправке твита с фото: {e}")
                
            else:
                # Отправка твита без фото
                try:
                    resp = client.create_tweet(text=content, in_reply_to_status_id=last_tweet_id, auto_populate_reply_metadata=True)
                except Exception as e:
                    return self.error(f"Ошибка при отправке твита: {e}")
                
            # сохраняем ID последнего твита для цепочки
            last_tweet_id = resp.data.get('id')
            
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
