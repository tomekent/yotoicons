// Track data structure: {id: number, name: string, iconId: string|null}
let tracks = [{id: Date.now(), name: '', iconId: null}];
const trackListDiv = document.getElementById('trackList');
const addTrackBtn = document.getElementById('addTrackBtn');
const downloadTracksBtn = document.getElementById('downloadTracksBtn');
const iconSearchModal = document.getElementById('iconSearchModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const modalTitle = document.getElementById('modalTitle');
const modalResultsCount = document.getElementById('modalResultsCount');
const modalIconGrid = document.getElementById('modalIconGrid');
const modalLoading = document.getElementById('modalLoading');
const modalSearchInput = document.getElementById('modalSearchInput');
let currentTrackIdx = null;
let lastSearchTerm = '';

let modalOffset = 0;
let modalTotal = null;
let modalQuery = '';
let modalLoadingIcons = false;

function renderTrackList() {
    trackListDiv.innerHTML = '';
    tracks.forEach((track) => {
        const wrapper = document.createElement('div');
        wrapper.style.display = 'flex';
        wrapper.style.alignItems = 'center';
        wrapper.style.marginBottom = '16px';
        wrapper.style.gap = '18px';

        // Icon placeholder
        const iconDiv = document.createElement('div');
        iconDiv.style.width = '64px';
        iconDiv.style.height = '64px';
        iconDiv.style.border = '2px solid #cbd5e1';
        iconDiv.style.borderRadius = '12px';
        iconDiv.style.background = '#fff';
        iconDiv.style.display = 'flex';
        iconDiv.style.alignItems = 'center';
        iconDiv.style.justifyContent = 'center';
        iconDiv.style.cursor = 'pointer';
        iconDiv.title = 'Click to assign icon';

        if (track.iconId) {
            iconDiv.innerHTML = `<img src="/yoto_icons/${track.iconId}.png" alt="icon" style="width:56px;height:56px;border-radius:8px;">`;
        } else {
            // Use a plus icon instead of camera
            iconDiv.innerHTML = `<span style="color:#a0aec0;font-size:2.2rem;">&#43;</span>`;
        }
        iconDiv.onclick = () => openIconSearch(track.id);

        // Track name input
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.value = track.name;
        nameInput.placeholder = "Track name...";
        nameInput.style.width = '220px';
        nameInput.style.padding = '8px 12px';
        nameInput.style.borderRadius = '8px';
        nameInput.style.border = '1px solid var(--input-border)';
        nameInput.oninput = (e) => {
            track.name = e.target.value;
        };

        // Remove track button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'removeTrackBtn';
        removeBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <line x1="6" y1="6" x2="18" y2="18" stroke="#718096" stroke-width="2" stroke-linecap="round"/>
                <line x1="18" y1="6" x2="6" y2="18" stroke="#718096" stroke-width="2" stroke-linecap="round"/>
            </svg>
        `;
        removeBtn.setAttribute('data-id', track.id);
        removeBtn.onclick = () => {
            const idxToRemove = tracks.findIndex(t => t.id === track.id);
            if (idxToRemove !== -1) {
                tracks.splice(idxToRemove, 1);
                renderTrackList();
            }
        };

        wrapper.appendChild(iconDiv);
        wrapper.appendChild(nameInput);
        wrapper.appendChild(removeBtn);
        trackListDiv.appendChild(wrapper);
    });
}

addTrackBtn.onclick = () => {
    tracks.push({id: Date.now() + Math.random(), name: '', iconId: null});
    renderTrackList();
};

function openIconSearch(trackId) {
    currentTrackIdx = tracks.findIndex(t => t.id === trackId);
    iconSearchModal.style.display = 'flex';
    modalTitle.textContent = `Searching Icon for "${tracks[currentTrackIdx].name || 'Track'}"`;
    modalSearchInput.value = tracks[currentTrackIdx].name;
    lastSearchTerm = tracks[currentTrackIdx].name;
    searchIcons(tracks[currentTrackIdx].name);
    modalSearchInput.focus();
}

closeModalBtn.onclick = () => {
    iconSearchModal.style.display = 'none';
    modalIconGrid.innerHTML = '';
    modalResultsCount.textContent = '';
    modalSearchInput.value = '';
};

modalSearchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        searchIcons(modalSearchInput.value);
    }
});

modalSearchInput.addEventListener('input', function(e) {
    if (modalSearchInput.value !== lastSearchTerm) {
        lastSearchTerm = modalSearchInput.value;
        searchIcons(modalSearchInput.value);
    }
});

async function searchIcons(query, append = false) {
    if (!append) {
        modalOffset = 0;
        modalTotal = null;
        // Show placeholder instead of clearing
        modalIconGrid.innerHTML = `<div style="width:100%;text-align:center;padding:40px 0;color:#a0aec0;">Loading...</div>`;
    }
    modalLoading.style.display = 'block';
    modalLoadingIcons = true;
    try {
        const resp = await fetch(`/api/search?query=${encodeURIComponent(query)}&offset=${modalOffset}&limit=25`);
        const data = await resp.json();
        modalTotal = data.total;
        modalResultsCount.textContent = `Results (${modalTotal})`;
        if (!append) modalIconGrid.innerHTML = '';
        data.results.forEach(row => {
            const card = document.createElement('div');
            card.className = 'icon-card';
            card.style.cursor = 'pointer';
            card.innerHTML = `<img src="/yoto_icons/${row.id}.png" alt="icon">`;
            card.onclick = () => {
                tracks[currentTrackIdx].iconId = row.id;
                renderTrackList();
                iconSearchModal.style.display = 'none';
                modalIconGrid.innerHTML = '';
                modalResultsCount.textContent = '';
                modalSearchInput.value = '';
            };
            card.title = `${row.category} | ${row.tag_1} | ${row.tag_2}`;
            card.onmouseenter = () => card.classList.add('selected');
            card.onmouseleave = () => card.classList.remove('selected');
            modalIconGrid.appendChild(card);
        });
        modalOffset += data.results.length;
    } finally {
        modalLoading.style.display = 'none';
        modalLoadingIcons = false;
    }
}

modalIconGrid.addEventListener('scroll', function() {
    if (
        modalIconGrid.scrollTop + modalIconGrid.clientHeight >= modalIconGrid.scrollHeight - 40 &&
        !modalLoadingIcons &&
        modalOffset < modalTotal
    ) {
        searchIcons(modalQuery, true);
    }
});

downloadTracksBtn.onclick = async function() {
    const assigned = tracks.filter(t => t.iconId && t.name.trim());
    const payload = assigned.map(t => ({id: t.iconId, name: t.name.trim()}));
    const resp = await fetch('/download', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({tracks: payload})
    });
    if (resp.ok) {
        const blob = await resp.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'track_icons.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } else {
        alert('Download failed');
    }
};

// On page load, check for preTracks in localStorage
const preTracks = localStorage.getItem('preTracks');
if (preTracks) {
    const parsed = JSON.parse(preTracks);
    tracks = parsed.map((t, idx) => ({
        id: Date.now() + idx,
        name: t.name,
        iconId: t.iconId
    }));
    localStorage.removeItem('preTracks');
}


renderTrackList();