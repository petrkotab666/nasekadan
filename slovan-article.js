(() => {
  const fragments = [
    '/clanky/parts/slovan-01.html',
    '/clanky/parts/slovan-02.html',
    '/clanky/parts/slovan-03.html',
    '/clanky/parts/slovan-04.html',
    '/clanky/parts/slovan-05.html'
  ];
  const partCounts = {
    'slovan-lavka-hero-20260724': 3,
    'slovan-detail-20260724': 2,
    'lavka-shell-20260724': 2,
    'slovan-vstup-20260724': 2
  };

  async function loadBody() {
    const target = document.getElementById('slovan-article-body');
    if (!target) return;
    const html = [];
    for (const url of fragments) {
      const response = await fetch(`${url}?v=20260724`, {cache: 'no-store'});
      if (!response.ok) throw new Error(`Nelze načíst ${url}`);
      html.push(await response.text());
    }
    target.innerHTML = html.join('');
  }

  async function finalImage(url) {
    try {
      const response = await fetch(`${url}?v=20260724`, {cache: 'no-store'});
      if (!response.ok) return '';
      return URL.createObjectURL(await response.blob());
    } catch {
      return '';
    }
  }

  async function imageFromParts(base) {
    const count = partCounts[base] || 0;
    const chunks = [];
    for (let index = 1; index <= count; index += 1) {
      const suffix = String(index).padStart(2, '0');
      const response = await fetch(`/.image-parts/${base}.part-${suffix}?v=20260724`, {cache: 'no-store'});
      if (!response.ok) throw new Error(`Chybí obrazová část ${base}-${suffix}`);
      chunks.push((await response.text()).replace(/\s+/g, ''));
    }
    return `data:image/jpeg;base64,${chunks.join('')}`;
  }

  async function loadPhotos() {
    const images = document.querySelectorAll('img[data-photo-base]');
    for (const image of images) {
      const finalUrl = image.dataset.photoFinal;
      const base = image.dataset.photoBase;
      image.src = await finalImage(finalUrl) || await imageFromParts(base);
    }
  }

  document.addEventListener('DOMContentLoaded', async () => {
    try {
      await loadBody();
      await loadPhotos();
    } catch (error) {
      const target = document.getElementById('slovan-article-body');
      if (target) target.innerHTML = '<div class="factcheck"><h3>Část článku se nepodařilo načíst</h3><p>Obnovte stránku. Redakce byla o technické chybě informována.</p></div>';
      console.error(error);
    }
  });
})();
