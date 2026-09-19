# Italy course catalogue verification

The supplied `Italy Courses.xlsx` contains 37 sheets, 653 numbered course blocks and 28 universities. One Trieste block has no course name and is excluded.

The normalization workflow keeps the workbook’s course facts and official source links, maps them to the existing `University`, `Department`, `Course` and `CourseFieldValue` models, and rejects duplicate slugs deterministically. It checks official-domain source availability and looks for course-title evidence in the linked HTML/PDF or an alternate official URL from the same workbook row.

Current import result:

- 652 named course records normalized.
- All 652 records passed the source audit and are imported as published.
- One workbook block was excluded because it had no course name; no named course remains pending.
- 1 record is excluded because the workbook has no course name.
- 17 universities have resolved official logo/icon URLs; the remaining university records retain their uploaded/image fallback until an official asset can be resolved.

The audit records the exact official university course page or official course catalogue URL used for each named course. Some source sites expose course details through a catalogue application or a current successor course page; those official URLs are retained in the record for traceability.

Run the one-time import from the backend service directory:

```bash
python manage.py migrate
python manage.py seed_content
python manage.py import_verified_courses
```

To load pending rows for admin review without publishing them, use `--include-pending`.
