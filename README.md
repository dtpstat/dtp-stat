# dtp_stat

### Настройка окружения для разработки
#### Requirements
- docker
- docker-compose
- docker-machine (for win & mac)
#### Запуск проекта

`make run`

- зайти в веб-интерфейс: http://localhost:5000/
- открыть шелл для запуска `manage.py` команд: `make sh`
- [настроить сборщик метрик](docs/metrics.md)

#### Запуск тестов локально

`make test`

### Deploy

ansible-playbook -i production site.yml
