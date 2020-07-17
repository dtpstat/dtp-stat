### Тесты
- Тесты пишутся на фреймворке [pytest](https://docs.pytest.org/en/stable/index.html)
- Интеграция с джангой через библиотеку [pytest-django](https://pytest-django.readthedocs.io/en/latest/)
- Запускаются на каждый коммит через [github actions](../.github/workflows/pytest.yml)

#### Parametrize

Иногда удобно протестировать кусок логики с набором входных и выходных данных. Для этого можно использовать декоратор `@pytest.mark.parametrize` 
Пример: 
```
import pytest


@pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```
[Документация](https://docs.pytest.org/en/stable/parametrize.html)
