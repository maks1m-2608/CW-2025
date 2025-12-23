Idea Creator (Генератор идей)

Данный сервис предназначен для генерации идей с помощью локальной LLM. 

Для работы программы необходимо наличие локальной LLM (Ollama + Mistral), базы данных PosgreSQL, Docker.
В папке .env нужно ввести свои значения для базы данных и ip.

Запуск проекта через Docker:
1. Перейти в директорию с файлами проекта.
2. Выполнить команду "sudo docker compose up -d --build"
3. Перейти по адресу http://localhost:8000/
4. Пользуемся программой!

Если нужно посмотреть результаты запросов в базе данных:
1. Перейти в директорию с файлами проекта.
2. Выполнить команду "docker exec -it "название контейнера с БД" psql -U "имя пользователя" -d "название БД" "
3. Работа с базой данных:
Для просмотра содержимого выполнить команду:
"
SELECT t.title AS "Тема", string_agg(i.text, ', ') AS "Список идей"
FROM topics t
JOIN ideas i ON t.id = i.topic_id
GROUP BY t.id, t.title
ORDER BY t.created_at DESC;
"
Для просмотра всех тем: 
"SELECT * FROM topics;"

Для просмотра всех идей: 
"SELECT * FROM ideas;"

Очистить базу данных:
"TRUNCATE topics, ideas RESTART IDENTITY CASCADE;"

Выйти:
"\q"

