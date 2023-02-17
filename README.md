# D11 (Dissertation DB)

## Взаимодействие с Aleph'ом
* Создание записей
  * Запуск 
    * `/exlibris/u50_5/rsl01/conv/diss/r1_diss_new`
    * Пример `%src_file` – `Создание записей - запрос.seq`
      * Записи нумеруются от `000000001`
      * Внутренний идентификатор передается в 911 поле `000000001 911   L $$aD11$$b11930$$cautoref`
  * Результат `/exlibris/u50_5/rsl01/source/diss_r1/$(basename %src_file).sysno_id`
    * Пример результата – `Создание записей - ответ.sysno_id`
    * Формат - соответствие Aleph ID и внутренних идентификаторов (например `010785981, 11930, autoref`)
    
* Обновление записей
  * Запуск `/exlibris/u50_5/rsl01/conv/diss/r3_diss_update %src_file`
  * Результат `/exlibris/u50_5/rsl01/source/diss_r3/$(basename %src_file).finished`
    
* Выгрузка данных записей
  * Запуск 
    * `/exlibris/u50_5/rsl01/conv/diss/r2_diss_unload %src_file`
    * Пример `%src_file` – `Выгрузка данных записей - запрос.aleph_id_list`
  * Результат `/exlibris/u50_5/rsl01/source/diss_r2/$(basename %src_file).seq`
    * Пример результата – `Выгрузка данных записей - ответ.seq`


## URLS

### Документ

* `/doc/{ID}.html` HTML версия документа
* `/doc/{ID}-aleph-synopsis.txt` ALEPH версия автореферата
* `/doc/{ID}-aleph-dissertation.txt` ALEPH версия диссертации

### Список документов

#### ALEPH

* `/doc/list/aleph/create/synopsis.txt` авторефераты
* `/doc/list/aleph/create/dissertation.txt` диссертации

##### Фильтры списков документов
* `limit=<INT>` ограничение выдачи по кол-ву
