/**
 * gallery.js — Ryan Lafferty
 * ─────────────────────────────────────────────────────────
 * Infinite-scroll art gallery pulling from:
 *   1. Art Institute of Chicago (AIC) public API — no key needed
 *   2. your-images.json — local manifest for your artwork + maps
 *
 * To add your own work: edit your-images.json
 * To change AIC search: edit AIC_QUERY below
 * ─────────────────────────────────────────────────────────
 */

// ── Config ────────────────────────────────────────────────
const AIC_BASE   = 'https://api.artic.edu/api/v1';
const IIIF_BASE  = 'https://www.artic.edu/iiif/2';
const AIC_FIELDS = [
	'id',
	'title',
	'image_id',
	'artist_display',
	'date_display',
	'medium_display',
	'artwork_type_title',
	'dimensions',
	'place_of_origin',
	'description',
	'thumbnail',
].join(',');
const PAGE_SIZE  = 50;     // items per API page (max 100)
const IIIF_THUMB = '400,'; // grid thumbnail width
const IIIF_FULL  = '843,'; // lightbox / cached full size

// Change this to narrow the AIC feed. Empty = all public domain works.
// Examples: 'landscape', 'portrait', 'abstract', 'chicago', 'impressionism'
const AIC_QUERY  = '';

// ── State ─────────────────────────────────────────────────
const state = {
	aicPage:       1,
	loading:       false,
	exhausted:     false,
	activeFilter:  'all',
	localImages:   [],
	localLoaded:   false,
	lightboxItems: [],  // [{src, title, artist, date, medium, origin, dimensions, description, link}]
	lightboxIndex: -1,
};

// ── DOM refs ──────────────────────────────────────────────
const grid      = document.getElementById('gallery-grid');
const sentinel  = document.getElementById('sentinel');
const loadingEl = document.getElementById('loading-indicator');
const lightbox  = document.getElementById('lightbox');
const lbImg     = document.getElementById('lightbox-img');
const lbTitle   = document.getElementById('lb-title');
const lbArtist  = document.getElementById('lb-artist');
const lbDate    = document.getElementById('lb-date');
const lbMedium  = document.getElementById('lb-medium');
const lbOrigin  = document.getElementById('lb-origin');
const lbDims    = document.getElementById('lb-dimensions');
const lbDesc    = document.getElementById('lb-description');
const lbLink    = document.getElementById('lb-link');
const lbCounter = document.getElementById('lb-counter');

// ── Local images manifest ─────────────────────────────────
async function loadLocalImages() {
	try {
		const res = await fetch('your-images.json');
		if (!res.ok) return;
		state.localImages = await res.json();
		state.localLoaded = true;
		renderLocalImages(state.activeFilter);
	} catch (_) {
		console.info('No your-images.json — AIC images only.');
	}
}

function renderLocalImages(filter) {
	document.querySelectorAll('.gallery-item[data-source="local"]').forEach(el => el.remove());

	const filtered = state.localImages.filter(img => {
		if (filter === 'all') return true;
		if (filter === 'map') return img.type === 'map';
		return (img.type || '').toLowerCase().includes(filter);
	});

	filtered.forEach(img => {
		const index = state.lightboxItems.length;
		state.lightboxItems.push({
			src:         img.src,
			title:       img.title,
			artist:      img.credit || '',
			date:        img.year || '',
			medium:      img.medium || '',
			origin:      '',
			dimensions:  '',
			description: '',
			link:        img.link || '',
		});

		const wrap = document.createElement('div');
		wrap.className = 'gallery-item';
		wrap.dataset.source = 'local';
		wrap.dataset.type   = img.type || 'artwork';
		wrap.dataset.lbIndex = index;

		wrap.innerHTML = `
			<img src="${img.thumb || img.src}" alt="${escHtml(img.title)}" loading="lazy" />
			<div class="item-overlay">
				<p class="item-title">${escHtml(img.title)}</p>
				<p class="item-artist">${escHtml(img.credit || '')}</p>
			</div>
			<span class="item-tag">${img.type === 'map' ? 'map' : 'work'}</span>
		`;

		attachImgLoad(wrap);
		wrap.addEventListener('click', () => openLightbox(index));
		grid.prepend(wrap);
	});
}

// ── Fetch AIC artworks ────────────────────────────────────
async function fetchAIC() {
	if (state.loading || state.exhausted) return;
	state.loading = true;
	loadingEl.classList.add('visible');

	try {
		// Always use /search so query[term][is_public_domain] is honored by Elasticsearch.
		let url = `${AIC_BASE}/artworks/search`
			+ `?query[term][is_public_domain]=true`
			+ `&fields=${encodeURIComponent(AIC_FIELDS)}`
			+ `&limit=${PAGE_SIZE}`
			+ `&page=${state.aicPage}`;
		if (AIC_QUERY) url += `&q=${encodeURIComponent(AIC_QUERY)}`;

		const res  = await fetch(url, {
			headers: { 'AIC-User-Agent': 'personal-gallery (ryan@example.com)' },
		});
		const json = await res.json();
		const artworks = (json.data || []).filter(a => a.image_id);

		if (!artworks.length) { state.exhausted = true; return; }

		renderAICItems(artworks);
		state.aicPage++;

		// PAGE_SIZE=50, API cap=10,000 records → max page 200.  Stop at 100 (5,000 items).
		if (state.aicPage > 100) state.exhausted = true;

	} catch (err) {
		console.error('AIC fetch error:', err);
	} finally {
		state.loading = false;
		loadingEl.classList.remove('visible');
	}
}

function renderAICItems(artworks) {
	const filter = state.activeFilter;

	artworks.forEach(art => {
		const type = normalizeType(art.artwork_type_title || '');

		if (filter === 'map') return;
		if (filter !== 'all' && !type.includes(filter)) return;

		const thumbUrl = `${IIIF_BASE}/${art.image_id}/full/${IIIF_THUMB}/0/default.jpg`;
		const fullUrl  = `${IIIF_BASE}/${art.image_id}/full/${IIIF_FULL}/0/default.jpg`;
		const lqip     = art.thumbnail && art.thumbnail.lqip ? art.thumbnail.lqip : null;

		const index = state.lightboxItems.length;
		state.lightboxItems.push({
			src:         fullUrl,
			title:       art.title || 'Untitled',
			artist:      art.artist_display || '',
			date:        art.date_display || '',
			medium:      art.medium_display || '',
			origin:      art.place_of_origin || '',
			dimensions:  art.dimensions || '',
			description: stripHtml(art.description || ''),
			link:        `https://www.artic.edu/artworks/${art.id}`,
		});

		const wrap = document.createElement('div');
		wrap.className = 'gallery-item';
		wrap.dataset.source  = 'aic';
		wrap.dataset.type    = type;
		wrap.dataset.lbIndex = index;

		// LQIP blur-up: set as CSS background so it shows before the real img loads
		if (lqip) wrap.style.backgroundImage = `url("${lqip}")`;

		wrap.innerHTML = `
			<img src="${thumbUrl}" alt="${escHtml(art.title || 'Untitled')}" loading="lazy" />
			<div class="item-overlay">
				<p class="item-title">${escHtml(art.title || 'Untitled')}</p>
				<p class="item-artist">${escHtml(truncate(art.artist_display, 60))}</p>
			</div>
		`;

		attachImgLoad(wrap);
		wrap.addEventListener('click', () => openLightbox(index));
		grid.appendChild(wrap);
	});
}

// ── Lightbox ──────────────────────────────────────────────
function openLightbox(index) {
	if (index < 0 || index >= state.lightboxItems.length) return;
	state.lightboxIndex = index;
	const item = state.lightboxItems[index];

	lbImg.src = '';
	lbImg.classList.remove('loaded');
	lbImg.src = item.src;
	lbImg.onload = () => lbImg.classList.add('loaded');

	lbTitle.textContent  = item.title;
	lbArtist.textContent = item.artist;
	lbDate.textContent   = item.date;
	lbMedium.textContent = item.medium;

	setMeta(lbOrigin,     item.origin);
	setMeta(lbDims,       item.dimensions);
	setMeta(lbDesc,       item.description);

	lbLink.href = item.link;
	lbLink.style.display = item.link ? '' : 'none';

	updateNavButtons();
	lbCounter.textContent = `${index + 1} / ${state.lightboxItems.length}`;

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
	if (state.lightboxIndex > 0) openLightbox(state.lightboxIndex - 1);
}

function lightboxNext() {
	if (state.lightboxIndex < state.lightboxItems.length - 1) openLightbox(state.lightboxIndex + 1);
}

function updateNavButtons() {
	document.getElementById('lb-prev').disabled = state.lightboxIndex <= 0;
	document.getElementById('lb-next').disabled = state.lightboxIndex >= state.lightboxItems.length - 1;
}

document.getElementById('lightbox-close').addEventListener('click', closeLightbox);
document.getElementById('lb-prev').addEventListener('click', lightboxPrev);
document.getElementById('lb-next').addEventListener('click', lightboxNext);
lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener('keydown', e => {
	if (lightbox.classList.contains('hidden')) return;
	if (e.key === 'Escape')      closeLightbox();
	if (e.key === 'ArrowLeft')   lightboxPrev();
	if (e.key === 'ArrowRight')  lightboxNext();
});

// ── Filters ───────────────────────────────────────────────
document.querySelectorAll('.filter-btn').forEach(btn => {
	btn.addEventListener('click', () => {
		document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
		btn.classList.add('active');
		state.activeFilter = btn.dataset.filter;

		document.querySelectorAll('.gallery-item[data-source="aic"]').forEach(el => el.remove());
		// Reset only the AIC portion of lightboxItems; keep local items at front
		const localCount = state.localImages.filter(img => {
			const f = state.activeFilter;
			if (f === 'all') return true;
			if (f === 'map') return img.type === 'map';
			return (img.type || '').toLowerCase().includes(f);
		}).length;
		state.lightboxItems.splice(localCount);

		state.aicPage   = 1;
		state.exhausted = false;

		if (state.localLoaded) renderLocalImages(state.activeFilter);
		fetchAIC();
	});
});

// ── Infinite scroll ───────────────────────────────────────
const observer = new IntersectionObserver(entries => {
	if (entries[0].isIntersecting) fetchAIC();
}, { rootMargin: '600px' });

observer.observe(sentinel);

// ── Helpers ───────────────────────────────────────────────
function attachImgLoad(wrap) {
	const img = wrap.querySelector('img');
	const onLoad = () => {
		img.classList.add('loaded');
		wrap.style.backgroundImage = ''; // clear lqip once real img is painted
	};
	img.addEventListener('load', onLoad);
	if (img.complete) onLoad();
}

function normalizeType(raw) {
	const r = raw.toLowerCase();
	if (r.includes('paint'))                                    return 'painting';
	if (r.includes('photo'))                                    return 'photograph';
	if (r.includes('draw'))                                     return 'drawing';
	if (r.includes('print') || r.includes('engrav') || r.includes('etch')) return 'print';
	return r;
}

function truncate(str, n) {
	if (!str) return '';
	return str.length > n ? str.slice(0, n) + '\u2026' : str;
}

function escHtml(str) {
	return String(str)
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;');
}

function stripHtml(str) {
	return str.replace(/<[^>]+>/g, '').trim();
}

function setMeta(el, val) {
	el.textContent  = val || '';
	el.style.display = val ? '' : 'none';
}

// ── Viewer count ──────────────────────────────────────────
function updateViewerCount() {
	document.getElementById('viewer-count').textContent = '1 viewing';
}

// ── Init ──────────────────────────────────────────────────
(async function init() {
	updateViewerCount();
	await loadLocalImages();
	fetchAIC();
}());
