# Звідки брати новини, звіти й аналітику по китайських моделях

Це додаток до категорії D у [`INFRA-CAPSTONE.md`](INFRA-CAPSTONE.md). Питання просте: **де дивитися первинний факт**, а де лише чужу інтерпретацію.

Правило одне. Спочатку філінг або сторінка самої компанії. Потім агенція (Reuters, Caixin). Наприкінці блог і Telegram. Якщо цифра є лише в статті, а в звіті її немає — у таблиці пишемо `inferred`, не `verified`.

---

## 1. Спільні джерела (для всіх імен)

| Що потрібно | Куди йти | Навіщо саме це |
| --- | --- | --- |
| Офіційні біржові PDF (прибутки, placing, ризик-фактори) | [HKEXnews](https://www.hkexnews.hk/) — пошук за кодом `0100`, `2513`, `0700`, `1810`, `9988` | Для MiniMax, Z.AI, Tencent, Xiaomi, Alibaba це перше джерело правди. Не Yahoo-заголовок |
| Ціна, календар звітів, чорновик cash flow | Yahoo Finance, наприклад [2513.HK](https://finance.yahoo.com/quote/2513.HK/), `0100.HK`, `0700.HK`, `1810.HK`, `9988.HK` | Зручно тягнути в Python. Цифри з `Ticker.info` завжди звіряти з PDF |
| Чи модель ще «жива» на ринку API | [OpenRouter](https://openrouter.ai/) (рейтинг Value Leaders) і картка провайдера | Якщо MiniMax випав з топу — попит на токени міг впасти раніше, ніж звіт |
| Ваги, ліцензія, технічний звіт | [Hugging Face](https://huggingface.co/) і GitHub лабораторії | Реліз моделі часто виходить за тижні до згадки в 10-сторінковому огляді банку |
| Якість моделі (не ціна акції) | [Artificial Analysis](https://artificialanalysis.ai/), LMSYS / Arena, власні прогони | Щоб не плутати «багато токенів на OpenRouter» з «краща модель» |
| Англомовні новини по Китаю | [Reuters](https://www.reuters.com/), [Bloomberg](https://www.bloomberg.com/), [South China Morning Post](https://www.scmp.com/), [Caixin Global](https://www.caixinglobal.com/), [Fortune](https://fortune.com/) | Перевірені вторинні джерела. SCMP і Caixin частіше першими пишуть про HK IPO й держзакупівлі |
| Китайськомовні тех-новини | 36Kr, LatePost, Jiemian, The Paper, Xueqiu (雪球) | Швидше за англійську пресу. Перевіряти фактаж обидва рази: часто без першоджерела |
| Континентальні A-share філінги (книга B, не моделі) | [巨潮资讯 CNINFO](http://www.cninfo.com.cn/) | Для Cambricon, NAURA, SMIC A-share. Для MiniMax / Z.AI на HKEX не головне |

Раз на тиждень достатньо: HKEXnews по п’яти кодах + OpenRouter + один огляд Caixin/SCMP. Не треба читати все.

---

## 2. Джерела по кожній компанії

### MiniMax (`0100.HK`) — публічна лабораторія

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| Investor relations | [ir.minimaxi.com/en](https://ir.minimaxi.com/en) | Дати звітів, презентації, контакти IR (`ir@minimax.io`) |
| Сайт продукту | [minimaxi.com](https://www.minimaxi.com) | Релізи моделей (M3, Hailuo), не фінанси |
| Біржа | HKEXnews, код **0100** | Interim / annual results, placing, prospectus |
| Новини-агрегатор | Yahoo / Reuters по `00100.HK` | Календар, наприклад interim results ([анонс серпня 2026](https://finance.yahoo.com/technology/ai/articles/minimax-report-2026-interim-financial-093000807.html)) |

### Z.AI / GLM (`2513.HK`) — публічна лабораторія

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| Продукт і блог моделей | [z.ai](https://z.ai) (наприклад [блог GLM-5.3](https://z.ai/blog/glm-5.3)) | Що саме випустили, open-weight чи ні |
| Китайський корпоративний сайт | [zhipuai.cn](https://www.zhipuai.cn/) | Локальні релізи, продукти AutoGLM / ChatGLM |
| Біржа | HKEXnews, код **2513** | Виручка on-prem vs cloud, збитки, placing |
| Котирування | [Yahoo 2513.HK](https://finance.yahoo.com/quote/2513.HK/) | Ціна. Виручку завжди брати з PDF, не з картки Yahoo |

### Alibaba / Qwen (`9988.HK`, `BABA`)

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| IR групи | [alibabagroup.com IR](https://www.alibabagroup.com/en-US/ir-tools) | Earnings, cloud revenue. Qwen у звіті часто сидить у Cloud, окремого рядка «модель» може не бути |
| SEC (ADR) | EDGAR, емітент Alibaba Group Holding | 20-F / 6-K — той самий звіт англійською |
| Моделі | Hugging Face / ModelScope (`Qwen`) | Реліз лінійки Qwen3.x |
| Біржа HK | HKEXnews, код **9988** | Паралельно з SEC |

Пам’ятай: акція Alibaba — це ще й e-commerce. Не читай рух `BABA` як «ринок повірив у Qwen».

### Tencent / Hunyuan / Hy (`0700.HK`)

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| IR | [tencent.com/en-us/investors](https://www.tencent.com/en-us/investors) | Квартальні результати, сегмент Cloud |
| Біржа | HKEXnews, код **0700** | Офіційні PDF |
| Моделі | OpenRouter slug `tencent`, релізи Hunyuan | Окремого «чистого» тікера моделі немає |

Tencent ще й інвестор у приватні лабораторії (у тому числі згадують DeepSeek). У нотатці розділяй: **власна модель Hunyuan** vs **частка в чужій лабораторії**.

### Xiaomi / MiMo (`1810.HK`)

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| IR | [ir.mi.com](https://ir.mi.com/) | Річний і квартальний звіт; AI зазвичай у розділі про телефони / AIoT, не окремий сегмент |
| Біржа | HKEXnews, код **1810** | Офіційні PDF |
| Моделі | OpenRouter slug `xiaomi` | MiMo — продукт, не окрема компанія |

### DeepSeek (приватна)

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| Сайт | [deepseek.com](https://www.deepseek.com) | Продукт і API, не фінансовий звіт |
| Код і ваги | [github.com/deepseek-ai](https://github.com/deepseek-ai) | Реліз V3 / V4, ліцензія |
| Фінанси | Немає 10-K. Лише статті агенцій і регуляторні уривки (раунди, оцінка) | Ставити мітку `reported in press`, не `filing` |
| Контекст | Wikipedia [DeepSeek](https://en.wikipedia.org/wiki/DeepSeek) лише як навігація, не як джерело цифр | Завжди йти в статтю Reuters / FT / Bloomberg, на яку вона посилається |

### Moonshot / Kimi (приватна)

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| Продукт | [kimi.com](https://www.kimi.com) / [moonshot.cn](https://www.moonshot.cn) | Реліз Kimi, не P&L |
| Новини про IPO | Reuters, SCMP, Fortune (наприклад [огляд лабораторій](https://fortune.com/2026/07/26/china-moonshot-deepseek-zai-kimi-challenging-us-ai-cost/)) | «Confidentially filed IPO» ≠ тікер. Поки немає коду HKEX — ціни немає |
| Ваги | Hugging Face (`moonshotai`) | Open-weight релізи |

### Inclusion AI / Ling / Ant Group (приватна група)

| Тип | Адреса | Що там брати |
| --- | --- | --- |
| Лабораторія | [inclusion-ai.org](https://www.inclusion-ai.org/) | Хто стоїть за Ling |
| Релізи Ant | [antgroup.com news](https://www.antgroup.com/en/news-media/press-releases/1759982400000) | Офіційний текст про Ling-1T |
| Документація моделі | [developer.ant-ling.com](https://developer.ant-ling.com/en/docs/models/ling/) | Технічний опис, не виручка |
| Публічний проксі | IR Alibaba (див. вище) | Лише як інвестор Ant. Не підставляти cloud Alibaba як «виручку Ling» |

---

## 3. Аналітика (вторинна, після філінгу)

| Джерело | Коли варто | Обмеження |
| --- | --- | --- |
| Звіти CICC, UBS, Goldman, HSBC по HK AI | Після interim MiniMax / Z.AI | Платні; часто є в анотації на HKEXnews, якщо компанія сама викладає «analyst coverage» |
| SemiAnalysis, The Information | Compute, дефіцит чипів, собівартість токена | Підписка; не замінює P&L |
| Sacra та подібні профілі приватних | Оцінка DeepSeek / раунди | Модельні оцінки, не аудит |
| OpenRouter + Artificial Analysis | Попит і якість API | Не виручка компанії |

---

## 4. Щотижневий мінімум (30–40 хвилин)

1. HKEXnews: чи вийшов PDF по `0100`, `2513`, `0700`, `1810`, `9988`.
2. OpenRouter: чи ті самі бренди ще в Value Leaders.
3. Сайти моделей: DeepSeek GitHub, Z.ai blog, MiniMax IR, Qwen на Hugging Face.
4. Одна стрічка Caixin або SCMP / Reuters по «China AI IPO» або «GLM / Kimi / DeepSeek».
5. У журнал: дата, URL, одна цифра, мітка `filing` / `company blog` / `press`.

Якщо за тиждень не було філінгу — не вигадуй «оновлену виручку» з колонки новин.

---

## 5. Як це лягає на питання 6

У [`../q6-ai-metrics/Q6-METRICS.md`](../q6-ai-metrics/Q6-METRICS.md) для книги D рахуємо ціну `0100.HK` і `2513.HK` і перевіряємо присутність моделі на OpenRouter. Цифри виручки MiniMax і Z.AI беремо **лише** з PDF на HKEXnews. Для DeepSeek і Kimi в таблиці CapEx / revenue ставимо порожньо, не нуль.
