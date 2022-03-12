# Задача
- От популациите на държавите (data/country_populations.csv) извадете популацията на всяка страна (всички, които не започват с "OWID_" префикс) за 2020 г. 

- От файла с ваксинациите (data/vaccinations.csv) извадете последните данните за напълно ваксинираната с ковид ваксина част от населението (колона - people_fully_vaccinated) за всяка една от страните дефинирани в "country_populations.csv" (без дефинираните общи региони с "OWID_" префикс). Използвайте колоните - iso_code / Country Code. Ако има такива, за които няма данни запълнете информацията с нула (0).

- Пресметнете процента напълно ваксинирани за всяка една страна: ([vaccinations.csv\колона people_fully_vaccinated] / [country_populations.csv\колона 2020])*100

- Запишете получената информация в дадената таблица, следвайки предефинираната структура на таблицата

Table 'countries':
name (text), iso_code (text), population (int), total_vaccinated (int), percentage_vaccinated(real) 

- 'prepare.py' създава sqlite3 таблица с няколко предефинирани записа.

- Бонус: Опитайте се да запазите предефинираните страни от таблицата, като единствено промените техните стойности за population, total_vaccinated и percentage_vaccinated.
