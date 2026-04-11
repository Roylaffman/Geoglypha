/**
 * gallery.js — Ryan Lafferty
 * Graphitia: local-only art gallery, no external API.
 * Add works by editing your-images.json.
 */

const state = {
	activeFilter:  'all',
	items:         [],
	lightboxIndex: -1,
};

const grid      = document.getElementById('gallery-grid');
const emptyEl   = document.getElementById('empty-state');
const lightbox  = document.getElementById('lightbox');
const lbImg     = document.getElementById('lightbox-img');
const lbTitle   = document.getElementById('lb-title');
const lbArtist  = document.getElementById('lb-artist');
const lbDate    = document.getElementById('lb-date');
const lbMedium  = document.getElementById('lb-medium');
const lbDesc    = document.getElementById('lb-description');
const lbLink    = document.getElementById('lb-link');
const lbCounter = document.getElementById('lb-counter');

async function loadImages() {
	try {
		const res = await fetch('your-images.json');
		if (!res.ok) throw new Error('not found');
		state.items = await res.json();
	} catch (_) {
		state.items = [];
	}
	render();
}

function render() {
	grid.innerHTML = '';

	const filtered = state.items.filter(img => {
		if (state.activeFilter === 'all') return true;
		if (state.activeFilter === 'map') return img.type === 'map';
		return (img.type || '').toLowerCase().includes(state.activeFilter);
	});

	document.getElementById('piece-count').textContent =
		filtered.length === 1 ? '1 work' : `${filtered.length} works`;

	if (!filtered.length) {
		emptyEl.classList.remove('hidden');
		return;
	}
	emptyEl.classList.add('hidden');

	filtered.forEach((img, i) => {
		const wrap = document.createElement('div');
		wrap.className = 'gallery-item';
		wrap.dataset.lbIndex = i;

		wrap.innerHTML = `
			<img src="${img.thumb || img.src}" alt="${escHtml(img.title)}" loading="lazy" />
			<div class="item-overlay">
				<p class="item-title">${escHtml(img.title)}</p>
				<p class="item-artist">${escHtml(img.medium || '')}</p>
			</div>
			<span class="item-tag">${img.type === 'map' ? 'map' : 'work'}</span>
		`;

		attachImgLoad(wrap);
		wrap.addEventListener('click', () => openLightbox(i, filtered));
		grid.appendChild(wrap);
	});
}

function openLightbox(index, filtered) {
	const item = filtered[index];
	state.lightboxIndex = index;
	state._filtered = filtered;

	lbImg.src = '';
	lbImg.classList.remove('loaded');
	lbImg.src = item.src;
	lbImg.onload = () => lbImg.classList.add('loaded');

	lbTitle.textContent  = item.title;
	lbArtist.textContent = item.credit || 'Ryan Lafferty';
	lbDate.textContent   = item.year || '';
	lbMedium.textContent = item.medium || '';

	setMeta(lbDesc, item.description || '');

	lbLink.href = item.link || '#';
	lbLink.style.display = item.link ? '' : 'none';

	lbCounter.textContent = `${index + 1} / ${filtered.length}`;
	updateNavButtons(filtered);

	lightbox.classList.remove('hidden');
	document.body.style.overflow = 'hidden';
}

function closeLightbox() {
	lightbox.classList.add('hidden');
	document.body.style.overflow = '';
	lbImg.src = '';
	lbImg.classList.remove('loaded');
}

function lightboxPrev() {
	if (state.lightboxIndex > 0)
		openLightbox(state.lightboxIndex - 1, state._filtered);
}

function lightboxNext() {
	if (state.lightboxIndex < state._filtered.length - 1)
		openLightbox(state.lightboxIndex + 1, state._filtered);
}

function updateNavButtons(filtered) {
	document.getElementById('lb-prev').disabled = state.lightboxIndex <= 0;
	document.getElementById('lb-next').disabled = state.lightboxIndex >= filtered.length - 1;
}

document.getElementById('lightbox-close').addEventListener('click', closeLightbox);
document.getElementById('lb-prev').addEventListener('click', lightboxPrev);
document.getElementById('lb-next').addEventListener('click', lightboxNext);
lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener('keydown', e => {
	if (lightbox.classList.contains('hidden')) return;
	if (e.key === 'Escape')     closeLightbox();
	if (e.key === 'ArrowLeft')  lightboxPrev();
	if (e.key === 'ArrowRight') lightboxNext();
});

document.querySelectorAll('.filter-btn').forEach(btn => {
	btn.addEventListener('click', () => {
		document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
		btn.classList.add('active');
		state.activeFilter = btn.dataset.filter;
		render();
	});
});

function attachImgLoad(wrap) {
	const img = wrap.querySelector('img');
	const onLoad = () => img.classList.add('loaded');
	img.addEventListener('load', onLoad);
	if (img.complete) onLoad();
}

function escHtml(str) {
	return String(str)
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;');
}

function setMeta(el, val) {
	el.textContent   = val || '';
	el.style.display = val ? '' : 'none';
}

loadImages();
