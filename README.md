# Tender Hack backend

Серверная часть приложения по умному поиску товаров

### Запуск
```shell
$ python3 -m venv venv && source venv/bin/activate
$ pip install -r requirements/base.txt
$ ./app/manage.py makemigrations && ./app/manage.py migrate
$ ./app/manage.py loaddata products.json # не возможно положить в git репозиторий
$ ./app/manage.py runserver
```

<br>

### Описание фильтров для API
###### фильтры можно применять в неограниченным количеством списком в запросе

#### Запрос по всем полям
###### так же поддерживается поиск по числовым характеристикам, например: размер 100
```json
{
  "value": "любая строчка, в том числе с ошибками",
  "type": "All"
}
```
#### Запрос по имени продукта
```json
{
  "value": "часть имени товара, в любой раскладке, с ошибками и т д",
  "type": "Name"
}
```
#### Запрос категории продуктов
```json
{
  "value": "часть имени категории, с ошибками и т д",
  "type": "Category"
}
```
#### Запрос по имени характеристики
```json
{
  "value": "часть значения характеристики, с ошибками и т д",
  "type": "Characteristic"
}
```
#### Запрос по имени и значению характеристики
```json
{
  "value": "значение характеристики",
  "type": "часть названия характеристики"
}
```
#### Фильтрация по значению цифровой характеристики
###### операторы: = >= <= < >, так же поддерживается ранжированные значения
```json
{
  "value": ">=100",
  "type": "*Размер"
}
```
#### Множественное применение фильтров
###### Search API позволяет получить общие объекты среди разных фильтров, например черные каучуковые сапоги
###### При использовании одной и той же характеристики значения этих характеристик объединяются
###### Так же присутствует пагинация результата
```json
{
  "body": [
    {
      "value": "сапАги",
      "type": "Name"
    },
    {
      "value": "каучук",
      "type": "Материал"
    },
    {
      "value": "синий",
      "type": "Цвет"
    },
    {
      "value": "черный",
      "type": "Цвет"
    }
  ],
  "limit": 5,
  "offset": 0
}
``` 
 ###### - вернет синие и черные ботинки из каучука


### Автокомплиты и подсказки
###### Наша система подразумевает наличие подсказок по именам продуктов, категорий и т д в строке поиска товаров. Поиск оптимизирован для постоянных запросов

### Система релевантности
###### Мы реализовали систему релевантности, основанной на частоте посещения странице продукта пользователем
