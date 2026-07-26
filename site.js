// Mobilní styl je načítán přímo z JavaScriptu jako pojistka proti staré HTML šabloně a cache.
document.addEventListener('DOMContentLoaded',()=>{
  if(!document.querySelector('link[data-mobile-css]')){
    const mobile=document.createElement('link');
    mobile.rel='stylesheet';
    mobile.href='/mobile.css?v=20260724-mobile-3';
    mobile.setAttribute('data-mobile-css','true');
    document.head.appendChild(mobile);
  }

  if(document.querySelector('main.article-shell')&&!document.querySelector('script[data-article-adstream]')){
    const adstream=document.createElement('script');
    adstream.src='/reklamy-sidebar.js?v=20260724-adstream-3';
    adstream.async=true;
    adstream.setAttribute('data-article-adstream','true');
    document.head.appendChild(adstream);
  }

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
  const epeticeHref='/clanky/epetice-nemocnice-kadan.html';

  if(path===''||path==='/index.html'){
    const list=document.querySelector('.article-list');
    if(list&&!list.querySelector(`a[href="${epeticeHref}"]`)){
      const card=document.createElement('article');
      card.className='article-card hospital';
      card.setAttribute('data-epetice-card','');
      card.innerHTML=`
        <div class="visual"><strong>ePetice a nemocnice</strong></div>
        <div class="article-body">
          <span class="meta">26. 7. 2026 · 10:15 · Zdravotnictví a veřejná správa</span>
          <h3>Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná</h3>
          <p>Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze sčítat elektronické a listinné podpisy.</p>
          <a class="read-more" href="${epeticeHref}">Přečíst článek →</a>
        </div>`;
      const weekly=list.querySelector('[data-weekly-events-card]');
      if(weekly)weekly.after(card);else list.prepend(card);
    }

    const aside=document.querySelector('.current-aside');
    if(aside&&!aside.querySelector(`a[href="${epeticeHref}"]`)){
      aside.innerHTML=`
        <p class="aside-label">DALŠÍ AKTUÁLNÍ ČLÁNEK</p>
        <p class="aside-date">26. 7. 2026 v 10:15</p>
        <h2>Petice za nemocnici míří online. Obě verze ale musí být stejné</h2>
        <p>Vysvětlujeme limit 3500 znaků, pravidla kombinovaného sběru podpisů a skutečný postup zveřejnění ePetice.</p>
        <a class="aside-button" href="${epeticeHref}">Přečíst článek →</a>
        <div class="aside-links">
          <a href="/clanky/nemocnice-kadan-software-kyberbezpecnost.html">64,7 milionu za software</a>
          <a href="/clanky/nocni-vyluky-vlaku-kadan-klasterec-chomutov-cervenec-srpen-2026.html">Noční výluky vlaků</a>
          <a href="/clanky/">Všechny články podle data</a>
        </div>`;
    }
  }

  if(path==='/clanky'){
    const archive=document.querySelector('.archive-list');
    if(archive&&!archive.querySelector(`a[href="${epeticeHref}"]`)){
      const item=document.createElement('article');
      item.className='archive-item hospital';
      item.setAttribute('data-epetice-card','');
      item.innerHTML=`
        <div class="archive-visual"><strong>ePetice a nemocnice</strong></div>
        <div class="archive-body">
          <span class="archive-meta">26. července 2026 v 10:15 · Zdravotnictví a veřejná správa</span>
          <h2>Petice za nemocnici míří online. Papírová a elektronická verze ale musí být stejná</h2>
          <p>Co znamená limit 3500 znaků, zda se ePetice schvaluje a kdy lze spojit elektronické a listinné podpisy.</p>
          <a href="${epeticeHref}">Přečíst článek →</a>
        </div>`;
      const weekly=archive.querySelector('[data-weekly-events-card]');
      if(weekly)weekly.after(item);else archive.prepend(item);
    }
  }

  if(path===epeticeHref.replace(/\.html$/,'' )||path===epeticeHref){
    const status=document.querySelector('.status-box');
    if(status){
      status.innerHTML='<b>Stav při poslední kontrole:</b> K 26. červenci 2026 ve 13:27 nebyla petice za Nemocnici Kadaň ve veřejně dostupném seznamu oficiálních ePetic dohledatelná. Jakmile se objeví, porovnáme její úplné znění s listinnou verzí a článek aktualizujeme.';
    }
    const structured=document.querySelector('script[type="application/ld+json"]');
    if(structured){
      try{
        const data=JSON.parse(structured.textContent);
        if(data&&data['@type']==='NewsArticle'){
          data.dateModified='2026-07-26T13:27:00+02:00';
          structured.textContent=JSON.stringify(data);
        }
      }catch(error){
        console.warn('Nepodařilo se upravit čas kontroly ePetice.',error);
      }
    }
    return;
  }

  if(path==='/clanky/petice-nemocnice-kadan.html'){
    const article=document.querySelector('.article');
    if(!article)return;

    article.querySelectorAll('p').forEach(paragraph=>{
      const text=(paragraph.textContent||'').trim();
      if(text.startsWith('Petice tedy konflikt nevytvořila.')&&text.includes('Podrobnou finanční analýzu')){
        paragraph.textContent='Petice tedy konflikt nevytvořila. Stala se jeho novou a veřejně viditelnou etapou.';
      }
    });

    document.querySelectorAll('.source-list a[href="/clanky/nemocnice-kadan.html"]').forEach(link=>link.closest('li')?.remove());
    document.querySelectorAll('.sidebox').forEach(box=>{
      if((box.querySelector('h3')?.textContent||'').trim()==='Základní analýza')box.remove();
    });

    if(!document.getElementById('hospital-series-style')){
      const style=document.createElement('style');
      style.id='hospital-series-style';
      style.textContent='.sunday-teaser{margin:30px 0;padding:28px;border-radius:20px;background:linear-gradient(135deg,#14232d,#355d70 62%,#9f2626);color:#fff;box-shadow:0 18px 45px #14232d26}.sunday-teaser .eyebrow{margin:0 0 8px;color:#ffd9d9;font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.sunday-teaser h2{margin:0 0 12px;color:#fff;font-size:32px}.sunday-teaser p{margin:0 0 13px;color:#edf3f5}.sunday-teaser .time{display:inline-block;padding:10px 14px;border:1px solid #ffffff66;border-radius:999px;color:#fff;font-weight:900}.previous-analysis{margin:44px 0 24px;padding:24px;border:1px solid #c7d8df;border-radius:18px;background:#f4f8fa}.previous-analysis strong{display:block;margin-bottom:8px;font:800 23px Georgia,serif;color:#14232d}';
      document.head.appendChild(style);
    }

    if(!document.getElementById('nedelni-clanek')){
      const teaser=document.createElement('section');
      teaser.id='nedelni-clanek';
      teaser.className='sunday-teaser';
      teaser.innerHTML=`
        <p class="eyebrow">NEDĚLE V 5:00 · NAVAZUJÍCÍ ANALÝZA</p>
        <h2>64,7 milionu za software: Nemocnice Kadaň ukázala jen část skládačky</h2>
        <p>Rozebíráme, co se skrývá pod účetní položkou software, proč kybernetická bezpečnost nebyla dobrovolný luxus a proč zákonná povinnost sama nevysvětluje rozsah ani cenu investic.</p>
        <span class="time">Vyjde v neděli 26. 7. v 5:00</span>`;
      const sourceBox=article.querySelector('.source-list');
      if(sourceBox)sourceBox.before(teaser);else article.appendChild(teaser);
    }

    if(!article.querySelector('.previous-analysis')){
      const previous=document.createElement('div');
      previous.className='previous-analysis';
      previous.innerHTML=`
        <strong>První část série o Nemocnici Kadaň</strong>
        <p>Podrobný rozbor hospodaření, provozu a politického rozkolu najdete v první analýze.</p>
        <p><a href="/clanky/nemocnice-kadan.html">Nemocnice Kadaň: ztráta 46 milionů, pomoc města a rozkol ODS →</a></p>`;
      const sourceBox=article.querySelector('.source-list');
      if(sourceBox)sourceBox.before(previous);else article.appendChild(previous);
    }

    const sourceBox=article.querySelector('.source-list');
    const previous=article.querySelector('.previous-analysis');
    const teaser=document.getElementById('nedelni-clanek');
    if(sourceBox){
      if(previous)sourceBox.before(previous);
      if(teaser)sourceBox.before(teaser);
    }
    return;
  }

  if(path!='/clanky/nemocnice-kadan.html')return;

  const tag=document.querySelector('.article .tag');
  if(tag)tag.textContent='ZDRAVOTNICTVÍ · KOMUNÁLNÍ POLITIKA · 24. ČERVENCE 2026';
  const published=document.querySelector('.sidebox .updated');
  if(published)published.textContent='Publikováno: 24. 7. 2026';

  const structured=document.querySelector('script[type="application/ld+json"]');
  if(structured){
    try{
      const data=JSON.parse(structured.textContent);
      if(data&&data['@type']==='NewsArticle'){
        data.datePublished='2026-07-24';
        data.dateModified='2026-07-24';
        structured.textContent=JSON.stringify(data);
      }
    }catch(error){
      console.warn('Nepodařilo se upravit strukturované datum článku.',error);
    }
  }

  const sourceNote=document.querySelector('.source-list small');
  if(sourceNote)sourceNote.textContent=sourceNote.textContent.replace('23. července 2026','24. července 2026');

  const article=document.querySelector('.article');
  if(!article)return;

  const politics=document.getElementById('politika');
  if(politics&&!document.getElementById('hossner-stanovisko')){
    const hossner=document.createElement('section');
    hossner.innerHTML=`
      <h2 id="hossner-stanovisko">Proč byl Petr Hossner odvolán: jeho pohled a stanovisko města</h2>

      <h3>Jak svou roli popisuje bývalý ředitel</h3>
      <p>Petr Hossner na vlastním webu uvádí, že nemocnici vedl od listopadu 2016 do září 2024. Své působení hodnotí jako období rozvoje, otevírání nových ambulancí, růstu objemu péče, ziskového hospodaření a vytváření finančních rezerv. Současně tvrdí, že po změně vedení města odmítal předávat citlivé informace z veřejných soutěží neoprávněným osobám a že po jeho odvolání následovaly spory o pracovní smlouvy, odměňování a požadovanou náhradu škody.</p>
      <p>Na své časové ose uvádí, že byl 24. září 2024 odvolán z funkce jednatele, v březnu 2025 podal žalobu na neplatnost výpovědi a nemocnice po něm následně žalobou požadovala 25,9 milionu korun. Ve svých textech z června a července 2026 varuje před možností hrozícího úpadku, požaduje zveřejnění aktuálního cash-flow a stabilizačního plánu a kritizuje některé kroky současného vedení nemocnice a města.</p>

      <h3>Jak odvolání vysvětlovalo město</h3>
      <p>V tiskové zprávě zveřejněné po změně vedení město uvedlo, že důvodem odvolání byly <strong>zásadní neshody v přístupech k řízení a nedostatečná komunikace při realizaci klíčových kroků</strong>, které podle města vyžadovaly větší koordinaci s vlastníkem nemocnice. Starosta Jan Losenický současně veřejně uznal, že Petr Hossner nemocnici ekonomicky stabilizoval, pozvedl a učinil konkurenceschopnou. Podle starosty ale neshody trvaly delší dobu a město necítilo ochotu ke změně způsobu řízení a komunikace.</p>
      <p>Jako konkrétní příklad město uvádělo, že rada nebyla včas informována o některých strategických organizačních a finančních rozhodnutích. Starosta v říjnu 2024 zmínil také koupi společnosti ARC-MED za 16 milionů korun, o níž se podle jeho vyjádření radní dozvěděli až poté, co byla smlouva podepsána. V dubnu 2025 pak uvedl, že město nebylo spokojeno se systémem řízení a postrádalo některé důležité dokumenty.</p>

      <div class="callout">
        <strong>Důležité časové rozlišení</strong>
        Původním veřejným zdůvodněním odvolání v září 2024 byly neshody o řízení, koordinaci a komunikaci. Spory o souběh funkcí jednatele a ředitele, pracovní smlouvy, odměňování, požadované vrácení peněz a další výsledky následných prověrek se veřejně rozvinuly až později. Článek proto tyto dvě fáze neslučuje a uvádí stanoviska obou stran jako tvrzení účastníků dosud neuzavřeného sporu.
      </div>`;
    politics.before(hossner);
  }

  const scenarios=document.getElementById('scenare');
  if(scenarios&&!document.getElementById('petice')){
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
      <p>Jako předkladatelka je uvedena <strong>Vlasta Štaubrová</strong>. Na zveřejněné kandidátní listině uskupení <strong>Dáme Kadani novou šanci</strong> je uvedena na <strong>12. místě</strong> jako spa terapeutka. Vedle podnikatelské činnosti a působení ve vedení místního SVJ je tedy veřejně doložitelné také její přímé politické propojení s tímto kandidujícím uskupením.</p>
      <p>Tato skutečnost je při hodnocení petice podstatná a čtenář by ji měl znát. Sama kandidatura však ještě nedokazuje, že petice je oficiální akcí uskupení, že ji uskupení zadalo nebo koordinovalo. Takové tvrzení by vyžadovalo další podklad nebo vyjádření zúčastněných.</p>

      <div class="factcheck">
        <h3>Co lze o petici doložit</h3>
        <ul>
          <li><strong>Doložené:</strong> petice je datována 21. 7. 2026 a žádá zachování nemocnice ve vlastnictví města.</li>
          <li><strong>Doložené:</strong> předkladatelkou je Vlasta Štaubrová.</li>
          <li><strong>Doložené:</strong> Vlasta Štaubrová je na kandidátní listině uskupení Dáme Kadani novou šanci uvedena na 12. místě.</li>
          <li><strong>Doložené:</strong> veřejné rejstříky ji spojují s podnikáním a vedením místního SVJ.</li>
          <li><strong>Nedoložené:</strong> že město již rozhodlo o prodeji nebo privatizaci nemocnice.</li>
          <li><strong>Nedoložené:</strong> že petice vznikla jako oficiální nebo koordinovaná akce uskupení Dáme Kadani novou šanci.</li>
        </ul>
      </div>`;
    scenarios.before(petition);
  }

  const toc=document.querySelector('.toc ol');
  if(toc){
    if(!toc.querySelector('a[href="#hossner-stanovisko"]')){
      const item=document.createElement('li');
      item.innerHTML='<a href="#hossner-stanovisko">Odvolání Petra Hossnera: oba pohledy</a>';
      const politicsLink=toc.querySelector('a[href="#politika"]');
      if(politicsLink)politicsLink.closest('li').before(item);else toc.appendChild(item);
    }
    if(!toc.querySelector('a[href="#petice"]')){
      const item=document.createElement('li');
      item.innerHTML='<a href="#petice">Petice za zachování nemocnice</a>';
      const scenariosLink=toc.querySelector('a[href="#scenare"]');
      if(scenariosLink)scenariosLink.closest('li').before(item);else toc.appendChild(item);
    }
  }

  const sources=document.querySelector('.source-list ul');
  if(sources){
    if(!sources.querySelector('[data-hossner-source]')){
      const homepage=document.createElement('li');
      homepage.setAttribute('data-hossner-source','homepage');
      homepage.innerHTML='<a href="https://petrhossnerkadan.cz/" target="_blank" rel="noopener noreferrer">Petr Hossner: osobní web a časová osa jeho působení v Nemocnici Kadaň</a>';
      const warning=document.createElement('li');
      warning.setAttribute('data-hossner-source','warning');
      warning.innerHTML='<a href="https://petrhossnerkadan.cz/aktuality/upozorneni-na-povinnosti-jednatele-nemocnice-kadan-a-vyzva-k-prevenci-dalsich-skod/" target="_blank" rel="noopener noreferrer">Petr Hossner: upozornění na povinnosti jednatele a jeho hodnocení ekonomické situace</a>';
      const cityRelease=document.createElement('li');
      cityRelease.setAttribute('data-hossner-source','city-release');
      cityRelease.innerHTML='<a href="https://petrhossnerkadan.cz/wp-content/uploads/2025/09/1.-TZ_Kadan_odvolani_Hossner.pdf" target="_blank" rel="noopener noreferrer">Tisková zpráva města Kadaně k odvolání Petra Hossnera ze září 2024</a>';
      const cityReason=document.createElement('li');
      cityReason.setAttribute('data-hossner-source','city-reason');
      cityReason.innerHTML='<a href="https://www.idnes.cz/usti/zpravy/kadan-nemocnice-jednatel-odvolani-hossner.A241002_100431_usti-zpravy_grr" target="_blank" rel="noopener noreferrer">iDNES: veřejné vysvětlení důvodů odvolání starostou Janem Losenickým</a>';
      const laterPosition=document.createElement('li');
      laterPosition.setAttribute('data-hossner-source','later-position');
      laterPosition.innerHTML='<a href="https://www.irozhlas.cz/zpravy-domov/reditel-a-zaroven-jednatel-kadan-odvolala-sefa-nemocnice-ten-se-chce-soudit_2504232104_elev" target="_blank" rel="noopener noreferrer">Český rozhlas: pozdější stanovisko města a nemocnice ke způsobu řízení, dokumentům a odměňování</a>';
      sources.append(homepage,warning,cityRelease,cityReason,laterPosition);
    }
    if(!sources.querySelector('[data-petition-source]')){
      const copy=document.createElement('li');
      copy.setAttribute('data-petition-source','copy');
      copy.textContent='Kopie petice „Petice za zachování Nemocnice Kadaň s.r.o. ve vlastnictví města“, datovaná 21. 7. 2026, poskytnutá redakci.';
      const candidates=document.createElement('li');
      candidates.setAttribute('data-petition-source','candidates');
      candidates.innerHTML='<a href="https://damekadaninovousanci.cz/#kandidati" target="_blank" rel="noopener noreferrer">Dáme Kadani novou šanci: zveřejněná kandidátní listina</a>';
      const registry=document.createElement('li');
      registry.setAttribute('data-petition-source','registry');
      registry.innerHTML='<a href="https://www.podnikatel.cz/rejstrik/vlasta-staubrova-72623195/" target="_blank" rel="noopener noreferrer">Veřejný rejstřík: Vlasta Štaubrová a její podnikatelská činnost</a>';
      const svj=document.createElement('li');
      svj.setAttribute('data-petition-source','svj');
      svj.innerHTML='<a href="https://www.podnikatel.cz/rejstrik/spolecenstvi-vlastniku-jednotek-chomutovska-1220-1222-kadan-28678338/" target="_blank" rel="noopener noreferrer">Veřejný rejstřík: vedení SVJ Chomutovská 1220–1222</a>';
      sources.append(copy,candidates,registry,svj);
    }
  }

  if(!document.getElementById('next-hospital-analysis')){
    const style=document.createElement('style');
    style.textContent='.next-article-teaser{margin:48px 0 24px;padding:28px;border-radius:20px;background:linear-gradient(135deg,#14232d,#355d70 62%,#9f2626);color:#fff;box-shadow:0 18px 45px #14232d26}.next-article-teaser .tag{color:#ffd7d7;margin:0 0 8px}.next-article-teaser h2{color:#fff;margin:0 0 12px;font-size:32px}.next-article-teaser p{color:#e7eef1}.next-article-teaser a{display:inline-flex;margin-top:8px;padding:13px 17px;border-radius:10px;background:#fff;color:#8f2027;font-weight:900;text-decoration:none}.next-article-teaser .scheduled{display:inline-block;margin-top:10px;padding:9px 12px;border:1px solid #ffffff66;border-radius:999px;font-weight:900;color:#fff}';
    document.head.appendChild(style);
    const publicAt=Date.parse('2026-07-25T03:00:00Z');
    const isPublic=Date.now()>=publicAt;
    const teaser=document.createElement('section');
    teaser.id='next-hospital-analysis';
    teaser.className='next-article-teaser';
    teaser.innerHTML=`
      <p class="tag">NAVAZUJÍCÍ ČLÁNEK</p>
      <h2>Petice rozjela volební spor. Co víme o 100 milionech, kyberbezpečnosti a údajném plánu nemocnici prodat</h2>
      <p>Prověřili jsme nové výroky o 77 milionech krajských dotací, čekání na refundaci kyberprojektů, bankovním financování i tvrzení o záměru nemocnici prodat.</p>
      ${isPublic?'<a href="/clanky/petice-nemocnice-kadan.html">Přečíst navazující článek →</a>':'<span class="scheduled">Vyjde v sobotu 25. 7. v 5:00</span>'}`;
    const sourceBox=article.querySelector('.source-list');
    if(sourceBox)sourceBox.before(teaser);else article.appendChild(teaser);
  }
});
