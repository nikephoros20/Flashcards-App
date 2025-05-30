# Flashcards App

##  Общее описание
Собственная вариация приложения Anki. Подобные приложения используются для создания карточек, содержащих информацию для запоминания.  

В оригинальном Anki возможно создавать карточки любого формата с нуля, но моя версия ограничена только карточками для английских слов. Основное отличие — автоматическое создание карточек на основе парсинга определений из Викисловаря, чего нет в оригинальном приложении.  

###  Как это работает?  
Чтобы запомнить информацию, её нужно повторить несколько раз. Пользователь добавляет английские слова, после чего они попадают в систему повторения. Когда слово появляется в специальном меню изучения, пользователь оценивает, через какое время ему стоит вернуться к нему.

##  Функции

###  *Найти слово*
1. *Поиск по одному слову*  
   - Если карточка уже добавлена, выводится уведомление с предложением её отредактировать.  
   - Если слово новое, приложение найдёт его определение в Викисловаре, предложит отредактировать и сохранить.  
   
2. *Добавление нескольких слов (через запятую)*  
   - Новые слова добавляются из Викисловаря.  
   - Выводится список: какие слова добавлены, какие уже были в базе, какие не удалось найти.  

###  *Список слов*
- Просмотр уже добавленных карточек.  
- Различные варианты сортировки.  
- Возможность открыть меню редактирования карточки.  

###  *Учить слова*
1. *Повторение слов по расписанию*  
   - Если пришло время повторения, карточки становятся активными в этом разделе.  
   - Если все слова повторены, приложение предложит изучать слова с опережением графика (на выбранное количество дней).  

2. *Как проходит повторение?*  
   - Появляется слово, пользователь пытается вспомнить его определение.  
   - Нажимает "Показать", чтобы увидеть правильный ответ.  
   - Выбирает, через сколько времени стоит повторить слово, например:  
      - *"<1 мин"* - слово не запомнено, нужно повторить его как можно скорее.
      - *"1 день"* - слово знакомо, но запомнилось плохо.  
      - *"1 неделя"* - слово запомнено.  
      - *"1 месяц" или "3 месяца"* - слово хорошо запомнено.  

По возможности проект будет обновляться и дорабатываться в будущем.
