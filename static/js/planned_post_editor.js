document.addEventListener("DOMContentLoaded", () => {
  // helper: извлечь "имя аккаунта" до ":"
  function parseAccountName(text) {
    return text.split(':')[0].trim();
  }
  // helper: очистка мета-тегов твита
  function cleanTweetMeta(data) {
    const container = document.createElement('div');
    container.innerHTML = data || '';
    container.querySelectorAll('div.tweet-separator').forEach(el => el.remove());
    container.querySelectorAll('span.tweet-numbering, span.tweet-arrow, span.tweet-char-counter')
             .forEach(el => el.remove());
    return container.innerHTML;
  }

  // restart/replace editor для одного textarea
  function restartEditorForTextarea(textarea, accountName, ckConfigs, editable) {
    if (!textarea) return;
    const instance = CKEDITOR.instances[textarea.id];
    const oldData = instance ? cleanTweetMeta(instance.getData({ format: 'html' })) : (textarea.value || '');
    const editorId = textarea.id;

    const newConfig = ckConfigs[accountName];
    if (!newConfig) {
        const error_msg = `CKEditor config для "${accountName}" не найден`;
        console.error(error_msg);
        alert(`Ошибка: ${error_msg}`);
        return; // прекращаем выполнение, чтобы не ломать редактор
    }

    // сформируем config: возьмём исходный, если есть, иначе пустой
    const baseConfig = instance ? Object.assign({}, instance.config) : {};
    const config = Object.assign({}, baseConfig,
      newConfig ? {
        toolbar: newConfig.toolbar,
        allowedContent: newConfig.allowedContent,
        extraPlugins: newConfig.extraPlugins
      } : {}
    );

    // уничтожаем если был
    if (instance) {
      try { instance.destroy(); } catch (e) { console.warn('Ошибка при destroy CKEditor:', e); }
    }

    // создаём/заменяем
    const newEditor = CKEDITOR.replace(editorId, config);

    // после инициализации ставим содержимое и readonly-режим
    newEditor.once('instanceReady', () => {
      try { newEditor.setData(oldData); } catch (e) { console.warn('setData failed', e); }
      // setReadOnly(true) делает редактор доступным для просмотра, но не для редактирования
      newEditor.setReadOnly(!editable);
    });

    return newEditor;
  }

  // Основная логика для строки <tr>
  function handleRow(tr) {
    const leftTd = tr.children[0];
    const rightTd = tr.children[1];
    if (!rightTd || !leftTd) return;

    const textarea = rightTd.querySelector('textarea[data-ckeditor-configs]');
    if (!textarea) return;

    // парсим конфиги из data-атрибута
    let ckConfigs = {};
    try {
      ckConfigs = JSON.parse(textarea.dataset.ckeditorconfigs || textarea.dataset.ckeditorConfigs || '{}');
    } catch (e) {
      console.error('Невалидный JSON в data-ckeditor-configs для', textarea, e);
    }

    const small = leftTd.querySelector('small');
    const accountName = small.textContent.trim();
    restartEditorForTextarea(textarea, accountName, ckConfigs, true);
  }

  // Если на странице таблица с формами (множественные/табличные формы)
  const trs = document.querySelectorAll('table.form-table tbody tr');
  if (trs && trs.length) {
    trs.forEach(tr => handleRow(tr));
    return;
  }

  // Иначе — попытка обработать одиночную форму (не в таблице)
  // 1) ищем textarea с data-ckeditor-configs
  const singleTextarea = document.querySelector('textarea[data-ckeditor-configs]');
  if (!singleTextarea) return;

  // find account select by id or readonly
  const select = document.getElementById('id_account');
  const readonlyDiv = document.querySelector('.form-row.field-account .readonly');
  let ckConfigs = {};
  try { ckConfigs = JSON.parse(singleTextarea.dataset.ckeditorconfigs || singleTextarea.dataset.ckeditorConfigs || '{}'); } catch(e){}

  if (select) {
    const apply = () => {
      const selectedText = select.selectedOptions[0].text;
      const accountName = parseAccountName(selectedText);
      restartEditorForTextarea(singleTextarea, accountName, ckConfigs, true);
    };
    select.addEventListener('change', apply);
    apply();
  } else if (readonlyDiv) {
    const accountName = parseAccountName(readonlyDiv.innerText);
    restartEditorForTextarea(singleTextarea, accountName, ckConfigs, false);
  } else {
    console.error('Something unexpected happened!');
  }
});
