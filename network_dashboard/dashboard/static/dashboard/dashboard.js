(function () {
  const sections = document.querySelectorAll('.panel');
  const navButtons = document.querySelectorAll('.nav-item');
  const alertFilter = document.getElementById('alertFilter');
  const markAllRead = document.getElementById('markAllRead');
  const globalSearch = document.getElementById('globalSearch');
  const manualSearch = document.getElementById('manualSearch');
  const viewer = document.getElementById('viewerContent');
  const resetTasks = document.getElementById('resetTasks');
  const taskProgress = document.getElementById('taskProgress');
  const progressLabel = document.getElementById('progressLabel');
  const checkboxes = document.querySelectorAll("input[type='checkbox'][data-task-key]");
  const docsButton = document.getElementById('openDocs');

  function switchSection(target) {
    sections.forEach((section) => {
      section.classList.toggle('hidden', section.id !== target);
    });
    navButtons.forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.section === target);
    });
  }

  navButtons.forEach((button) => {
    button.addEventListener('click', () => switchSection(button.dataset.section));
  });

  function filterAlerts() {
    const selected = alertFilter.value;
    document.querySelectorAll('.alert-card').forEach((card) => {
      const match = selected === 'all' || card.dataset.severity === selected;
      card.style.display = match ? 'grid' : 'none';
    });
  }

  alertFilter?.addEventListener('change', filterAlerts);
  filterAlerts();

  function markCardRead(card) {
    card.classList.add('read');
    card.style.opacity = 0.55;
  }

  document.querySelectorAll('.mark-read').forEach((btn) => {
    btn.addEventListener('click', (event) => {
      const card = event.target.closest('.alert-card');
      if (card) markCardRead(card);
    });
  });

  markAllRead?.addEventListener('click', () => {
    document.querySelectorAll('.alert-card').forEach(markCardRead);
  });

  manualSearch?.addEventListener('input', (event) => {
    const term = event.target.value.toLowerCase();
    document.querySelectorAll('.manual-category').forEach((category) => {
      const categoryName = category.dataset.category.toLowerCase();
      const items = category.querySelectorAll('li');
      let visible = categoryName.includes(term);

      items.forEach((item) => {
        const title = item.dataset.title.toLowerCase();
        const show = title.includes(term) || categoryName.includes(term);
        item.style.display = show ? 'flex' : 'none';
        if (show) visible = true;
      });

      category.style.display = visible ? 'flex' : 'none';
    });
  });

  function renderViewer(title, format) {
    const isPdf = format === 'pdf';
    viewer.innerHTML = `
      <div class="viewer-meta">
        <p class="meta-title">${title}</p>
        <span class="meta-format">${format.toUpperCase()}</span>
      </div>
      <div class="viewer-body ${isPdf ? 'pdf' : 'md'}">
        ${isPdf ? '<p>Simulação de PDF embutido.</p>' : '<pre># Preview Markdown\n\n- Sumário de execução\n- Comandos e diagramas</pre>'}
      </div>
    `;
  }

  document.querySelectorAll('.view-btn').forEach((btn) => {
    btn.addEventListener('click', (event) => {
      const item = event.target.closest('li');
      renderViewer(item.dataset.title, item.dataset.format);
    });
  });

  function saveTasks() {
    const state = Array.from(checkboxes).map((cb) => ({ key: cb.dataset.taskKey, checked: cb.checked }));
    localStorage.setItem('dashboardTasks', JSON.stringify(state));
  }

  function loadTasks() {
    const raw = localStorage.getItem('dashboardTasks');
    if (!raw) return;
    try {
      const state = JSON.parse(raw);
      state.forEach(({ key, checked }) => {
        const cb = document.querySelector(`input[data-task-key="${key}"]`);
        if (cb) cb.checked = checked;
      });
    } catch (e) {
      console.warn('Não foi possível carregar as tarefas salvas.', e);
    }
  }

  function updateProgress() {
    const total = checkboxes.length;
    const done = Array.from(checkboxes).filter((cb) => cb.checked).length;
    const percent = Math.round((done / total) * 100);
    taskProgress.style.width = `${percent}%`;
    progressLabel.textContent = `${percent}% das rotinas concluídas`;
  }

  checkboxes.forEach((cb) => {
    cb.addEventListener('change', () => {
      saveTasks();
      updateProgress();
    });
  });

  resetTasks?.addEventListener('click', () => {
    checkboxes.forEach((cb) => (cb.checked = false));
    saveTasks();
    updateProgress();
  });

  loadTasks();
  updateProgress();

  function focusSearch() {
    globalSearch?.focus();
  }

  document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      focusSearch();
    }
    if (!event.ctrlKey && event.key.toLowerCase() === 'g') {
      focusSearch();
    }
    if (!event.ctrlKey && event.key.toLowerCase() === 'm') {
      switchSection('manuals');
    }
    if (event.ctrlKey && /[1-9]/.test(event.key)) {
      const index = parseInt(event.key, 10) - 1;
      if (checkboxes[index]) {
        checkboxes[index].checked = !checkboxes[index].checked;
        checkboxes[index].dispatchEvent(new Event('change'));
      }
    }
  });

  if (docsButton) {
    docsButton.addEventListener('click', () => {
      alert('Modo documentação (GitBook-like) pode ser integrado aqui.');
    });
  }
})();
