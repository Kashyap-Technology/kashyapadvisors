document.addEventListener('DOMContentLoaded', () => {
  const university = document.getElementById('id_university');
  const department = document.getElementById('id_department');
  if (!university || !department) return;
  let controller;
  university.addEventListener('change', async () => {
    controller?.abort();
    controller = new AbortController();
    department.replaceChildren(new Option('Choose a department', ''));
    if (!university.value) return;
    department.disabled = true;
    try {
      const base = window.location.pathname.split('/course/')[0] + '/course/';
      const response = await fetch(`${base}departments/${university.value}/`, {signal:controller.signal});
      if (!response.ok) throw new Error('Could not load departments');
      const data = await response.json();
      data.departments.forEach(item => department.add(new Option(item.title, item.id)));
    } catch (error) {
      if (error.name === 'AbortError') return;
      department.replaceChildren(new Option('Could not load departments. Save and retry.', ''));
    } finally {
      department.disabled = false;
    }
  });
});
