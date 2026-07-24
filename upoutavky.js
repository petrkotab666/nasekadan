document.addEventListener('DOMContentLoaded',()=>{
  const path=window.location.pathname.replace(/\/+$/,'')||'/';
  const publishAt=Date.parse('2026-07-26T03:00:00Z');
  const isPublished=Date.now()>=publishAt;
  const articleUrl='/clanky/nemocnice-kadan-software-kyberbezpecnost.html';
  const title='64,7 milionu za software: Nemocnice Kadaň ukázala jen část skládačky';

  if(path==='/clanky/petice-nemocnice-kadan.html'&&!document.getElementById('next-cyber-analysis')){
    const article=document.querySelector('.article');
    if(article){
      const style=document.createElement('style');
      style.textContent='.next-article-teaser{margin:48px 0 24px;padding:28px;border-radius:20px;background:linear-gradient(135deg,#14232d,#355d70 62%,#9f2626);color:#fff;box-shadow:0 18px 45px #14232d26}.next-article-teaser .tag{color:#ffd7d7;margin:0 0 8px}.next-article-teaser h2{color:#fff;margin:0 0 12px;font-size:32px}.next-article-teaser p{color:#e7eef1}.next-article-teaser a{display:inline-flex;margin-top:8px;padding:13px 17px;border-radius:10px;background:#fff;color:#8f2027;font-weight:900;text-decoration:none}.next-article-teaser .scheduled{display:inline-block;margin-top:10px;padding:9px 12px;border:1px solid #ffffff66;border-radius:999px;font-weight:900;color:#fff}';
      document.head.appendChild(style);
      const teaser=document.createElement('section');
      teaser.id='next-cyber-analysis';
      teaser.className='next-article-teaser';
      teaser.innerHTML=`<p class="tag">V NEDĚLI NA NAŠE KADAŇ</p><h2>${title}</h2><p>Rozebrali jsme, co se skrývá za účetními 64,7 milionu, proč nemocnice kybernetickou bezpečnost řešit musí a proč povinnost zabezpečení stále nevysvětluje konečný účet.</p>${isPublished?`<a href="${articleUrl}">Přečíst celý článek →</a>`:'<span class="scheduled">Vyjde v neděli 26. 7. v 5:00</span>'}`;
      const sources=article.querySelector('.source-list');
      if(sources)sources.before(teaser);else article.appendChild(teaser);
    }
  }

  if(path==='/'&&isPublished&&!document.getElementById('home-cyber-analysis')){
    const target=document.querySelector('main .cards, main .article-grid, main section');
    if(target){
      const card=document.createElement('article');
      card.id='home-cyber-analysis';
      card.className='card';
      card.innerHTML=`<p class="tag">ZDRAVOTNICTVÍ · ANALÝZA</p><h2><a href="${articleUrl}">${title}</a></h2><p>Co nemocnice skutečně pořizovala, proč kybernetická ochrana není dobrovolný luxus a které části konečného účtu veřejné dokumenty stále nevysvětlují.</p><a class="btn" href="${articleUrl}">Přečíst analýzu</a>`;
      target.prepend(card);
    }
  }
});
