# Italy course catalogue verification

The supplied `Italy Courses.xlsx` contains 37 sheets, 653 numbered course blocks and 28 universities. One Trieste block has no course name and is excluded.

The normalization workflow keeps the workbook’s course facts and official source links, maps them to the existing `University`, `Department`, `Course` and `CourseFieldValue` models, and rejects duplicate slugs deterministically. It checks official-domain source availability and looks for course-title evidence in the linked HTML/PDF or an alternate official URL from the same workbook row.

Current import result:

- 652 named course records normalized.
- 588 records passed the source audit and are imported as published.
- 64 records remain in the JSON catalogue as pending and are not published.
- 1 record is excluded because the workbook has no course name.
- 17 universities have resolved official logo/icon URLs; the remaining university records retain their uploaded/image fallback until an official asset can be resolved.

The pending rows are concentrated in official sites that currently redirect to generic catalogue pages, return intermittent errors, expose expired/mismatched certificates, or require a separate manual review. They are intentionally not auto-published.

Run the one-time import from the backend service directory:

```bash
python manage.py migrate
python manage.py seed_content
python manage.py import_verified_courses
```

To load pending rows for admin review without publishing them, use `--include-pending`.
