const events=[
 {d:'25',m:'ČVC',t:'Letní koncert na Mírovém náměstí',time:'19:00',place:'Mírové náměstí',cat:'Hudba',desc:'Večerní program pod širým nebem v historickém centru. Doporučujeme dorazit alespoň 20 minut před začátkem.'},
 {d:'26',m:'ČVC',t:'Rodinné odpoledne ve Smetanových sadech',time:'14:00–18:00',place:'Smetanovy sady',cat:'Pro děti',desc:'Soutěže, tvoření a doprovodný program pro rodiny. Část aktivit je vhodná i pro menší děti.'},
 {d:'27',m:'ČVC',t:'Komentovaná prohlídka historické Kadaně',time:'10:00',place:'Turistické informační centrum',cat:'Historie',desc:'Procházka centrem s výkladem o radnici, Katově uličce, hradbách a proměnách královského města.'},
 {d:'30',m:'ČVC',t:'Večerní běh podél Ohře',time:'18:00',place:'Nábřeží Maxipsa Fíka',cat:'Sport',desc:'Neformální běžecké setkání pro veřejnost. Trasa vede převážně po rovině podél řeky.'},
 {d:'02',m:'SRP',t:'Farmářské a řemeslné trhy',time:'08:00–13:00',place:'Mírové náměstí',cat:'Trhy',desc:'Regionální potraviny, drobné řemeslné výrobky a občerstvení přímo v centru města.'},
 {d:'03',m:'SRP',t:'Pohádka pod širým nebem',time:'16:00',place:'Amfiteátr',cat:'Pro děti',desc:'Odpolední představení pro děti a rodiče. Vhodné je vzít si deku nebo podsedák.'}
];

document.querySelector('#events').innerHTML=events.map(e=>`<article class="event"><div class="date"><b>${e.d}</b><span>${e.m}</span></div><div><span class="event-cat">${e.cat}</span><h3>${e.t}</h3><p class="event-meta">${e.place} · ${e.time}</p><p>${e.desc}</p><a href="#tip">Ověřit nebo doplnit akci →</a></div></article>`).join('');
