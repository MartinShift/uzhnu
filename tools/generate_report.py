"""Generate the practice report (.docx) for the Arch Kanban project.

Mirrors the structure and styling of the reference report.docx in the
workspace root, but with the Arch Kanban content. Figures are inserted
as italic placeholders that the student can replace with screenshots.

Run:  python tools/generate_report.py
Output: report_archkanban.docx in the workspace root.
"""

from __future__ import annotations

from pathlib import Path
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, RGBColor

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FONT_BODY = "Times New Roman"
FONT_MONO = "Consolas"
SIZE_BODY = Pt(14)
SIZE_TBL = Pt(12)
SIZE_CODE = Pt(9)
INDENT_FIRST = Cm(1.25)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------
def _set_run(run, *, bold=False, italic=False, size=SIZE_BODY, font=FONT_BODY,
             color: RGBColor | None = None):
    run.font.name = font
    run.font.size = size
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    # Force Cyrillic-safe font in Word rPr
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        rfonts.set(qn(f"w:{attr}"), font)


def _para(doc_or_cell, text="", *, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
          first_line_indent: Cm | None = INDENT_FIRST, bold=False, italic=False,
          size=SIZE_BODY, font=FONT_BODY, spacing=1.5, space_before=0, space_after=0,
          color: RGBColor | None = None, left_indent: Cm | None = None):
    p = doc_or_cell.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = spacing
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if first_line_indent is not None:
        pf.first_line_indent = first_line_indent
    if left_indent is not None:
        pf.left_indent = left_indent
    if text:
        run = p.add_run(text)
        _set_run(run, bold=bold, italic=italic, size=size, font=font, color=color)
    return p


def _page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


# Higher-level wrappers ------------------------------------------------------
def body(doc, text):
    return _para(doc, text)


def body_noindent(doc, text, *, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    return _para(doc, text, first_line_indent=None, align=align)


def centered(doc, text, *, bold=False, italic=False, size=SIZE_BODY,
             space_before=0, space_after=0):
    return _para(doc, text, align=WD_ALIGN_PARAGRAPH.CENTER,
                 first_line_indent=None, bold=bold, italic=italic, size=size,
                 space_before=space_before, space_after=space_after)


def h_section(doc, text):
    # Top-level heading: "ВСТУП", "ВИСНОВКИ", "1 ТЕОРЕТИЧНА ЧАСТИНА"
    p = _para(doc, text.upper(), align=WD_ALIGN_PARAGRAPH.CENTER,
              first_line_indent=None, bold=True, space_before=12, space_after=12)
    return p


def h_sub(doc, text):
    # "1.1 Загальні відомості..." — bold, left-aligned, no first-line indent
    p = _para(doc, text, align=WD_ALIGN_PARAGRAPH.LEFT,
              first_line_indent=None, bold=True, space_before=10, space_after=6)
    return p


def h_subsub(doc, text):
    # "1.1.1 …" — bold italic, indented
    p = _para(doc, text, align=WD_ALIGN_PARAGRAPH.LEFT,
              first_line_indent=INDENT_FIRST, bold=True, italic=True,
              space_before=6, space_after=4)
    return p


def figure_placeholder(doc, number: str, caption: str, *, height_hint="≈400px"):
    """Insert a styled placeholder where the student will paste a screenshot,
    followed by the centered caption line."""
    box = _para(doc, f"[Рисунок {number} — місце для скріншота, {height_hint}]",
                align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent=None,
                italic=True, color=RGBColor(0x77, 0x77, 0x77),
                space_before=6, space_after=2)
    centered(doc, f"Рисунок {number} {caption}", size=Pt(13),
             space_before=0, space_after=8)


def table_caption(doc, number: str, name: str):
    # Table caption goes ABOVE the table, left-aligned, e.g.:
    # "Таблиця 2.1 Атрибути сутності «Project»"
    _para(doc, f"Таблиця {number} {name}", align=WD_ALIGN_PARAGRAPH.LEFT,
          first_line_indent=None, space_before=8, space_after=4)


def _cell_set_text(cell, text, *, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT,
                   size=SIZE_TBL):
    cell.text = ""
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = 1.15
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = None
    run = p.add_run(text)
    _set_run(run, bold=bold, size=size)


def _set_table_borders(table):
    tbl = table._element
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr"); tbl.insert(0, tblPr)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:color"), "000000")
        borders.append(b)
    tblPr.append(borders)


def attribute_table(doc, headers: list[str], rows: list[list[str]],
                    col_widths_cm: list[float] | None = None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(table)
    for i, h in enumerate(headers):
        _cell_set_text(table.rows[0].cells[i], h, bold=True,
                       align=WD_ALIGN_PARAGRAPH.CENTER)
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            _cell_set_text(table.rows[r].cells[c], val,
                           align=WD_ALIGN_PARAGRAPH.CENTER
                           if c >= 2 else WD_ALIGN_PARAGRAPH.LEFT)
    if col_widths_cm:
        for col_idx, width in enumerate(col_widths_cm):
            for row in table.rows:
                row.cells[col_idx].width = Cm(width)
    return table


def bullets(doc, items: list[str]):
    for item in items:
        p = _para(doc, "• " + item, first_line_indent=Cm(0), left_indent=Cm(0.5),
                  space_before=0, space_after=0)
    return None


def code_block(doc, code: str, *, filename: str | None = None):
    if filename:
        _para(doc, f"// {filename}", first_line_indent=None,
              italic=True, color=RGBColor(0x55, 0x55, 0x55),
              space_before=8, space_after=2, size=Pt(10))
    for line in code.splitlines() or [""]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_before = Pt(0); pf.space_after = Pt(0)
        pf.first_line_indent = None
        pf.left_indent = Cm(0.5)
        run = p.add_run(line if line else " ")
        _set_run(run, size=SIZE_CODE, font=FONT_MONO)


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
def _setup_section(doc):
    s = doc.sections[0]
    s.top_margin = Cm(2.0)
    s.bottom_margin = Cm(2.0)
    s.left_margin = Cm(3.0)
    s.right_margin = Cm(1.5)
    s.orientation = WD_ORIENT.PORTRAIT


def _set_default_styles(doc):
    style = doc.styles["Normal"]
    style.font.name = FONT_BODY
    style.font.size = SIZE_BODY
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.insert(0, rfonts)
    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        rfonts.set(qn(f"w:{attr}"), FONT_BODY)


# ===========================================================================
# Content
# ===========================================================================
def build_cover(doc):
    centered(doc, "МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ", bold=True,
             size=Pt(14), space_after=2)
    centered(doc, "Природничо-гуманітарний фаховий коледж", space_after=2)
    centered(doc, "ДВНЗ «Ужгородський національний університет»", space_after=18)

    for _ in range(4):
        _para(doc, "")
    centered(doc, "[ПІБ СТУДЕНТА]", bold=True, size=Pt(14), space_after=2)
    centered(doc, "студент 4-го курсу", space_after=2)
    centered(doc, "денної форми навчання", space_after=2)
    centered(doc, "ІНП № [НОМЕР ЗАЛІКОВОЇ КНИЖКИ]", space_after=16)

    centered(doc, "ЗВІТ", bold=True, size=Pt(18), space_after=4)
    centered(doc, "ПРОХОДЖЕННЯ ВИРОБНИЧО-ТЕХНОЛОГІЧНОЇ ПРАКТИКИ",
             bold=True, size=Pt(14), space_after=4)
    centered(doc, "галузь знань 12 «Інформаційні технології»,",
             size=Pt(13), space_after=2)
    centered(doc, "спеціальність 121 «Інженерія програмного забезпечення»",
             size=Pt(13), space_after=14)
    centered(doc,
             "Розробка інформаційної системи управління архітектурними "
             "проєктами на основі канбан-методології «Arch Kanban»",
             bold=True, size=Pt(14), space_after=20)

    for _ in range(2):
        _para(doc, "")
    centered(doc, "Науковий керівник:", space_after=2)
    centered(doc, "Викл. [ПІБ КЕРІВНИКА]", space_after=12)
    centered(doc, "Дата «     »                 2026 р.", space_after=2)
    centered(doc, "Підпис ____________________", space_after=18)
    centered(doc, "Робота захищена «     »                 2026 р.", space_after=2)
    centered(doc, "з оцінкою «     /     /     »", space_after=2)
    centered(doc, "Підписи членів комісії ____________________", space_after=18)
    centered(doc, "Ужгород 2026", bold=True)
    _page_break(doc)


def build_task(doc):
    centered(doc, "Природничо-гуманітарний фаховий коледж", space_after=2)
    centered(doc, "Державного вищого навчального закладу", space_after=2)
    centered(doc, "«Ужгородський національний університет»", space_after=12)
    body_noindent(doc, "Галузь знань: 12 «Інформаційні технології»",
                  align=WD_ALIGN_PARAGRAPH.LEFT)
    body_noindent(doc, "Спеціальність: 121 «Інженерія програмного забезпечення»",
                  align=WD_ALIGN_PARAGRAPH.LEFT)
    body_noindent(doc, "Циклова комісія: Програмування та інформаційні технології",
                  align=WD_ALIGN_PARAGRAPH.LEFT)
    _para(doc, "")
    body_noindent(doc, "ЗАТВЕРДЖУЮ", align=WD_ALIGN_PARAGRAPH.RIGHT)
    body_noindent(doc, "Голова ЦК __________ Н.Л. Лінчук",
                  align=WD_ALIGN_PARAGRAPH.RIGHT)
    body_noindent(doc, "«____» березня 2026 р.", align=WD_ALIGN_PARAGRAPH.RIGHT)
    _para(doc, "")

    centered(doc, "ЗАВДАННЯ", bold=True, size=Pt(16))
    centered(doc, "НА ВИРОБНИЧО-ТЕХНОЛОГІЧНУ ПРАКТИКУ", bold=True)
    centered(doc, "СТУДЕНТОВІ ГРУПИ [НОМЕР ГРУПИ]", bold=True, space_after=6)
    centered(doc, "[ПІБ СТУДЕНТА]", bold=True, space_after=2)
    centered(doc, "(прізвище, ім’я, по батькові)", italic=True,
             size=Pt(11), space_after=12)

    body(doc, "1. Індивідуальне завдання: Розробити інформаційну систему "
              "управління архітектурними проєктами на основі канбан-методології "
              "«Arch Kanban», що забезпечує облік проєктів, етапів робіт, "
              "учасників команди, креслень та коментарів.")
    body(doc, "2. Термін здачі студентом закінченого звіту, програмного "
              "продукту, заповненого щоденника із печатками та характеристикою — "
              "[ДАТА] 2026 року.")
    body(doc, "3. Перелік питань, що їх належить розробити (обґрунтувати) "
              "в процесі проходження практики:")
    bullets(doc, [
        "Опис предметної області та побудова моделі завдання.",
        "Обґрунтування вибору методу розв’язку завдання.",
        "Створення бази даних.",
        "Розробка алгоритму та структури програми.",
        "Написання програмних модулів.",
        "Розробка інструкції для кінцевого користувача.",
        "Тестування та впровадження програмного продукту.",
    ])
    body(doc, "4. Дата видачі завдання _______ березня 2026 року.")
    _para(doc, "")
    body_noindent(doc, "Керівник виробничо-технологічної практики __________________ "
                       "([ПІБ КЕРІВНИКА])")
    body_noindent(doc, "Завдання прийняв до виконання ____________________ "
                       "(___________________________)")
    body_noindent(doc, "                                     (дата)            "
                       "(підпис студента, розшифровка)",
                  align=WD_ALIGN_PARAGRAPH.CENTER)
    _page_break(doc)


def build_toc(doc):
    centered(doc, "ЗМІСТ", bold=True, space_after=10)
    rows = [
        ("ВСТУП", "4"),
        ("КОРОТКІ ВІДОМОСТІ ПРО ПІДПРИЄМСТВО-БАЗУ ПРАКТИКИ", "6"),
        ("1 ТЕОРЕТИЧНА ЧАСТИНА", "7"),
        ("1.1 Загальні відомості про предметну область", "7"),
        ("1.2 Огляд аналогів", "8"),
        ("1.3 Опис предметної області та постановка задачі", "10"),
        ("1.4 Обґрунтування вибору методу розв’язку задачі", "12"),
        ("1.5 Огляд засобів розробки", "13"),
        ("2 ПРАКТИЧНА ЧАСТИНА", "15"),
        ("2.1 Визначення сутностей та їх атрибутів", "15"),
        ("2.2 Архітектура проєкту та взаємодія між об’єктами", "19"),
        ("2.3 Фізична структура програми", "20"),
        ("2.4 Тестування проєкту", "22"),
        ("2.5 Інтерфейс та керівництво користувача", "24"),
        ("ВИСНОВКИ", "32"),
        ("ПЕРЕЛІК ВИКОРИСТАНИХ ДЖЕРЕЛ", "33"),
        ("Додаток 1. Фізична схема", "35"),
        ("Додаток 2. Діаграма Пітера Чена", "36"),
        ("Додаток 3. Лістинг коду", "37"),
    ]
    for title, page in rows:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = p.paragraph_format
        pf.line_spacing = 1.5
        pf.first_line_indent = None
        pf.tab_stops.add_tab_stop(Cm(16.0), alignment=2, leader=1)  # 2=right, 1=dots
        run = p.add_run(title)
        _set_run(run)
        p.add_run("\t")
        run2 = p.add_run(page)
        _set_run(run2)
    _page_break(doc)


def build_intro(doc):
    h_section(doc, "Вступ")
    body(doc,
         "Управління проєктами в архітектурній студії — це робота з великою "
         "кількістю паралельних замовлень, кожне з яких проходить кілька "
         "технічних етапів: від ескізу до фінального передавання креслень "
         "замовнику. У більшості невеликих бюро ця інформація розпорошена "
         "між електронною поштою, месенджерами та локальними дисками, що "
         "ускладнює контроль за термінами та відповідальністю.")
    body(doc,
         "Метою роботи є розробка вебзастосунку «Arch Kanban» — інформаційної "
         "системи управління архітектурними проєктами на основі канбан-методології, "
         "що дозволяє відстежувати рух кожного проєкту колонками етапів, "
         "призначати виконавців, прикріплювати креслення та фіксувати коментарі "
         "учасників команди.")
    body(doc,
         "Об’єктом дослідження є процеси операційного управління проєктами "
         "в архітектурному бюро. Предметом дослідження є методи й програмні "
         "засоби побудови повноцінного SPA-застосунку з бекендом на ASP.NET "
         "Core та фронтендом на React + TypeScript.")
    body(doc, "Для досягнення поставленої мети визначено такі завдання:")
    bullets(doc, [
        "проаналізувати предметну область та існуючі програмні рішення "
        "(Trello, Jira) для управління канбан-дошками;",
        "спроєктувати реляційну структуру бази даних для зберігання "
        "проєктів, етапів, учасників, креслень та коментарів;",
        "реалізувати REST API на ASP.NET Core 10 та Entity Framework Core;",
        "реалізувати односторінковий клієнт (SPA) на React 19 + TypeScript "
        "з підтримкою двох мов інтерфейсу (українська, англійська);",
        "впровадити drag-and-drop переміщення карток між колонками етапів;",
        "впровадити JWT-автентифікацію з трирівневою рольовою моделлю "
        "(Адміністратор, Менеджер, Користувач) та гостьовим режимом перегляду;",
        "забезпечити деплой готового продукту в Docker-контейнер на хостинг Render.",
    ])
    body(doc,
         "Програмний продукт розробляється на сучасному технологічному стеку: "
         "бекенд — ASP.NET Core 10 з Entity Framework Core, фронтенд — React 19 "
         "із TypeScript, Vite та Tailwind CSS v4, drag-and-drop — "
         "@hello-pangea/dnd, локалізація — react-i18next. Як база даних "
         "використовується SQL Server LocalDB (за замовчуванням) або SQLite — "
         "у середовищі розробки та продакшені. Деплой здійснюється "
         "багатоетапним Dockerfile у безкоштовний хостинг Render.")
    body(doc,
         "Очікуваним результатом є функціональний вебзастосунок із чітким "
         "поділом доступу, інтуїтивно зрозумілим інтерфейсом та повним "
         "циклом життя проєктної картки — від створення до завершення.")
    _page_break(doc)


def build_practice_base(doc):
    h_section(doc, "Короткі відомості про підприємство-базу практики")
    body(doc,
         "Базою практики є [НАЗВА ПІДПРИЄМСТВА] — [коротко рід діяльності "
         "(наприклад: архітектурна студія, що спеціалізується на проєктуванні "
         "індивідуальних житлових будинків та невеликих комерційних об’єктів)]. "
         "Підприємство виконує повний цикл робіт — від концепт-ескізу та "
         "узгодження з замовником до випуску робочих креслень і авторського "
         "нагляду на будівельному майданчику.")
    body(doc,
         "Основні напрями діяльності організації:")
    bullets(doc, [
        "розробка ескізних і робочих проєктів житлових та комерційних будівель;",
        "погодження проєктної документації із замовником та підрядниками;",
        "випуск креслень загальнобудівельної частини, вентиляції, "
        "електрики, водопостачання;",
        "ведення авторського нагляду на етапі будівництва.",
    ])
    body(doc,
         "Організаційна структура [НАЗВА ПІДПРИЄМСТВА] включає керівництво, "
         "групу архітекторів, дизайнерів та конструкторів, а також "
         "адміністративний відділ. Команда працює з кількома паралельними "
         "проєктами одночасно, тому процеси планування та контролю термінів "
         "потребують централізованої цифрової підтримки — саме цей запит і "
         "став підставою для розробки системи «Arch Kanban».")
    _page_break(doc)


# ===========================================================================
# Section 1 — Theory
# ===========================================================================
def build_section_1(doc):
    h_section(doc, "1 Теоретична частина")
    h_sub(doc, "1.1 Загальні відомості про предметну область")
    body(doc,
         "Архітектурний проєкт є центральною одиницею обліку в системі та "
         "розглядається як ланцюг технічних завдань зі створення проєктної "
         "документації для об’єкта замовника. Кожен проєкт має чіткий "
         "життєвий цикл, що відображається через систему статусів-етапів: "
         "«Ескіз» → «Погодження замовником» → «Розробка креслень» → «Готово». "
         "Цей цикл — пряме перенесення канбан-методології, де картка "
         "переміщується між колонками в міру виконання робіт.")
    body(doc,
         "Учасниками проєкту в системі є члени команди студії з різними "
         "ролями: архітектори (відповідають за концепцію та загальні рішення), "
         "дизайнери (інтер’єр, фасади) та конструктори (вузли, розрахунки). "
         "Один проєкт може мати декількох призначених виконавців; "
         "один виконавець може бути задіяний у декількох проєктах паралельно "
         "(зв’язок «багато-до-багатьох»).")
    body(doc,
         "Окремими сутностями моделюються креслення (зберігаються як "
         "посилання на зовнішні файли — Google Drive, Dropbox тощо, без "
         "завантаження вмісту на сервер) та коментарі учасників, що "
         "дозволяють відстежувати історію обговорень безпосередньо в "
         "контексті проєкту.")
    body(doc,
         "Кожна картка має пріоритет (Низький / Середній / Високий / Терміновий) "
         "та опційну дату дедлайну. Це дозволяє керівникові швидко виявляти "
         "критичні задачі без зміни самої колонки етапу.")

    h_sub(doc, "1.2 Огляд аналогів")
    body(doc,
         "На сучасному ринку є чимало платформ для управління канбан-дошками. "
         "Перший і найвідоміший аналог — Trello (Atlassian). Це універсальний "
         "сервіс з простим інтерфейсом «дошка — колонка — картка», який "
         "часто беруть як референс для подібних рішень.")
    figure_placeholder(doc, "1.1", "Інтерфейс платформи «Trello»")
    body(doc, "Переваги Trello:")
    bullets(doc, [
        "інтуїтивно зрозумілий drag-and-drop між колонками;",
        "велика екосистема Power-Ups та шаблонів дошок;",
        "безкоштовний тариф, достатній для невеликих команд.",
    ])
    body(doc, "Недоліки Trello для конкретного сценарію архітектурного бюро:")
    bullets(doc, [
        "відсутність специфічних для архітектурної роботи полів "
        "(етапи проєктування, посилання на креслення, замовник);",
        "обмежений безкоштовний тариф щодо інтеграцій та автоматизацій;",
        "налаштування системи доступів і ролей вимагає переходу на платний тариф.",
    ])
    body(doc,
         "Другим аналогом є Jira (Atlassian) — потужна система управління "
         "задачами з широкими можливостями налаштування workflow та "
         "звітності. Вона активно використовується в IT-командах, проте її "
         "складність є радше недоліком для невеликої архітектурної студії.")
    figure_placeholder(doc, "1.2", "Інтерфейс платформи «Jira»")
    body(doc, "Переваги Jira:")
    bullets(doc, [
        "гнучка конфігурація типів задач, полів і workflow;",
        "потужна звітність і аналітика;",
        "інтеграція з усією екосистемою Atlassian.",
    ])
    body(doc, "Недоліки Jira:")
    bullets(doc, [
        "висока складність налаштування та крута крива входу для "
        "нетехнічних користувачів;",
        "інтерфейс перевантажений елементами, не призначеними для "
        "архітектурної специфіки;",
        "платні тарифи навіть для базових сценаріїв із невеликими командами.",
    ])
    body(doc,
         "Висновок за результатами огляду: існуючі рішення — або занадто "
         "загальні (Trello), або занадто складні та орієнтовані на "
         "розробників (Jira). Розробка власної компактної системи «Arch Kanban», "
         "адаптованої під сценарій архітектурної студії (фіксовані етапи "
         "проєктування, спеціалізовані ролі команди, прикріплення посилань на "
         "креслення), є виправданим рішенням, що дозволяє повністю покрити "
         "цільовий сценарій без надлишкової складності.")

    h_sub(doc, "1.3 Опис предметної області та постановка задачі")
    body(doc,
         "Предметна область охоплює діяльність невеликих архітектурних студій, "
         "що ведуть кілька проєктів паралельно. Ключові категорії користувачів "
         "системи «Arch Kanban»:")
    bullets(doc, [
        "адміністратор — має повний доступ, керує користувачами та командою;",
        "менеджер — створює проєкти, призначає виконавців, фіксує прогрес;",
        "користувач (виконавець) — переглядає свої проєкти, оновлює статус, "
        "коментує, прикріплює креслення;",
        "гість (без авторизації) — переглядає публічну дошку та деталі "
        "проєктів у режимі «лише читання», що дозволяє замовнику слідкувати "
        "за процесом без створення облікового запису.",
    ])
    body(doc,
         "Постановка задачі — створення вебзастосунку, що забезпечить:")
    bullets(doc, [
        "візуалізацію проєктів у вигляді канбан-дошки з чотирьох колонок;",
        "drag-and-drop переміщення карток між колонками із збереженням "
        "позиції в БД;",
        "детальну сторінку проєкту з повним набором полів (назва, замовник, "
        "опис, етап, пріоритет, дедлайн), списком виконавців, посиланнями на "
        "креслення та стрічкою коментарів;",
        "автентифікацію за JWT-токеном з трьома рівнями доступу;",
        "повну українську локалізацію інтерфейсу з можливістю перемикання на "
        "англійську без перезавантаження сторінки;",
        "адаптивний дизайн для роботи з настільних і мобільних пристроїв;",
        "розгортання одним Docker-контейнером на хостингу Render.",
    ])

    h_sub(doc, "1.4 Обґрунтування вибору методу розв’язку задачі")
    body(doc,
         "Для розв’язання поставленої задачі обрано клієнт-серверну архітектуру "
         "з чітким поділом на бекенд (REST API) та фронтенд (SPA). Такий "
         "підхід дозволяє паралельно розробляти й тестувати кожну з частин, "
         "забезпечує можливість у майбутньому додати мобільний клієнт без "
         "змін на бекенді, а також полегшує деплой та масштабування.")
    body(doc,
         "Бекенд реалізовано на ASP.NET Core 10 за патерном Controller-Service "
         "із використанням Entity Framework Core як ORM. Для зберігання "
         "даних використовується SQL Server LocalDB (за замовчуванням) або "
         "SQLite (для середовища розробки та продакшен-демо в контейнері). "
         "Автентифікація реалізована за допомогою JSON Web Token (JWT) із "
         "хешуванням паролів через BCrypt.")
    body(doc,
         "Фронтенд побудований як односторінковий застосунок (SPA) на React 19 "
         "з TypeScript. Збирання здійснює Vite, стилізація — Tailwind CSS v4, "
         "маршрутизація — react-router-dom, drag-and-drop — @hello-pangea/dnd "
         "(сучасний форк визнаної бібліотеки react-beautiful-dnd), "
         "локалізація — react-i18next.")
    body(doc,
         "База даних спроєктована на основі ER-моделі та нормалізована до "
         "третьої нормальної форми (3NF). Це дозволило уникнути надмірності "
         "даних та забезпечити цілісність при оновленнях. Зв’язки реалізовано "
         "через зовнішні ключі з каскадним видаленням залежних сутностей "
         "(коментарі, креслення, призначення).")
    body(doc,
         "Деплой реалізовано за допомогою багатоетапного Dockerfile: перший "
         "етап (node:22-alpine) збирає React-білд, другий (dotnet/sdk:10.0) "
         "публікує API, третій (dotnet/aspnet:10.0) запускає кінцевий "
         "контейнер, що віддає і API, і статичний фронтенд з wwwroot. Така "
         "схема дозволяє розгорнути проєкт одним web-сервісом на безкоштовному "
         "тарифі хостингу Render.")

    h_sub(doc, "1.5 Огляд засобів розробки")
    h_subsub(doc, "1.5.1 ASP.NET Core 10 та Entity Framework Core")
    body(doc,
         "ASP.NET Core — кросплатформений вебфреймворк з відкритим вихідним "
         "кодом для побудови сучасних вебзастосунків і вебсервісів на .NET. "
         "Версія 10 надає високопродуктивний веб-сервер Kestrel, вбудовану "
         "підтримку мінімалістичних API, систему ін’єкції залежностей "
         "(Dependency Injection) та проміжне ПЗ (middleware) для авторизації, "
         "CORS, статичних файлів тощо. Мова програмування — C#.")
    body(doc,
         "Entity Framework Core — об’єктно-реляційний маппер (ORM), що "
         "дозволяє працювати з реляційними БД як з колекціями об’єктів C#. "
         "Підтримує LINQ-запити, міграції, lazy/eager loading та кілька "
         "провайдерів баз даних (SQL Server, SQLite, PostgreSQL та інші).")

    h_subsub(doc, "1.5.2 React 19, TypeScript, Vite та Tailwind CSS")
    body(doc,
         "React — JavaScript-бібліотека для побудови користувацьких інтерфейсів "
         "на основі компонентного підходу. Версія 19 додала підтримку Server "
         "Components та поліпшила механізм асинхронного рендеру.")
    body(doc,
         "TypeScript — типізована надбудова над JavaScript, що додає "
         "статичну типізацію та компіляцію в чистий JS. Дозволяє виявляти "
         "помилки на етапі розробки та робить код самодокументованим.")
    body(doc,
         "Vite — сучасний інструмент збірки фронтенд-проєктів, що "
         "використовує нативні ES-модулі браузера для миттєвого Hot Module "
         "Replacement у dev-режимі та Rollup для оптимізованого production-білду.")
    body(doc,
         "Tailmwind CSS v4 — utility-first CSS-фреймворк, що дозволяє "
         "стилізувати компоненти прямо через класи (наприклад, "
         "«bg-brand-600 hover:bg-brand-700 rounded-md») без написання "
         "окремих CSS-файлів. Версія 4 використовує новий компілятор з "
         "інтеграцією через Vite-плагін.")

    h_subsub(doc, "1.5.3 SQL Server LocalDB та SQLite")
    body(doc,
         "SQL Server LocalDB — спрощена версія Microsoft SQL Server для "
         "розробників, що працює як локальний процес без потреби у "
         "встановленні повного сервера. Використовується як основний "
         "провайдер БД у середовищі розробки на Windows.")
    body(doc,
         "SQLite — компактна вбудовувана реляційна СУБД, що зберігає базу "
         "даних в одному файлі. У проєкті використана як альтернативний "
         "провайдер для контейнеризованого розгортання, де простіше "
         "обмежитися одним процесом без зовнішніх залежностей.")

    h_subsub(doc, "1.5.4 Інструменти розробки")
    body(doc,
         "Git — розподілена система контролю версій для відстеження змін у "
         "вихідному коді та координації роботи команди. npm — менеджер "
         "пакетів для Node.js, що використовується для встановлення та "
         "оновлення фронтенд-залежностей. NuGet — менеджер пакетів для .NET, "
         "що обслуговує серверні залежності. Docker — платформа "
         "контейнеризації, що дозволяє запакувати застосунок із усіма його "
         "залежностями в один образ для відтворюваного розгортання. Render — "
         "хмарний хостинг із підтримкою деплою Docker-контейнерів через "
         "інтеграцію з Git-репозиторіями.")
    _page_break(doc)


# ===========================================================================
# Section 2 — Practice
# ===========================================================================
def build_section_2(doc):
    h_section(doc, "2 Практична частина")
    h_sub(doc, "2.1 Визначення сутностей та їх атрибутів")
    body(doc,
         "Для забезпечення обліку архітектурних проєктів та керування "
         "командою спроєктовано концептуальну модель бази даних із шести "
         "сутностей: Project (проєкт), Member (учасник команди), "
         "ProjectMember (зв’язок проєкту з учасниками), Attachment "
         "(прикріплене посилання на креслення) та Comment (коментар).")

    body(doc, "Проєкт (Project). Центральна сутність системи — окрема "
              "архітектурна задача, що рухається колонками канбан-дошки.")
    table_caption(doc, "2.1", "Атрибути сутності «Project»")
    attribute_table(doc,
        ["Назва атрибута", "Опис та призначення", "Ключове поле", "Обов’язковість"],
        [
            ["Id", "Унікальний ідентифікатор проєкту", "Так", "Так"],
            ["Title", "Назва проєкту (наприклад, «Вілла в Ужгороді»)", "Ні", "Так"],
            ["ClientName", "Замовник, для якого виконується проєкт", "Ні", "Ні"],
            ["Description", "Розширений опис, ТЗ або примітки", "Ні", "Ні"],
            ["Stage", "Колонка дошки (Sketch / ClientApproval / Drawings / Done)",
             "Ні", "Так"],
            ["Priority", "Пріоритет (Low / Medium / High / Urgent)", "Ні", "Так"],
            ["Position", "Порядкова позиція в межах своєї колонки", "Ні", "Так"],
            ["DueDate", "Опційний дедлайн", "Ні", "Ні"],
            ["CreatedAt", "Дата створення картки", "Ні", "Так"],
        ],
        col_widths_cm=[3.4, 7.0, 2.4, 2.4],
    )

    table_caption(doc, "2.2", "Зв’язки сутності «Project»")
    attribute_table(doc,
        ["Пов’язана сутність", "Тип зв’язку", "Призначення"],
        [
            ["Member", "Багато до багатьох (через ProjectMember)",
             "Один проєкт має кількох виконавців; один виконавець — у "
             "кількох проєктах"],
            ["Attachment", "Один до багатьох",
             "Проєкт може мати декілька посилань на креслення"],
            ["Comment", "Один до багатьох",
             "Стрічка коментарів у межах проєкту"],
        ],
        col_widths_cm=[4.0, 4.5, 6.7],
    )

    body(doc, "Учасник команди (Member). Зберігає інформацію про людину, "
              "яка має обліковий запис у системі.")
    table_caption(doc, "2.3", "Атрибути сутності «Member»")
    attribute_table(doc,
        ["Назва атрибута", "Опис та призначення", "Ключове поле", "Обов’язковість"],
        [
            ["Id", "Унікальний ідентифікатор користувача", "Так", "Так"],
            ["Name", "Ім’я та прізвище для відображення", "Ні", "Так"],
            ["Role", "Професійна роль (Architect / Designer / Constructor)",
             "Ні", "Так"],
            ["Username", "Логін для входу в систему", "Ні", "Так"],
            ["PasswordHash", "Хеш пароля (BCrypt)", "Ні", "Так"],
            ["AccessLevel", "Рівень доступу (User / Manager / Admin)",
             "Ні", "Так"],
        ],
        col_widths_cm=[3.4, 7.0, 2.4, 2.4],
    )

    table_caption(doc, "2.4", "Зв’язки сутності «Member»")
    attribute_table(doc,
        ["Пов’язана сутність", "Тип зв’язку", "Призначення"],
        [
            ["Project", "Багато до багатьох (через ProjectMember)",
             "Учасник може бути призначений на кілька проєктів"],
            ["Comment", "Логічний зв’язок за полем Author",
             "Коментар автоматично підписується іменем "
             "автентифікованого користувача"],
        ],
        col_widths_cm=[4.0, 5.5, 5.7],
    )

    body(doc, "Зв’язок проєкту й учасника (ProjectMember). Допоміжна "
              "сутність-«стик» для реалізації багато-до-багатьох між "
              "Project та Member.")
    table_caption(doc, "2.5", "Атрибути сутності «ProjectMember»")
    attribute_table(doc,
        ["Назва атрибута", "Опис та призначення", "Ключове поле", "Обов’язковість"],
        [
            ["ProjectId", "Посилання на проєкт",
             "Так (складений)", "Так"],
            ["MemberId", "Посилання на учасника",
             "Так (складений)", "Так"],
        ],
        col_widths_cm=[3.4, 7.0, 2.4, 2.4],
    )

    body(doc, "Посилання на креслення (Attachment). Зберігає назву та URL "
              "зовнішнього файлу (Google Drive, Dropbox, OneDrive тощо). "
              "Завантаження бінарного вмісту в систему не передбачено для "
              "спрощення архітектури.")
    table_caption(doc, "2.6", "Атрибути сутності «Attachment»")
    attribute_table(doc,
        ["Назва атрибута", "Опис та призначення", "Ключове поле", "Обов’язковість"],
        [
            ["Id", "Унікальний ідентифікатор посилання", "Так", "Так"],
            ["ProjectId", "Зовнішній ключ на проєкт", "Ні", "Так"],
            ["Label", "Підпис посилання (наприклад, «Поверхневий план»)",
             "Ні", "Так"],
            ["Url", "Адреса зовнішнього файлу", "Ні", "Так"],
        ],
        col_widths_cm=[3.4, 7.0, 2.4, 2.4],
    )

    body(doc, "Коментар (Comment). Фіксує обговорення в межах конкретного "
              "проєкту. Автор підставляється автоматично з JWT-токена.")
    table_caption(doc, "2.7", "Атрибути сутності «Comment»")
    attribute_table(doc,
        ["Назва атрибута", "Опис та призначення", "Ключове поле", "Обов’язковість"],
        [
            ["Id", "Унікальний ідентифікатор коментаря", "Так", "Так"],
            ["ProjectId", "Зовнішній ключ на проєкт", "Ні", "Так"],
            ["Author", "Ім’я автора (з JWT-токена)", "Ні", "Так"],
            ["Text", "Текст коментаря", "Ні", "Так"],
            ["CreatedAt", "Дата й час публікації", "Ні", "Так"],
        ],
        col_widths_cm=[3.4, 7.0, 2.4, 2.4],
    )

    body(doc,
         "У цьому розділі визначено склад сутностей концептуальної схеми, "
         "встановлено атрибути та зв’язки. Описана структура нормалізована "
         "до третьої нормальної форми та повністю відповідає бізнес-логіці "
         "архітектурного бюро.")

    # ----- 2.2 Architecture -----
    h_sub(doc, "2.2 Архітектура проєкту та взаємодія між об’єктами")
    body(doc,
         "Архітектура «Arch Kanban» побудована за клієнт-серверним принципом "
         "з повним поділом на бекенд (ASP.NET Core 10 Web API) та "
         "фронтенд (React 19 + TypeScript SPA). Обидві частини взаємодіють "
         "виключно через JSON REST API, що уніфікує контракт та дозволяє "
         "змінювати клієнт без модифікації серверної логіки.")
    body(doc, "Бекенд реалізує такі шари:")
    bullets(doc, [
        "Models — POCO-класи (Project, Member, ProjectMember, Attachment, "
        "Comment) та переліки (Stage, Role, Priority, AccessLevel);",
        "Data — AppDbContext (Entity Framework Core) і DbSeeder, що "
        "наповнює базу демонстраційними даними при першому запуску;",
        "Dtos — Data Transfer Objects, що відокремлюють внутрішню модель "
        "від API-контракту;",
        "Controllers — три головні контролери (AuthController, "
        "ProjectsController, MembersController) та допоміжний "
        "AttachmentsController;",
        "Auth — TokenService для випуску JWT-токенів і налаштування "
        "middleware автентифікації у Program.cs.",
    ])
    body(doc,
         "Фронтенд організовано модульно за стандартними категоріями для "
         "React-застосунку:")
    bullets(doc, [
        "pages/ — повноекранні маршрути (BoardPage, ProjectDetailPage, "
        "MembersPage, LoginPage);",
        "components/ — перевикористовувані елементи UI (Navbar, Column, "
        "ProjectCard, CreateProjectModal, AssigneeDropdown);",
        "auth/ — контекст автентифікації, сховище токена в localStorage та "
        "ProtectedRoute для захищених маршрутів;",
        "api/ — типізовані axios-клієнти для кожного контролера;",
        "i18n/ — конфігурація react-i18next та файли перекладу uk.json / en.json;",
        "types.ts — TypeScript-типи, що відповідають серверним DTO.",
    ])
    body(doc,
         "Автентифікація відбувається за такою схемою: користувач вводить "
         "логін і пароль у LoginPage → клієнт надсилає POST /api/auth/login → "
         "сервер перевіряє пароль через BCrypt та видає підписаний JWT-токен → "
         "клієнт зберігає токен у localStorage та автоматично додає заголовок "
         "Authorization: Bearer ... до всіх наступних запитів. Всі мутації "
         "(POST/PUT/PATCH/DELETE) у контролерах захищені атрибутом [Authorize]; "
         "GET-методи відкриті для гостьового перегляду через [AllowAnonymous].")
    body(doc,
         "Drag-and-drop переміщення карток реалізовано на основі бібліотеки "
         "@hello-pangea/dnd. При відпусканні картки клієнт виконує оптимістичне "
         "оновлення локального стану, після чого надсилає PATCH "
         "/api/projects/{id}/move з новим етапом і позицією. У разі помилки "
         "стан відкочується до знімка перед перетягуванням.")

    # ----- 2.3 Physical structure -----
    h_sub(doc, "2.3 Фізична структура програми")
    body(doc,
         "Програмний комплекс «Arch Kanban» організований як монорепозиторій "
         "із двома кореневими підпапками — server/ (бекенд) та client/ (фронтенд). "
         "Корінь репозиторію також містить файли деплою (Dockerfile, "
         ".dockerignore, render.yaml) та документацію (README.md).")
    figure_placeholder(doc, "2.1", "Структура кореневого каталогу проєкту")
    body(doc,
         "Опис основних каталогів і файлів:")
    bullets(doc, [
        "server/ — ASP.NET Core 10 Web API, що містить контролери, моделі, "
        "DbContext, сидер БД та налаштування JWT;",
        "client/ — React + TypeScript SPA, що збирається Vite у статичний "
        "набір файлів та віддається ASP.NET у проді;",
        "Dockerfile — багатоетапний образ: node:22 збирає клієнт, "
        "dotnet/sdk:10.0 публікує API, dotnet/aspnet:10.0 запускає "
        "контейнер;",
        ".dockerignore — виключає bin/obj/node_modules та локальні артефакти "
        "з контексту збірки;",
        "render.yaml — Render Blueprint: конфігурація web-сервісу, регіону, "
        "змінних оточення та healthcheck-маршруту;",
        "README.md — повна документація з інструкціями запуску та деплою.",
    ])
    figure_placeholder(doc, "2.2", "Вміст каталогу «server»")
    body(doc,
         "Вміст каталогу server/ організовано за функціональним призначенням:")
    bullets(doc, [
        "Models/ — POCO-класи сутностей: Project, Member, ProjectMember, "
        "Attachment, Comment, плюс перерахування Stage, Role, Priority, "
        "AccessLevel;",
        "Data/ — AppDbContext із конфігурацією зв’язків та індексів і "
        "DbSeeder з демо-даними;",
        "Dtos/ — record-типи для контрактів API "
        "(ProjectDto, MemberDto, LoginRequest тощо);",
        "Controllers/ — AuthController, ProjectsController, "
        "MembersController, AttachmentsController;",
        "Auth/TokenService.cs — клас для випуску й валідації JWT;",
        "Program.cs — налаштування DI, EF Core, JWT, CORS та статичних файлів;",
        "appsettings.json / appsettings.Development.json — конфігурація "
        "провайдера БД (SQL Server LocalDB або SQLite).",
    ])
    figure_placeholder(doc, "2.3", "Вміст каталогу «server/Controllers»")
    figure_placeholder(doc, "2.4", "Вміст каталогу «server/Models»")
    body(doc,
         "Вміст каталогу client/src/ організовано за стандартом для React-SPA:")
    figure_placeholder(doc, "2.5", "Вміст каталогу «client/src»")
    bullets(doc, [
        "pages/ — BoardPage.tsx, ProjectDetailPage.tsx, MembersPage.tsx, "
        "LoginPage.tsx;",
        "components/ — Navbar.tsx, Column.tsx, ProjectCard.tsx, "
        "CreateProjectModal.tsx, AssigneeDropdown.tsx, priority.ts;",
        "api/ — клієнти client.ts (axios із інтерсепторами JWT), "
        "auth.ts, projects.ts, members.ts;",
        "auth/ — AuthContext.tsx (React Context із поточним користувачем), "
        "ProtectedRoute.tsx, storage.ts;",
        "i18n/ — index.ts (конфігурація i18next), uk.json, en.json;",
        "App.tsx — кореневий компонент із маршрутизацією;",
        "main.tsx — точка входу;",
        "types.ts — TypeScript-типи, що віддзеркалюють серверні DTO.",
    ])

    # ----- 2.4 Testing -----
    h_sub(doc, "2.4 Тестування проєкту")
    body(doc,
         "Тестування системи проводилося мануально через інтерфейс у "
         "браузерах Chrome та Edge. Як основну тестову БД використовувалася "
         "SQLite (файл archkanban.db в каталозі server/), що не потребує "
         "окремого серверного процесу та автоматично перестворюється при "
         "запуску завдяки виклику db.Database.EnsureCreated().")
    body(doc,
         "Першим етапом перевірялися сценарії автентифікації:")
    bullets(doc, [
        "успішний вхід під трьома демо-обліковими записами "
        "(admin/admin — адміністратор, olena/pass — менеджер, "
        "taras/pass — користувач);",
        "відхилення некоректних облікових даних із відображенням повідомлення;",
        "автоматичне перенаправлення на сторінку логіну при отриманні 401 "
        "від API завдяки interceptor-у axios;",
        "автоматичне зникнення авторизаційних кнопок у гостьовому режимі "
        "після очищення localStorage.",
    ])
    figure_placeholder(doc, "2.6", "Валідація даних при авторизації")
    body(doc,
         "Валідація форм реалізована на двох рівнях. На клієнті використовуються "
         "вбудовані механізми React (обов’язкові поля, мінімальна довжина, "
         "формати), на сервері — перевірка моделей у контролерах із "
         "відповідями BadRequest / Conflict. Помилки відображаються у "
         "вигляді червоних бейджів під формою без перезавантаження сторінки.")
    figure_placeholder(doc, "2.7", "Валідація форми створення проєкту")
    figure_placeholder(doc, "2.8", "Перевірка прав доступу — анонімна "
                                    "спроба зміни даних повертає 401")
    body(doc,
         "Окремо було проведено перевірку матриці доступів за допомогою "
         "curl-команд: усі GET-ендпоїнти для проєктів і учасників повертають "
         "200 для анонімного запиту, а будь-які мутації (POST, PUT, PATCH, "
         "DELETE) — 401 Unauthorized. Це підтверджує коректну роботу "
         "атрибутів [Authorize] та [AllowAnonymous] на контролерах.")
    body(doc,
         "Інтеграційне тестування деплою виконано локально через Docker: "
         "виконання команди docker build створює образ за багатоетапним "
         "Dockerfile, після чого docker run піднімає контейнер на порту 8080. "
         "Перевірка кінцевих точок /, /health, /api/projects, "
         "/projects/{id} (SPA deep-link) підтвердила коректну роботу як API, "
         "так і відображення статичного фронтенду з wwwroot/.")

    # ----- 2.5 UI / user guide -----
    h_sub(doc, "2.5 Інтерфейс та керівництво користувача")
    body(doc,
         "Для розгортання системи у середовищі розробки необхідно мати "
         "встановлений .NET 10 SDK, Node.js 20+ і npm. Послідовність кроків:")
    bullets(doc, [
        "клонувати репозиторій і перейти в його корінь;",
        "запустити бекенд: cd server && dotnet run — API підніметься на "
        "http://localhost:5080;",
        "у іншому терміналі запустити фронтенд: cd client && npm install && "
        "npm run dev — клієнт відкриється на http://localhost:5173.",
    ])
    body(doc,
         "При першому запуску бекенд автоматично створює базу даних та "
         "наповнює її демо-даними: 5 учасників команди, 4 проєкти в різних "
         "колонках, 3 коментарі та 3 посилання на креслення.")
    body(doc,
         "Інтерфейс системи побудований за принципом мінімалізму та "
         "доступний за адресою http://localhost:5173 (або за публічним URL "
         "при деплої на Render).")

    body(doc,
         "Стартова сторінка системи — публічна канбан-дошка, що доступна "
         "для гостьового перегляду без авторизації. У правому верхньому "
         "куті — мовний перемикач UK / EN та кнопка «Увійти».")
    figure_placeholder(doc, "2.9", "Головна сторінка в гостьовому режимі "
                                    "(перегляд без авторизації)")
    body(doc,
         "Натискання кнопки «Увійти» відкриває сторінку авторизації. "
         "Користувач вводить логін і пароль. Для ознайомлення з функціоналом "
         "можна скористатися демо-обліковими записами:")
    bullets(doc, [
        "Адміністратор. Логін: admin. Пароль: admin;",
        "Менеджер. Логін: olena. Пароль: pass;",
        "Користувач. Логін: taras. Пароль: pass.",
    ])
    figure_placeholder(doc, "2.10", "Сторінка авторизації")
    body(doc,
         "Альтернативно гість може натиснути посилання «Продовжити як гість» "
         "і повернутися до публічної дошки без створення сесії.")
    body(doc,
         "Після успішної авторизації відкривається повна канбан-дошка з "
         "чотирьох колонок («Ескіз», «Погодження замовником», «Розробка "
         "креслень», «Готово»). Кожна картка показує назву проєкту, "
         "замовника, дедлайн, кольоровий маркер пріоритету та аватари "
         "призначених виконавців.")
    figure_placeholder(doc, "2.11", "Головна сторінка (адміністратор)")
    body(doc,
         "Картки можна перетягувати між колонками — статус проєкту "
         "оновлюється автоматично з оптимістичною підсвіткою.")
    figure_placeholder(doc, "2.12", "Drag-and-drop переміщення картки")
    body(doc,
         "Кнопка «+ Новий проєкт» у правому верхньому куті відкриває "
         "мінімалістичну модалку з основними полями (назва, колонка, "
         "пріоритет, дедлайн). Після створення користувача автоматично "
         "перенаправляє на детальну сторінку проєкту.")
    figure_placeholder(doc, "2.13", "Модальне вікно створення проєкту")
    body(doc,
         "Детальна сторінка проєкту складається з двох колонок. Зліва — "
         "редагована назва, опис, секція посилань на креслення та стрічка "
         "коментарів. Справа — бокова панель із селектами етапу, пріоритету, "
         "полями замовника та дедлайну, а також блоком призначених учасників "
         "з можливістю додати нового через дропдаун.")
    figure_placeholder(doc, "2.14", "Детальна сторінка проєкту")
    figure_placeholder(doc, "2.15", "Додавання учасника через дропдаун")
    figure_placeholder(doc, "2.16", "Додавання посилання на креслення")
    figure_placeholder(doc, "2.17", "Стрічка коментарів та форма додавання")
    body(doc,
         "Гість, що відкриває детальну сторінку, бачить її в режимі "
         "read-only: усі поля вимкнено, кнопки збереження/видалення приховано, "
         "а на самому верху сторінки відображено бурштинову банер-плашку "
         "«Ви переглядаєте проєкт як гість. Увійдіть, щоб редагувати» з "
         "кнопкою «Увійти», що зберігає URL поточного проєкту для повернення.")
    figure_placeholder(doc, "2.18", "Гостьовий режим — детальна сторінка "
                                     "у режимі «лише читання»")
    body(doc,
         "Розділ «Команда» доступний лише авторизованим користувачам. "
         "Адміністратор і менеджер бачать форму додавання нового учасника "
         "(ім’я, роль, логін, пароль, рівень доступу) та кнопки видалення "
         "поряд із кожним записом. Звичайні користувачі бачать лише список "
         "у режимі перегляду.")
    figure_placeholder(doc, "2.19", "Сторінка «Команда» (адміністратор)")
    figure_placeholder(doc, "2.20", "Форма додавання нового учасника")
    body(doc,
         "Перемикач мови у правому верхньому куті дозволяє миттєво "
         "перемикатися між українською та англійською без перезавантаження "
         "сторінки. Вибір зберігається в localStorage та автоматично "
         "застосовується при наступному відкритті сайту.")
    figure_placeholder(doc, "2.21", "Інтерфейс англійською мовою")
    body(doc,
         "Завдяки використанню Tailwind CSS інтерфейс адаптивно "
         "відображається як на настільних, так і на мобільних пристроях. "
         "На вузьких екранах колонки канбан-дошки переходять у вертикальний "
         "стек, а навігаційна панель ущільнюється.")
    figure_placeholder(doc, "2.22", "Адаптивний відгук на мобільному пристрої")
    body(doc,
         "Готовий продукт розгорнуто на безкоштовному тарифі Render через "
         "багатоетапний Docker-контейнер. Конфігурація описана у файлі "
         "render.yaml: один web-сервіс, регіон Frankfurt, провайдер БД — "
         "SQLite, healthcheck на /health. Будь-який git push у гілку main "
         "автоматично запускає новий деплой.")
    figure_placeholder(doc, "2.23", "Деплой на Render — панель сервісу")
    body(doc,
         "Розроблений інтерфейс повністю відповідає вимогам мінімалістичного "
         "канбан-сервісу: всі ключові операції (drag-and-drop, створення, "
         "редагування, коментування, призначення виконавців) виконуються "
         "за один клік або одне перетягування. Розмежування доступу "
         "Адміністратор / Менеджер / Користувач / Гість реалізовано як на "
         "рівні UI, так і на рівні API.")
    _page_break(doc)


# ===========================================================================
# Conclusions, references, appendices
# ===========================================================================
def build_conclusions(doc):
    h_section(doc, "Висновки")
    body(doc,
         "У ході виконання роботи розроблено інформаційну систему «Arch Kanban», "
         "призначену для управління архітектурними проєктами на основі "
         "канбан-методології. Створений програмний продукт повністю покриває "
         "цикл життя архітектурного проєкту: від створення картки на етапі "
         "ескізу до її переміщення в колонку «Готово».")
    body(doc, "Основні результати роботи:")
    bullets(doc, [
        "проаналізовано предметну область і порівняно існуючі рішення "
        "(Trello, Jira), обґрунтовано доцільність розробки власного "
        "спеціалізованого продукту;",
        "спроєктовано реляційну структуру бази даних із шести сутностей, "
        "нормалізовану до 3NF, з повним покриттям зв’язків між проєктом, "
        "учасниками, кресленнями та коментарями;",
        "реалізовано REST API на ASP.NET Core 10 та Entity Framework Core "
        "з JWT-автентифікацією та трьома рівнями доступу;",
        "реалізовано SPA на React 19 + TypeScript з drag-and-drop "
        "переміщенням карток, повноекранною детальною сторінкою проєкту, "
        "стрічкою коментарів і керуванням командою;",
        "впроваджено двомовний інтерфейс (українська/англійська) з "
        "перемиканням «на льоту»;",
        "впроваджено гостьовий режим — публічний перегляд канбан-дошки та "
        "детальних сторінок без авторизації, що дозволяє замовнику стежити "
        "за процесом без створення облікового запису;",
        "впроваджено повний цикл деплою через багатоетапний Docker-контейнер "
        "у безкоштовний хостинг Render із healthcheck та автоматичним "
        "оновленням на git push.",
    ])
    body(doc,
         "Під час роботи над проєктом отримано практичні навички розробки "
         "клієнт-серверних SPA-застосунків, проєктування реляційних БД, "
         "інтеграції JWT-автентифікації, конфігурації Docker-контейнерів і "
         "розгортання продукту в хмарному середовищі.")
    body(doc,
         "Перспективи подальшого розвитку системи: додавання модуля "
         "сповіщень про зміну статусу або призначення на проєкт, реалізація "
         "повноцінного завантаження файлів креслень у вбудоване сховище, "
         "впровадження аналітичних віджетів (середній час виконання етапу, "
         "продуктивність учасника) та інтеграція з зовнішніми календарями "
         "(Google Calendar, Outlook).")
    _page_break(doc)


def build_references(doc):
    h_section(doc, "Перелік використаних джерел")
    refs = [
        "Trello — Manage Your Team’s Projects From Anywhere. Atlassian. "
        "URL: https://trello.com/ (дата звернення: 10.04.2026).",
        "Jira Software — Issue & Project Tracking Software. Atlassian. "
        "URL: https://www.atlassian.com/software/jira (дата звернення: 10.04.2026).",
        "Atlassian. What is Kanban? URL: "
        "https://www.atlassian.com/agile/kanban (дата звернення: 11.04.2026).",
        "Microsoft Docs. .NET 10 release notes. URL: "
        "https://learn.microsoft.com/dotnet/core/whats-new/dotnet-10/overview "
        "(дата звернення: 12.04.2026).",
        "Microsoft Docs. ASP.NET Core fundamentals. URL: "
        "https://learn.microsoft.com/aspnet/core/fundamentals "
        "(дата звернення: 12.04.2026).",
        "Microsoft Docs. Entity Framework Core overview. URL: "
        "https://learn.microsoft.com/ef/core/ (дата звернення: 13.04.2026).",
        "React Documentation. URL: https://react.dev/ "
        "(дата звернення: 13.04.2026).",
        "TypeScript Handbook. URL: "
        "https://www.typescriptlang.org/docs/handbook/intro.html "
        "(дата звернення: 14.04.2026).",
        "Vite Guide. Next Generation Frontend Tooling. URL: "
        "https://vitejs.dev/guide/ (дата звернення: 14.04.2026).",
        "Tailwind CSS v4 Documentation. URL: "
        "https://tailwindcss.com/docs (дата звернення: 15.04.2026).",
        "SQLite Documentation. Appropriate Uses For SQLite. URL: "
        "https://sqlite.org/whentouse.html (дата звернення: 15.04.2026).",
        "@hello-pangea/dnd. Beautiful and accessible drag and drop for "
        "lists with React. URL: https://github.com/hello-pangea/dnd "
        "(дата звернення: 16.04.2026).",
        "react-i18next Documentation. URL: "
        "https://react.i18next.com/ (дата звернення: 16.04.2026).",
        "JWT Introduction. URL: https://jwt.io/introduction "
        "(дата звернення: 17.04.2026).",
        "Render Documentation. Deploy Docker Containers. URL: "
        "https://render.com/docs/docker (дата звернення: 17.04.2026).",
        "Docker Documentation. Multi-stage builds. URL: "
        "https://docs.docker.com/build/building/multi-stage/ "
        "(дата звернення: 17.04.2026).",
        "Програма виробничо-технологічної практики для студентів денної "
        "форми навчання галузі знань 12 «Інформаційні технології», "
        "спеціальності 121 «Інженерія програмного забезпечення». "
        "Ужгород, 2026 р.",
    ]
    for i, ref in enumerate(refs, start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = p.paragraph_format
        pf.line_spacing = 1.5
        pf.first_line_indent = Cm(-0.75)
        pf.left_indent = Cm(0.75)
        pf.space_after = Pt(4)
        run = p.add_run(f"{i}. {ref}")
        _set_run(run)
    _page_break(doc)


def build_appendix_1(doc):
    h_section(doc, "Додаток 1. Фізична схема бази даних")
    body(doc,
         "Фізична схема бази даних «Arch Kanban» представлена нижче. "
         "Схема відображає таблиці, поля з типами даних та зв’язки між "
         "ними через зовнішні ключі.")
    figure_placeholder(doc, "Д.1.1",
                       "Фізична схема бази даних «Arch Kanban»",
                       height_hint="≈700px")
    _page_break(doc)


def build_appendix_2(doc):
    h_section(doc, "Додаток 2. Діаграма Пітера Чена")
    body(doc,
         "Концептуальна ER-діаграма у нотації Пітера Чена відображає "
         "сутності системи (Project, Member, Attachment, Comment) та зв’язки "
         "між ними з відповідними картинами потужностей.")
    figure_placeholder(doc, "Д.2.1",
                       "ER-діаграма системи «Arch Kanban» (нотація Пітера Чена)",
                       height_hint="≈700px")
    _page_break(doc)


# ----- Code listings -----
PROJECT_MODEL_CODE = '''namespace ArchKanban.Api.Models;

public class Project
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string ClientName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public Stage Stage { get; set; }
    public Priority Priority { get; set; } = Priority.Medium;
    public int Position { get; set; }
    public DateTime? DueDate { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public List<ProjectMember> ProjectMembers { get; set; } = new();
    public List<Attachment> Attachments { get; set; } = new();
    public List<Comment> Comments { get; set; } = new();
}
'''

PROGRAM_CS_CODE = '''var builder = WebApplication.CreateBuilder(args);

var port = Environment.GetEnvironmentVariable("PORT");
if (!string.IsNullOrEmpty(port))
    builder.WebHost.UseUrls($"http://0.0.0.0:{port}");

builder.Services.AddControllers().AddJsonOptions(o =>
    o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));

var provider = builder.Configuration["Database:Provider"] ?? "SqlServer";
builder.Services.AddDbContext<AppDbContext>(opts =>
    provider.Equals("Sqlite", StringComparison.OrdinalIgnoreCase)
        ? opts.UseSqlite(connectionString)
        : opts.UseSqlServer(connectionString));

builder.Services.AddSingleton<TokenService>();
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(opts => opts.TokenValidationParameters = new()
    {
        IssuerSigningKey = TokenService.GetKey(),
        ValidateIssuer = false, ValidateAudience = false,
        ValidateLifetime = true,
    });
builder.Services.AddAuthorization();

var app = builder.Build();
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
    DbSeeder.Seed(db);
}

app.UseDefaultFiles();
app.UseStaticFiles();
app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
app.MapControllers();
app.MapFallbackToFile("index.html");

app.Run();
'''

PROJECTS_CONTROLLER_CODE = '''[ApiController, Authorize, Route("api/projects")]
public class ProjectsController(AppDbContext db) : ControllerBase
{
    [HttpGet, AllowAnonymous]
    public async Task<ActionResult<IEnumerable<ProjectDto>>> GetAll() =>
        Ok((await db.Projects
                .Include(p => p.Attachments)
                .Include(p => p.Comments)
                .Include(p => p.ProjectMembers).ThenInclude(pm => pm.Member)
                .OrderBy(p => p.Stage).ThenBy(p => p.Position)
                .ToListAsync()).Select(ToDto));

    [HttpPatch("{id:int}/move")]
    public async Task<IActionResult> Move(int id, MoveProjectRequest req)
    {
        var project = await db.Projects.FindAsync(id);
        if (project is null) return NotFound();
        project.Stage = req.Stage;
        // resequence positions in source and target columns ...
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpPost("{id:int}/comments")]
    public async Task<ActionResult<CommentDto>> AddComment(int id, CreateCommentRequest req)
    {
        var author = User.FindFirstValue(ClaimTypes.Name) ?? "Unknown";
        var comment = new Comment { ProjectId = id, Author = author, Text = req.Text };
        db.Comments.Add(comment);
        await db.SaveChangesAsync();
        return Ok(new CommentDto(comment.Id, comment.Author, comment.Text, comment.CreatedAt));
    }
}
'''

APP_TSX_CODE = '''export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AppShell />}>
            <Route path="/" element={<BoardPage />} />
            <Route path="/projects/:id" element={<ProjectDetailPage />} />
            <Route path="/members" element={
              <ProtectedRoute><MembersPage /></ProtectedRoute>} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
'''

BOARD_DRAG_CODE = '''const onDragEnd = useCallback(async (result: DropResult) => {
  if (isGuest) return
  const { source, destination, draggableId } = result
  if (!destination) return
  // optimistic update of local state
  const snapshot = projects
  const next = reorder(projects, source, destination)
  setProjects(next)
  try {
    await projectsApi.move(Number(draggableId),
      destination.droppableId as Stage, destination.index)
  } catch {
    setProjects(snapshot)
  }
}, [projects, isGuest])
'''

DOCKERFILE_CODE = '''FROM node:22-alpine AS client
WORKDIR /src/client
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
RUN npm run build

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS server
WORKDIR /src
COPY server/*.csproj ./
RUN dotnet restore
COPY server/ ./
RUN dotnet publish -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=server /app/publish ./
COPY --from=client /src/client/dist ./wwwroot
ENV ASPNETCORE_ENVIRONMENT=Production \\
    Database__Provider=Sqlite \\
    ConnectionStrings__DefaultConnection="Data Source=archkanban.db"
EXPOSE 8080
ENTRYPOINT ["dotnet", "ArchKanban.Api.dll"]
'''


def build_appendix_3(doc):
    h_section(doc, "Додаток 3. Лістинг коду")
    body(doc,
         "У додатку наведено ключові фрагменти вихідного коду системи "
         "«Arch Kanban». Повний код проєкту доступний у репозиторії.")

    h_sub(doc, "1. server/Models/Project.cs — модель проєкту")
    code_block(doc, PROJECT_MODEL_CODE, filename="server/Models/Project.cs")

    h_sub(doc, "2. server/Program.cs — налаштування ASP.NET Core")
    code_block(doc, PROGRAM_CS_CODE, filename="server/Program.cs")

    h_sub(doc, "3. server/Controllers/ProjectsController.cs — основні методи")
    code_block(doc, PROJECTS_CONTROLLER_CODE,
               filename="server/Controllers/ProjectsController.cs")

    h_sub(doc, "4. client/src/App.tsx — маршрутизація")
    code_block(doc, APP_TSX_CODE, filename="client/src/App.tsx")

    h_sub(doc, "5. client/src/pages/BoardPage.tsx — обробка drag-and-drop")
    code_block(doc, BOARD_DRAG_CODE, filename="client/src/pages/BoardPage.tsx")

    h_sub(doc, "6. Dockerfile — багатоетапний образ для деплою")
    code_block(doc, DOCKERFILE_CODE, filename="Dockerfile")


# ===========================================================================
# Build it all
# ===========================================================================
def main():
    doc = Document()
    _setup_section(doc)
    _set_default_styles(doc)

    build_cover(doc)
    build_task(doc)
    build_toc(doc)
    build_intro(doc)
    build_practice_base(doc)
    build_section_1(doc)
    build_section_2(doc)
    build_conclusions(doc)
    build_references(doc)
    build_appendix_1(doc)
    build_appendix_2(doc)
    build_appendix_3(doc)

    out_path = Path(__file__).resolve().parent.parent / "report_archkanban.docx"
    doc.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
