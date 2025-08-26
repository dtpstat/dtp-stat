CKEDITOR.plugins.add('tweet_splitter', {
    icons: 'tweet_splitter',
    init: function(editor) {
        editor.addContentsCss(this.path + 'styles.css');

        editor.addCommand('insertTweetSplitter', {
            exec: function(editor) {
                const separator = CKEDITOR.dom.element.createFromHtml(
                    `<div class="tweet-separator" contenteditable="false">
                        <span class="tweet-separator-line"></span>
                        <span class="tweet-separator-text">Новый твит 
                            <span class="tweet-separator-remove" title="Объединить твиты">
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 4L4 12M4 4L12 12" stroke="#666" stroke-width="2" stroke-linecap="round"/>
                                </svg>
                            </span>
                        </span>
                        <span class="tweet-separator-line"></span>
                    </div>`
                );
                editor.insertElement(separator);
                setTimeout(() => updateTweetCounters(editor), 100);

                const editorDom = editor.document.$;
                editorDom.querySelectorAll('.tweet-separator-remove').forEach(button => {
                    button.onclick = function() {
                        const separator = button.closest('.tweet-separator');
                        if (separator) {
                            separator.remove();
                            setTimeout(() => updateTweetCounters(editor), 100);
                            editor.focus();
                        }
                    };
                });
            }
        });

        editor.ui.addButton('TweetSplitter', {
            label: 'Разбить на твиты',
            command: 'insertTweetSplitter',
            toolbar: 'insert',
            icon: 'horizontalrule',
        });

        editor.on('instanceReady', function() {
            updateTweetCounters(editor);
        });

        editor.on('key', function() {
            setTimeout(() => updateTweetCounters(editor), 100);
        });

        editor.on('afterCommandExec', function() {
            setTimeout(() => updateTweetCounters(editor), 100);
        });
        editor.on('contentDom', function() {
            editor.document.on('copy', function(evt) {
                const e = evt.data.$; // нативный ClipboardEvent
                e.preventDefault(); // отменяем стандартное копирование

                let html = editor.getSelectedHtml(true);;

                // Удаляем div tweet-separator и tweet-char-counter целиком
                html = html.replace(/<div class="tweet-(separator|char-counter)[^>]*>[\s\S]*?<\/div>/g, '');

                // Убираем все теги, оставляем только текст
                let text = html.replace(/<[^>]+>/g, '');

                // Кладём своё
                e.clipboardData.setData('text/plain', text);
                e.clipboardData.setData('text/html', text);
            });
        });
    }
});



const TWEET_LIMIT = 280;

function twitterLength(text) {
    if (!text) return 0;

    // Заменяем http/https ссылки и bare domains на 23 символа
    const urlRegex = /\b((https?:\/\/[^\s]+)|([a-z0-9.-]+\.[a-z]{2,})(\/[^\s]*)?)/gi;
    text = text.replace(urlRegex, 'x'.repeat(23));

    // Эмодзи считаем за 2 символа
    const emojiRegex = /[\p{Emoji_Presentation}\p{Emoji}\u200d]/gu;
    text = text.replace(emojiRegex, 'xx');

    return text.length;
}

document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function(e) {
            // Берём первый доступный CKEditor (или пробегаем все, если их несколько)
            for (let instanceName in CKEDITOR.instances) {
                const editor = CKEDITOR.instances[instanceName];
                if (!validateTweets(editor)) {
                    e.preventDefault(); // блокируем отправку
                    alert("❌ Нельзя сохранить: один или несколько твитов превышают 280 символов!");
                    return false; // выходим из цикла, форма не отправляется
                }
            }
        });
    });

function validateTweets(editor) {
    const editorData = editor.getData();
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = editorData;

    const nodes = Array.from(tempDiv.childNodes);
    let currentTweet = [];
    const tweets = [];

    nodes.forEach(node => {
        if (node.className === 'tweet-separator') {
            tweets.push(currentTweet);
            currentTweet = [];
        } else {
            currentTweet.push(node);
        }
    });
    if (currentTweet.length) tweets.push(currentTweet);

    // Проверяем длину
    for (let tweet of tweets) {
        const div = document.createElement('div');
        tweet.forEach(n => div.appendChild(n.cloneNode(true)));
        const text = div.textContent || div.innerText || '';
        if (twitterLength(text.trim()) > TWEET_LIMIT) {
            return false;
        }
    }
    return true;
}

function updateTweetCounters(editor) {
    const editorDom = editor.document.$;
    // Удаляем старые элементы
    editorDom.querySelectorAll('.tweet-numbering, .tweet-arrow, .tweet-char-counter').forEach(el => el.remove());

    const content = editor.getData();
    const tweetsHtml = content.split(/<div class="tweet-separator".*?\/div>/g);
    const separators = editorDom.querySelectorAll('.tweet-separator');

    // Собираем все узлы редактора
    let nodes = Array.from(editorDom.body.childNodes);
    let tweetNodes = [];
    let currentTweet = [];

    // Разделяем узлы на твиты
    nodes.forEach(node => {
        if (node.className === 'tweet-separator') {
            if (currentTweet.length) {
                tweetNodes.push(currentTweet);
                currentTweet = [];
            }
        } else {
            currentTweet.push(node);
        }
    });
    if (currentTweet.length) {
        tweetNodes.push(currentTweet);
    }

    tweetNodes.forEach((tweet, index) => {
        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = tweetsHtml[index] || '';
        const text = tempDiv.textContent || tempDiv.innerText || "";
        const textLength = twitterLength(text.trim());

        const tweetNumbering = (tweetNodes.length > 1) ? `${index + 1}/${tweetNodes.length} ` : '';
        const arrow = (index < tweetNodes.length - 1) ? ' ->' : '';
        const tweetNumberingLength = tweetNumbering.length;
        const arrowLength = arrow.length;
        const finalLength = textLength + tweetNumberingLength + arrowLength;

        // Находим первый и последний <p> для твита
        const firstP = tweet.find(node => node.nodeName === 'P');
        const lastP = tweet.slice().reverse().find(node => node.nodeName === 'P') || firstP;

        // Счётчик
        const counter = document.createElement('div');
        counter.className = 'tweet-char-counter';
        counter.setAttribute('contenteditable', 'false');
        counter.innerText = `[${finalLength}/${TWEET_LIMIT}]`;
        if (finalLength > TWEET_LIMIT) {
            counter.style.color = 'red';
        }

        // Нумерация
        if (tweetNumbering && firstP) {
            const numbering = document.createElement('span');
            numbering.className = 'tweet-numbering';
            numbering.setAttribute('contenteditable', 'false');
            numbering.innerText = tweetNumbering;
            firstP.insertBefore(numbering, firstP.firstChild);
        }

        // Стрелка
        if (arrow && lastP) {
             // Убираем лишние <br /> в конце параграфа
            while (lastP.lastChild && lastP.lastChild.nodeName === 'BR') {
                lastP.removeChild(lastP.lastChild);
            }

            const arrowEl = document.createElement('span');
            arrowEl.className = 'tweet-arrow';
            arrowEl.setAttribute('contenteditable', 'false');
            arrowEl.innerText = arrow;
            lastP.appendChild(arrowEl);
        }

        // Вставка счётчика
        if (index === 0) {
            editorDom.body.insertBefore(counter, editorDom.body.firstChild);
        } else if (separators[index - 1]) {
            separators[index - 1].parentNode.insertBefore(counter, separators[index - 1].nextSibling);
        } else {
            editorDom.body.appendChild(counter);
        }
    });
}
