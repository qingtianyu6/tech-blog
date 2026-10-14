const themeButton = document.querySelector('#theme');
themeButton?.addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme !== 'dark';
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  themeButton.setAttribute('aria-label', dark ? '切换浅色模式' : '切换深色模式');
  try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch {}
});
const search = document.querySelector('#search');
const filters = [...document.querySelectorAll('[data-filter]')];
let category = 'all';
function filterPosts() {
  const query = (search?.value || '').trim().toLocaleLowerCase();
  let visible = 0;
  document.querySelectorAll('.post-card').forEach(card => {
    const show = (category === 'all' || category === card.dataset.category)
      && card.dataset.search.toLocaleLowerCase().includes(query);
    card.hidden = !show;
    if (show) visible++;
  });
  const empty = document.querySelector('#empty');
  if (empty) empty.hidden = visible > 0;
}
search?.addEventListener('input', filterPosts);
filters.forEach(button => button.addEventListener('click', () => {
  category = button.dataset.filter;
  filters.forEach(filter => {
    const selected = filter === button;
    filter.classList.toggle('selected', selected);
    filter.setAttribute('aria-pressed', String(selected));
  });
  filterPosts();
}));
document.querySelectorAll('.prose pre').forEach(pre => {
  const code = pre.querySelector('code');
  if (!code) return;
  const button = document.createElement('button');
  button.className = 'copy-code';
  button.textContent = '复制';
  button.setAttribute('aria-label', '复制代码');
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = '已复制';
    } catch { button.textContent = '请选中复制'; }
    setTimeout(() => button.textContent = '复制', 1800);
  });
  pre.append(button);
});
