1.   Описание.

Бот предназначен для облегчения задачи выбора одежды.

2.   Принцип работы.

(1) Пользователь отправляет свою фотографию(по желанию еще текстовый промпт, который может содержать гендер, возраст и ценовой потолок предлагаемых товаров).

(2) Нейросеть обрабатывает фотографию и возвращает список, содержащий пол, возраст и цвет одежды человека.

(3) При помощи данных, которые выдала нейросеть с учетом информации из текстового промпта, данные из catalog.json сортируются и выбирается до 10 подходящих товаров, после чего ссылки на них с указанием цены отправляются пользователю.

3.   Техническая реализация.

(1) Написание нейросети и реализация алгоритма определения некоторых антропометрических данных:
   В связи с сжатым сроком в течение которого необходимо было создать рабочий прототип AI шоппинг ассистента, мы решили взять уже обученную модель для определения гендера, возраста человека. Для получения более точных результатов к выходному нейрону был добавлен нейрон смещения, а так же нами был реализрован алгоритм определения цвета одежды на человеке, работающий в совокупности с самой нейронной сетью.
   
   Работает это так: изображение разбивается на массив пикселей, после чего обрабатывается той моделью, которая отвечает за выделение прямоугольника (бокса), содержащего лицо человека. Выходными данными служат координаты данного прямоугольника. На следующем этапе помимо самого бокса выделяется вся область под ним, разграниченная продолжениями боковых сторон бокса. Эта область предпологаемо содержит одежду человека на фото. Далее с определенным интервалом берутся пиксели из этой области и для каждого цветового канала считается среднее значение. Полученные три значения и будут являться цветом одежды в формате rgb. В свою очередь бокс с лицом поочередно анализируется сначала моделью для определения гендера (выходным значением будет "Male" или "Female"), потом моделью для определиния возраста (выходным значением является кортеж содержащий рамки, в пределах которых находится предпологаемый возраст человека на фотографии).
   
   Важно: данная модель недостаточно точна, но для обучения более точной модели, даже при наличии наших навыков, нужно больше времени. 

(2) Парсинг сайта одежды

  Далее необходимо определить из какого каталога одежды пользователю будут предлагаться варианты. На первый взгляд может показаться, что использование данных с ozon или wildberries - наилучший вариант, однако эти сервисы постоянно борятся с возможностью парсинга своих сайтов, да и товары, выстовляемые на маркетплейсах, будут доступны гораздо меньшее количество времени, нежели товары, данные о которых находятся на сайтах, специализирующихся на продаже одежды.
  Для данной цели был выбран сайт https://www.lamoda.ru. После выбора сайта необходимо реализовать алгоритм парсинга. Схема такая: при помощи модуля selenium циклично нажимается кнопка "Показать еще". Таким образом парсится большая часть каталога одежды (130 страниц на каждый пол). После получения html кода расширенного каталога поочердно берутся фото оттуда и пропускаются через нейросеть. Выходные данные сохраняются в виде двух списков из списков, содержащих ссылку на товар и данные, полученные с фотографии товара и обработанные нейросетью. Каждый из списков записывается в словарь под ключём значение гендера людей на фотографиях всех этих товаров. Полученный словарь записывается в json файл.
  Дополнение: при реализации крупных проектов (представленный является прототипом) необходимо сохранять данные в sql формате и регулярно их обновлять посредством повторного парсинга.

(3) Написание телеграмм бота


4.   Установка и запуск.

Сначала нужно скачать зип архив и распаковать его. Далее нужно создать виртуальное окружение venv и скачать все библиотеки из requirements.txt. Запуск бота осуществляется запуском файла run.py (python run.py).

    
