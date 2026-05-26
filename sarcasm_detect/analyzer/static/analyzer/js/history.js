// history.js — client-side filter, search, and delete

document.addEventListener('DOMContentLoaded', () => {
  const rows = Array.from(document.querySelectorAll('.history-row'));
  const searchInput = document.getElementById('searchInput');
  const filterBtns = document.querySelectorAll('#filterBtns button');

  let activeFilter = 'all';

  function applyFilters() {
    const query = searchInput ? searchInput.value.toLowerCase() : '';
    rows.forEach(row => {
      const verdict = row.dataset.verdict;
      const text = row.textContent.toLowerCase();
      const matchFilter = activeFilter === 'all' || verdict === activeFilter;
      const matchSearch = !query || text.includes(query);
      row.style.display = matchFilter && matchSearch ? '' : 'none';
    });
  }

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', applyFilters);
  }
});

// Global delete function called by inline onclick
async function deleteAnalysis(id, btn) {
  if (!confirm('Delete this analysis? This cannot be undone.')) return;

  btn.disabled = true;
  btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';

  try {
    const resp = await fetch('/api/delete/' + id + '/', { method: 'POST' });
    if (resp.ok) {
      const row = document.getElementById('row-' + id);
      if (row) {
        row.style.transition = 'opacity 0.3s';
        row.style.opacity = '0';
        setTimeout(function() { row.remove(); }, 300);
      }
    } else {
      const data = await resp.text();
      console.error('Delete failed:', resp.status, data);
      alert('Failed to delete. Status: ' + resp.status);
      btn.disabled = false;
      btn.innerHTML = '<i class="fa fa-trash"></i>';
    }
  } catch (err) {
    console.error('Delete error:', err);
    alert('Network error: ' + err.message);
    btn.disabled = false;
    btn.innerHTML = '<i class="fa fa-trash"></i>';
  }
}
