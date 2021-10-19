
# Карта ДТП. Backend + Parser stat.gibdd.ru

👉 [База знаний о проекте Карта ДТП](https://github.com/dtpstat/dtp-project/wiki)

Backend Карты ДТП подготавливает пространственные данные для клиента и отдает их
через API.

Приложение основано популярном фреймворке Django и его расширении для работы
с геоданными [GeoDjango](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/). 
Которое в свою очередь опирается на библиотеку программ [GDAL](https://gdal.org/) и расширение для Postgres - [Postgis](https://postgis.net/).


## Функциональность

- API для карты (данные о ДТП, фильтр по областям)
- html каркас
- Парсер открытых данных ГИБДД
- Бот статистики
- Стандартная админка Django для работы с данными и справочниками.

---


## Разработка

- [Развертывание локальной среды](/docs/local-env.md)
- [Добавление нового API](https://www.django-rest-framework.org/api-guide/views/)
- [Добавление новых таблиц и моделей для данных](https://docs.djangoproject.com/en/3.2/topics/db/models/)
- [Встроенный cli](docs/cli.md)
  

## TODO

 - [ ] Описание структуры директорий
 - [ ] Описание методов API
