<div align="center">

# kutub · كُتُب

**Turn a Telegram book channel into a searchable library.**

[![Version](https://img.shields.io/github/v/tag/Ajarallah/kutub?label=version&color=blue)](https://github.com/Ajarallah/kutub/releases)
[![CI](https://github.com/Ajarallah/kutub/actions/workflows/ci.yml/badge.svg)](https://github.com/Ajarallah/kutub/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)](#requirements)
[![Telegram](https://img.shields.io/badge/Telegram-MTProto-26A5E4?logo=telegram&logoColor=white)](https://docs.telethon.dev/)
[![Kindle](https://img.shields.io/badge/Kindle-Send--to--Kindle-FF9900?logo=amazon&logoColor=white)](#kindle-delivery)

[English](#english) · [العربية](#العربية)

</div>

---

Book channels on Telegram hold thousands of files behind a scroll bar. There is no index, no reliable search, and no way to know what is actually in there. `kutub` reads a channel once, catalogues every ebook it finds, and gives you instant full-text search — then downloads any title on demand, optionally sending it straight to a Kindle.

Built for messy filenames and Arabic titles. Works with any language.

```console
$ kutub index @some_books_channel
Indexing: Some Books Channel
  … 250
  … 500
Added 9941 book(s) | skipped 0 already indexed

$ kutub search "kahneman"
[3182] Thinking, Fast and Slow — Daniel Kahneman  (epub, 2.4MB)
[7741] Noise: A Flaw in Human Judgment — Daniel Kahneman  (epub, 1.8MB)

2 result(s). Download with:  kutub get <id> [--kindle]

$ kutub get 3182 --kindle
Downloading: Thinking, Fast and Slow
Saved to: ~/Downloads/Thinking, Fast and Slow.epub
Sent to Kindle.
```

---

## English

### Features

|   | |
|---|---|
| **Full-channel indexing** | Walks a channel's entire history and catalogues every `.epub`, `.pdf`, `.mobi`, `.azw3`, `.txt`, `.docx`, `.fb2`, `.djvu` |
| **Instant search** | SQLite FTS5 index with substring fallback — sub-second results across tens of thousands of titles |
| **Author extraction** | Parses inconsistent filenames into title and author, handling Arabic and Latin separators |
| **Multi-channel** | Index several channels into one catalogue and search them together |
| **Kindle delivery** | `--kindle` downloads and sends via Send-to-Kindle, no email step |
| **Local and private** | Everything lives in `~/.kutub` — no server, no telemetry, no third party |

### Requirements

- Python 3.9 or newer
- [Telethon](https://docs.telethon.dev/) — `pip install telethon`
- Telegram API credentials (free — [see setup](#setup))
- Optional: [stkclient](https://github.com/maxdjohnson/stkclient) for Kindle delivery

### Install

```bash
git clone https://github.com/Ajarallah/kutub.git
cd kutub
pip install .
```

This puts a `kutub` command on your `PATH`. For Kindle delivery install the extra: `pip install ".[kindle]"`.

### Setup

**1 — Get Telegram API credentials**

Open <https://my.telegram.org/apps>, sign in with your phone number, and create an application (any title, platform **Desktop**). Copy the `api_id` and `api_hash`.

**2 — Authenticate**

```bash
kutub login
```

You will be asked for both values, then for the login code Telegram sends you. This happens once.

**3 — Index a channel**

```bash
kutub channels                  # find the channel and its id
kutub index @channelusername    # by username
kutub index -1001234567890      # by id
kutub index "Channel Title"     # by exact title
```

Indexing 10,000 files takes about two minutes, limited by Telegram's rate limits rather than by `kutub`.

### Usage

| Command | Purpose |
|---|---|
| `kutub login` | Authenticate with Telegram (one time) |
| `kutub channels` | List channels and groups you belong to |
| `kutub index <channel> [--limit N]` | Catalogue every ebook in a channel |
| `kutub search "query" [-n N]` | Full-text search the catalogue |
| `kutub list [--channel X] [-n N]` | List recently indexed books |
| `kutub stats` | Totals by channel and format |
| `kutub get <id> [--kindle]` | Download a book, optionally to Kindle |

### Kindle delivery

Authenticate `stkclient` once and find your device serial:

```bash
pip install stkclient
python3 -m stkclient login
python3 -m stkclient devices
```

Then set the serial so `--kindle` knows where to send:

```bash
export KINDLE_SERIAL=YOUR_DEVICE_SERIAL
kutub get 3182 --kindle
```

Or pass `--device` per call. Files arrive as Kindle Personal Documents.

### Configuration

| Variable | Purpose | Default |
|---|---|---|
| `KUTUB_HOME` | Data directory | `~/.kutub` |
| `KUTUB_DOWNLOAD_DIR` | Download destination | `~/Downloads` |
| `TG_API_ID` / `TG_API_HASH` | Telegram credentials (override the config file) | — |
| `KINDLE_SERIAL` | Default Kindle device serial | — |

### How it works

```
Telegram channel
      │
      │  Telethon (MTProto)  ── walks message history
      ▼
  file filter ──────────────  keeps ebook extensions only
      ▼
 filename parser ──────────  splits "Title - Author.epub" into fields
      ▼
   SQLite + FTS5 ──────────  ~/.kutub/books.db
      ▼
  search / get  ────────────  download → optional Send-to-Kindle
```

Indexing stores **metadata only** — files stay in Telegram until you ask for one. A catalogue of 10,000 books costs roughly 3 MB on disk.

### Privacy and safety

- Runs entirely on your machine — nothing is uploaded anywhere
- API credentials live in `~/.kutub/config.json` with `0600` permissions
- The Telegram session file grants access to your account: treat `~/.kutub/` as a secret directory and never commit it
- `kutub` reads only channels you already belong to, using your own account, exactly as the official client does

### Limitations

- Filename parsing assumes `Title - Author`. Files named `Author - Title` come out with the two fields swapped; search still finds them through the filename field.
- Duplicate uploads appear as separate entries — the same book posted twice is indexed twice.
- Telegram rate-limits history reads. Very large channels may pause mid-index; re-running `index` resumes safely and skips what is already catalogued.
- Kindle delivery requires `stkclient` to be authenticated separately.

### Roadmap

- [ ] EPUB metadata extraction for accurate titles and authors
- [ ] Duplicate detection across channels
- [ ] Incremental indexing from the last seen message
- [ ] Export the catalogue to CSV and JSON

### Contributing

Issues and pull requests are welcome. The tool is a single file with no build step — clone, edit `kutub.py`, run it.

---

## العربية

قنوات الكتب في تيليجرام تخزّن آلاف الملفات خلف شريط تمرير، بلا فهرس ولا بحث موثوق ولا وسيلة لمعرفة ما فيها فعلًا. تقرأ **kutub** القناة مرة واحدة، وتفهرس كل كتاب فيها، وتمنحك بحثًا نصيًا فوريًا، ثم تنزّل أي عنوان عند الطلب وترسله إلى الكيندل مباشرة إن أردت.

صُمّمت للأسماء الفوضوية والعناوين العربية، وتعمل مع أي لغة.

### المزايا

|   | |
|---|---|
| **فهرسة كاملة** | تمشي على تاريخ القناة كله وتلتقط صيغ `epub` و`pdf` و`mobi` و`azw3` و`txt` و`docx` و`fb2` و`djvu` |
| **بحث فوري** | فهرس SQLite FTS5 مع بحث احتياطي بالنص الجزئي، ونتائج في أقل من ثانية عبر عشرات الآلاف من العناوين |
| **استخراج المؤلف** | تحلّل أسماء الملفات غير المنتظمة إلى عنوان ومؤلف، وتتعامل مع الفواصل العربية واللاتينية |
| **قنوات متعددة** | افهرس عدة قنوات في قاعدة واحدة وابحث فيها جميعًا دفعة واحدة |
| **إرسال للكيندل** | الخيار `--kindle` ينزّل الكتاب ويرسله عبر Send-to-Kindle بلا بريد إلكتروني |
| **محلية وخاصة** | كل شيء داخل `~/.kutub`، بلا خادم ولا تتبّع ولا طرف ثالث |

### المتطلبات

- Python 3.9 أو أحدث
- مكتبة [Telethon](https://docs.telethon.dev/) — `pip install telethon`
- بيانات API من تيليجرام (مجانية)
- اختياري: [stkclient](https://github.com/maxdjohnson/stkclient) للإرسال إلى الكيندل

### التثبيت

```bash
git clone https://github.com/Ajarallah/kutub.git
cd kutub
pip install .
```

يضيف هذا أمر `kutub` إلى مسارك. وللإرسال إلى الكيندل ثبّت الإضافة: `pip install ".[kindle]"`.

### الإعداد

**١ — احصل على بيانات API**

افتح <https://my.telegram.org/apps>، وسجّل الدخول برقم هاتفك، وأنشئ تطبيقًا بأي اسم مع اختيار المنصة **Desktop**، ثم انسخ `api_id` و`api_hash`.

**٢ — سجّل الدخول**

```bash
kutub login
```

سيطلب منك القيمتين، ثم رمز التحقق الذي يصلك في تيليجرام. مرة واحدة فقط.

**٣ — افهرس قناة**

```bash
kutub channels                  # اعرض القنوات ومعرّفاتها
kutub index @channelusername    # بالمعرّف النصي
kutub index -1001234567890      # بالرقم
kutub index "اسم القناة"          # بالاسم الكامل
```

فهرسة عشرة آلاف ملف تستغرق دقيقتين تقريبًا، والحد هنا من تيليجرام لا من الأداة.

### الأوامر

| الأمر | الوظيفة |
|---|---|
| `kutub login` | تسجيل الدخول إلى تيليجرام (مرة واحدة) |
| `kutub channels` | عرض القنوات والمجموعات التي تنتمي إليها |
| `kutub index <channel>` | فهرسة كل كتب القناة |
| `kutub search "كلمة"` | بحث نصي في الفهرس |
| `kutub list` | عرض آخر ما فُهرس |
| `kutub stats` | إحصاءات حسب القناة والصيغة |
| `kutub get <id> --kindle` | تنزيل كتاب وإرساله للكيندل |

### الإرسال إلى الكيندل

سجّل الدخول في `stkclient` مرة واحدة، واستخرج الرقم التسلسلي لجهازك:

```bash
pip install stkclient
python3 -m stkclient login
python3 -m stkclient devices
```

ثم عيّن الرقم ليعمل الخيار `--kindle`:

```bash
export KINDLE_SERIAL=رقم_جهازك
```

أو مرّره لكل أمر عبر `--device`. تصل الملفات ضمن المستندات الشخصية في الكيندل.

### الخصوصية والأمان

- تعمل الأداة على جهازك بالكامل، ولا تُرفع أي بيانات إلى أي مكان
- بيانات API محفوظة في `~/.kutub/config.json` بصلاحيات `0600`
- ملف الجلسة يمنح صلاحية الوصول إلى حسابك، فعامِل مجلد `~/.kutub/` معاملة الأسرار ولا ترفعه إلى مستودع
- تقرأ الأداة القنوات التي تنتمي إليها فقط، بحسابك أنت، تمامًا كما يفعل تطبيق تيليجرام الرسمي

### الحدود المعروفة

- تحليل أسماء الملفات يفترض ترتيب `العنوان - المؤلف`، فالملفات المسماة `المؤلف - العنوان` يظهر حقلاها معكوسين، والبحث يجدها عبر اسم الملف على أي حال
- النسخ المكررة تظهر كمدخلات منفصلة
- تيليجرام يحدّ من سرعة قراءة السجل، وقد تتوقف الفهرسة مؤقتًا في القنوات الكبيرة جدًا، وإعادة تشغيل `index` تُكمل بأمان وتتجاوز المفهرس سابقًا
- الإرسال للكيندل يتطلب تسجيل دخول منفصل في `stkclient`

---

## License

MIT — see [LICENSE](LICENSE).

Built on [Telethon](https://docs.telethon.dev/) for Telegram access and [stkclient](https://github.com/maxdjohnson/stkclient) for Send-to-Kindle delivery.
