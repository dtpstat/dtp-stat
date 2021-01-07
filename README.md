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


crontab -e
```
0 1 * * * cd /var/www/dtpstat/ && . .venv/bin/activate && .venv/bin/python manage.py dtp >> /tmp/cronlog-dtp.txt 2>&1
0 12-20 * * * cd /var/www/dtpstat/ && . .venv/bin/activate && .venv/bin/python manage.py bot >> /tmp/cronlog-dtp.txt 2>&1
```