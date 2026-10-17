# Сайт «Код счастливой жизни»

Статический сайт тренингов Марины Степановой (флагманская программа — «Колесо успеха»). Репозиторий и адрес пока называются `koleso-uspeha` — их можно переименовать позже (Settings → Repository name), но тогда изменятся все ссылки в роликах.

Единственный контакт для покупки — Марина, Telegram @MarinaNew. Каждая кнопка «Купить» открывает `https://t.me/MarinaNew?text=…` с готовым текстом под конкретный продукт (с ценой, если она указана, и источником из UTM-метки); текст дополнительно копируется в буфер обмена. Хостинг — GitHub Pages (ветка `main`, корень).

## Как менять цены, даты, контакты
Всё — в одном файле **`assets/config.js`** (редактируется прямо на GitHub: открыть файл → ✏️ → Commit). Пустое значение = заглушка «Цена уточняется» / «Дата уточняется».

### Что нужно заполнить
| Поле в config.js | Что это |
|---|---|
| `prices.koleso-full`, `koleso-part1`, `koleso-part2` | Цены программы: 6 мес., Часть 1, Часть 2 |
| `prices.module`, `prices.training`, `prices.mini` | Цена модуля, одного тренинга, одного мини-тренинга (можно задать и индивидуально по коду, напр. `trening-ya-vizhu-dengi`) |
| `upgradeNote` | Условия перехода Часть 1 → полная программа |
| `dates.*` | Ближайшие даты групп по коду продукта |
| `defaultTrainingDuration` | Длительность трансформационного тренинга |
| `paymentLinks.*` | Ссылки на оплату (если есть) |
| `contacts.whatsapp` | WhatsApp Марины (необязательно, появится в подвале) |
| `contacts.channelUrl`, `contacts.clubUrl` | Публичные ссылки на канал и чат «ЗАДОЛБАЛО!» |
| `photos.marina` + файл в `assets/img/` | Фото Марины |
| `bios.marina` | Образование, опыт, сертификаты |
| `yandexMetrikaId` | Номер счётчика Метрики |
| `prices.individ-sessiya`, `individ-paket`, `individ-povtor` | Индивидуальная сессия, пакет, повторная сессия |
| `prices.diagnostika`, `prices.meditacii` | Диагностика, потоковые медитации |
| `individual.packageSize`, `individual.format` | Сколько сессий в пакете (пусто — не показывается), формат |
| `diagnostics.duration`, `format`, `creditTowardPurchase`, `freeSpotsNote` | Длительность и формат диагностики, зачёт стоимости при покупке, строка про бесплатные места |
| `earlyPrices`, `priceNotes` | Ранние цены и пояснения под ценой |

Уже заполнено из материалов: Telegram Марины @MarinaNew; цены «Самопринятие» 3 500 ₽, «Самоценность» 7 000 ₽, «Движение к цели» 2 500 ₽, «Лила» 3 500 ₽, «Архитектор продукта» 80–150 тыс. ₽.

### Коды продуктов
`koleso-full`, `koleso-part1`, `koleso-part2`, `modul-1`…`modul-6`, `trening-<адрес>` (напр. `trening-dengi-iz-detstva`), `mini-<адрес>` (напр. `mini-samozvanets`), `marafon-samoprinyatie`, `marafon-dvizhenie`, `igra-lila`, `trening-samotsennost`, `arhitektor-produkta`, `psy-obuchenie`, `individ-sessiya`, `individ-paket`, `individ-povtor`, `diagnostika`, `meditacii`.

## Тексты и отзывы
Страницы генерируются скриптом: `python3 _src/gen.py` (тексты — `_src/data.py`, отзывы — `_src/reviews.py`). Результат — готовые HTML, сборка на хостинге не нужна.

Стратегия и план продвижения — [STRATEGY.md](STRATEGY.md).

## Страницы
| Страница | Адрес |
|---|---|
| Код счастливой жизни — трансформационные тренинги Марины Степановой | https://avtomaster24bot-lab.github.io/koleso-uspeha/ |
| Каталог тренингов | https://avtomaster24bot-lab.github.io/koleso-uspeha/katalog/ |
| Программа «Колесо успеха» — 6 модулей, 24 тренинга | https://avtomaster24bot-lab.github.io/koleso-uspeha/koleso-uspeha/ |
| Для психологов и коучей | https://avtomaster24bot-lab.github.io/koleso-uspeha/dlya-psihologov/ |
| Индивидуальная работа | https://avtomaster24bot-lab.github.io/koleso-uspeha/individualno/ |
| Диагностика | https://avtomaster24bot-lab.github.io/koleso-uspeha/diagnostika/ |
| Ведущая: Марина Степанова | https://avtomaster24bot-lab.github.io/koleso-uspeha/vedushchie/ |
| Отзывы участников | https://avtomaster24bot-lab.github.io/koleso-uspeha/otzyvy/ |
| Вопросы и ответы | https://avtomaster24bot-lab.github.io/koleso-uspeha/faq/ |
| Клуб предпринимателей «ЗАДОЛБАЛО!» | https://avtomaster24bot-lab.github.io/koleso-uspeha/klub/ |
| Марафон «Самопринятие» — 5 недель | https://avtomaster24bot-lab.github.io/koleso-uspeha/marafon/samoprinyatie/ |
| Марафон «Движение к цели» — 14 дней | https://avtomaster24bot-lab.github.io/koleso-uspeha/marafon/dvizhenie-k-celi/ |
| Игра «Лила» — авторская трансформационная игра | https://avtomaster24bot-lab.github.io/koleso-uspeha/igra/lila/ |
| Модуль 1 «Танго с деньгами!» | https://avtomaster24bot-lab.github.io/koleso-uspeha/modul/1-tango-s-dengami/ |
| Модуль 2 «Сквозь страхи и сомнения!» | https://avtomaster24bot-lab.github.io/koleso-uspeha/modul/2-skvoz-strahi/ |
| Модуль 3 «Выход из замкнутого круга внутренних ограничений» | https://avtomaster24bot-lab.github.io/koleso-uspeha/modul/3-vyhod-iz-zamknutogo-kruga/ |
| Модуль 4 «Мой продукт — моя гордость» | https://avtomaster24bot-lab.github.io/koleso-uspeha/modul/4-moj-produkt/ |
| Модуль 5 «В ритме успеха: мастерство успевать важное без стресса» | https://avtomaster24bot-lab.github.io/koleso-uspeha/modul/5-v-ritme-uspeha/ |
| Модуль 6 «Квантовый скачок от мечты к цели» | https://avtomaster24bot-lab.github.io/koleso-uspeha/modul/6-kvantovyj-skachok/ |
| Я вижу деньги — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/ya-vizhu-dengi/ |
| Деньги из детства — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/dengi-iz-detstva/ |
| Финансовый потолок: как прорваться к новым доходам — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/finansovyj-potolok/ |
| Моя богатая жизнь — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/moya-bogataya-zhizn/ |
| Самозванец! Страх разоблачения — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/samozvanets-strah-razoblacheniya/ |
| Страх успеха: побег от достижений — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/strah-uspeha/ |
| Финансовый страх. Освобождение — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/finansovyj-strah-osvobozhdenie/ |
| Базовый страх: из неизвестности в радость жизни — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/bazovyj-strah/ |
| Всё под контролем! — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/vsyo-pod-kontrolem/ |
| Лидер, а не нянька! — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/lider-a-ne-nyanka/ |
| Не дай собой манипулировать! Вальс в треугольнике Карпмана — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/ne-daj-soboj-manipulirovat/ |
| Как конфликты превращаются в рост — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/konflikty-v-rost/ |
| Проявляйся легко — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/proyavlyajsya-legko/ |
| Мой продукт крутой! — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/moj-produkt-krutoj/ |
| Определение стоимости своей услуги — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/stoimost-uslugi/ |
| Как озвучивать цену и брать деньги за свои услуги — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/kak-ozvuchivat-cenu/ |
| Перфекционизм — дружить, нельзя избавляться — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/perfekcionizm/ |
| Короли прокрастинации! — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/koroli-prokrastinacii/ |
| Самооценка. Зачем тебе ценник? — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/samoocenka/ |
| Действуй как… Баланс мужского и женского — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/dejstvuj-kak/ |
| Всё начинается с мечты! — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/vsyo-nachinaetsya-s-mechty/ |
| Твой фундамент успешного старта к цели — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/fundament-starta/ |
| Проверка истинности цели — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/istinnost-celi/ |
| Конкретные шаги к цели — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/konkretnye-shagi/ |
| Самоценность. Нужный, полезный, хороший, ценный сам для себя! — тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/trening/samotsennost/ |
| Самозванец. Кто у руля? — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/samozvanets/ |
| Страх успеха. Кто жмёт на тормоза? — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/strah-uspeha/ |
| Финансовый страх. Денежная броня — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/finansovyj-strah/ |
| Базовый страх — скелет в шкафу успеха — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/bazovyj-strah/ |
| Зачем мне всё контролировать? — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/kontrol/ |
| Без меня никто не справится! — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/bez-menya/ |
| Истоки конфликтов в команде (бизнес, партнёрство, семья) — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/istoki-konfliktov/ |
| Как не терять связь в конфликтах (бизнес, партнёрство, семья) — мини-тренинг | https://avtomaster24bot-lab.github.io/koleso-uspeha/mini/svyaz-v-konfliktah/ |
