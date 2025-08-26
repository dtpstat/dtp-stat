document.addEventListener("DOMContentLoaded", function() {
    const textarea = document.getElementById("id_text");
    const ckConfigs = JSON.parse(textarea.dataset.ckeditorConfigs);
    let editor = CKEDITOR.instances[textarea.id];

    const modeField = document.getElementById("id_account");

    restartEditor(); // инициализация при загрузке страницы

    modeField.addEventListener("change", restartEditor);

    function restartEditor() {
        let val = modeField.selectedOptions[0].text;
        // оставляем только часть до "—"
        val = val.split('—')[0].trim();

        const newConfig = ckConfigs[val];

        if (!newConfig) {
            const error_msg = `CKEditor config для "${val}" не найден`;
            console.error(error_msg);
            alert(`Ошибка: ${error_msg}`);
            return; // прекращаем выполнение, чтобы не ломать редактор
        }

        // Пересоздаём редактор:

        // Сохраняем текущее содержимое
        const oldData = cleanTweetMeta(editor.getData({ format: 'html' }));

        // Сохраняем ID контейнера (textarea)
        const editorId = editor.name;

        // Создаём новый конфиг на основе старого, но с новыми параметрами
        let config = Object.assign({}, editor.config);
        config.toolbar = newConfig.toolbar;
        config.allowedContent = newConfig.allowedContent;
        config.extraPlugins = newConfig.extraPlugins;

        // Уничтожаем старый редактор
        editor.destroy();

        // Cоздаём новый редактор с нужными параметрами
        editor = CKEDITOR.replace(editorId, config);

        // Восстанавливаем содержимое
        editor.setData(oldData);
    } 
});

function cleanTweetMeta(data) {
    const container = document.createElement('div');
    container.innerHTML = data;

    // Удаляем div.tweet-separator
    container.querySelectorAll('div.tweet-separator').forEach(el => el.remove());

    // Удаляем span с указанными классами
    container.querySelectorAll('span.tweet-numbering, span.tweet-arrow, span.tweet-char-counter')
             .forEach(el => el.remove());

    return container.innerHTML;
}