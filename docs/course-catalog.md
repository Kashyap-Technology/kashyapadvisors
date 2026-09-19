# Managing universities, departments and courses

1. In `/admin/`, create or edit a **University**, then add and save its **Departments**.
2. Open **Courses**, add or edit a course, and choose its university and department.
3. In **Fields for this course**, enter a label and value directly. For example, `Nominal duration` → `3 years (180 ECTS)`, or `Entry qualification` → the complete requirements text.
4. Choose **Overview row** for facts and fees, or **Detailed section** for longer requirements. Set the order, visibility, and optional official URL and link label. Use **Add another Course field** for more fields. No separate field definition is needed.
5. Add **Admission calls** for each academic year and applicant category, with application start, precise deadline, time zone, study start, instructions, available places and official URL.
6. Save and publish the university, department, course and relevant calls. Refresh the website to see the changes.

## Course-specific fields

Every field belongs to exactly one course. Its label, value, presentation, order, visibility and source links are independent of other courses. Renaming or hiding `Tuition fee` on one course leaves other courses unchanged. The **Course fields** admin list shows each field's course and can be filtered by course. You can also create a field there by selecting its course.

Suggested labels: Study location, Study mode, Nominal duration, Study language, Awards, Course code, Tuition fee, Application fee, Deposit, Entry qualification, Language requirements, Other requirements, Required documents and More information. Enter fee amounts and explanations together, using paragraphs and line breaks as needed. Fields with the same label can exist on different courses; labels must be unique within one course.

Existing values and links have been preserved. Their formerly shared labels, presentation, order and visibility were copied onto their individual course records. The old global definitions are retained internally for migration history but are no longer editable through admin or used to render course pages.

Degree and discipline remain basic course fields. Detailed tuition replaces the optional basic tuition in the public overview. Published admission calls replace the basic deadline display. Existing legacy sections remain visible.

## Admission deadlines

For the supplied example, enter application start `2027-01-07`, deadline `2027-03-07 23:59:59`, time zone `Europe/Rome`, and studies commence `2027-10-01`. The website displays the deadline in CET; summer dates use CEST automatically. Applicant instructions remain specific to each call.

Existing courses without departments are preserved. Assign a department when editing them; all new courses require one.
