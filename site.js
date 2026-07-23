// Nasazení petice: 23. 7. 2026 22:15
// Verze 3 – doplnění článku a správné označení data vydání.
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('.head').forEach(head=>{
    const nav=head.querySelector('nav');
    if(!nav||head.querySelector('.menu-toggle'))return;
    const button=document.createElement('button');
    button.className='menu-toggle';
    button.type='button';
    button.setAttribute('aria-label','Otevřít hlavní menu');
    button.setAttribute('aria-expanded','false');
    button.innerHTML='<span></span><span></span><span></span>';
    button.addEventListener('click',()=>{
      const open=nav.classList.toggle('is-open');
      button.classList.toggle('is-open',open);
      button.setAttribute('aria-expanded',String(open));
      button.setAttribute('aria-label',open?'Zavřít hlavní menu':'Otevřít hlavní menu');
    });
    head.appendChild(button);
  });

  const path=window.location.pathname.replace(/\/+$/,'');
  if(path!='/clanky/nemocnice-kadan.html')return;

  const tag=document.querySelector('.article .tag');
  if(tag)tag.textContent='ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 23. ČERVENCE 2026';
  const published=document.querySelector('.sidebox .updated');
  if(published)published.textContent='Publikováno: 23. 7. 2026';

  const article=document.querySelector('.article');
  const scenarios=document.getElementById('scenare');
  if(!article||!scenarios||document.getElementById('petice'))return;

  const petition=document.createElement('section');
  petition.innerHTML=`
    <h2 id="petice">Nová petice žádá zachování nemocnice ve vlastnictví města</h2>
    <p>Do veřejné debaty vstoupila petice datovaná 21. července 2026 a adresovaná Zastupitelstvu města Kadaně. Její autoři požadují, aby město veřejně garantovalo, že Nemocnice Kadaň nebude prodána ani jinak převedena do soukromého vlastnictví. Současně žádají okamžitá stabilizační opatření, zachování potřebných zdravotnických oborů a ambulancí, pravidelné zveřejňování hospodářských výsledků, nezávislé odborné posouzení řízení nemocnice, případné personální změny a otevřenější komunikaci s veřejností i zaměstnanci.</p>
    <p>Petice také klade vedení města otázky po konkrétním ozdravném plánu, dalším zadlužování, dosavadních krocích ke zlepšení hospodaření a po tom, zda může město občanům zaručit zachování nemocnice v městském vlastnictví.</p>

    <div class="callout">
      <strong>Důležité rozlišení</strong>
      Petice vyjadřuje obavu z možného prodeje nebo předání nemocnice soukromému provozovateli. V dostupných podkladech jsme ale nenašli schválené rozhodnutí města, že se nemocnice prodá nebo privatizuje. Obava uvedená v petici proto není totéž jako doložený plán prodeje.
    </div>

    <h3>Kdo petici předkládá</h3>
    <p>Jako předkladatelka je uvedena <strong>Vlasta Štaubrová</strong>. Ve veřejných rejstřících je dohledatelná jako kadaňská podnikatelka a předsedkyně výboru Společenství vlastníků jednotek Chomutovská 1220–1222. V prověřených veřejných zdrojích jsme ji nenašli mezi kandidáty ani funkcionáři ODS, uskupení Dáme Kadani novou šanci nebo jiného politického subjektu.</p>
    <p>To nevylučuje osobní názory, kontakty nebo neformální podporu některé skupiny, ale bez veřejně doložitelného podkladu by nebylo korektní tvrdit, že je petice řízena konkrétní stranou. Samotné načasování petice v době vyhroceného sporu o nemocnici a před komunálními volbami politické propojení nedokazuje.</p>

    <div class="factcheck">
      <h3>Co lze o petici doložit</h3>
      <ul>
        <li><strong>Doložené:</strong> petice je datována 21. 7. 2026 a žádá zachování nemocnice ve vlastnictví města.</li>
        <li><strong>Doložené:</strong> předkladatelkou je Vlasta Štaubrová.</li>
        <li><strong>Doložené:</strong> veřejné rejstříky ji spojují s podnikáním a vedením místního SVJ.</li>
        <li><strong>Nedoložené:</strong> že město již rozhodlo o prodeji nebo privatizaci nemocnice.</li>
        <li><strong>Nedoložené:</strong> že předkladatelka jedná jménem ODS, uskupení Dáme Kadani novou šanci nebo jiné politické strany.</li>
      </ul>
    </div>`;
  scenarios.before(petition);

  const toc=document.querySelector('.toc ol');
  if(toc&&!toc.querySelector('a[href="#petice"]')){
    const item=document.createElement('li');
    item.innerHTML='<a href="#petice">Petice za zachování nemocnice</a>';
    const scenariosLink=toc.querySelector('a[href="#scenare"]');
    if(scenariosLink)scenariosLink.closest('li').before(item);else toc.appendChild(item);
  }

  const sources=document.querySelector('.source-list ul');
  if(sources&&!sources.querySelector('[data-petition-source]')){
    const copy=document.createElement('li');
    copy.setAttribute('data-petition-source','copy');
    copy.textContent='Kopie petice „Petice za zachování Nemocnice Kadaň s.r.o. ve vlastnictví města“, datovaná 21. 7. 2026, poskytnutá redakci.';
    const registry=document.createElement('li');
    registry.setAttribute('data-petition-source','registry');
    registry.innerHTML='<a href="https://www.podnikatel.cz/rejstrik/vlasta-staubrova-72623195/" target="_blank" rel="noopener noreferrer">Veřejný rejstřík: Vlasta Štaubrová a její podnikatelská činnost</a>';
    const svj=document.createElement('li');
    svj.setAttribute('data-petition-source','svj');
    svj.innerHTML='<a href="https://www.podnikatel.cz/rejstrik/spolecenstvi-vlastniku-jednotek-chomutovska-1220-1222-kadan-28678338/" target="_blank" rel="noopener noreferrer">Veřejný rejstřík: vedení SVJ Chomutovská 1220–1222</a>';
    sources.append(copy,registry,svj);
  }
});