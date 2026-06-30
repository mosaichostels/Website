<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-H3K992L4ZT');</script>

<!-- Mosaic SEO Suite -->
<meta name="description" content="Photos of Mosaic Hostel Varanasi — dorm rooms, private rooms, rooftop, and the Assi Ghat neighbourhood.">
<link rel="canonical" href="https://www.mosaichostels.com/gallery/">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
<meta property="og:site_name" content="Mosaic Hostel Varanasi">
<meta property="og:title"       content="Photo Gallery — Mosaic Hostel Varanasi">
<meta property="og:description" content="Photos of Mosaic Hostel Varanasi — dorm rooms, private rooms, rooftop, and the Assi Ghat neighbourhood.">
<meta property="og:url"         content="https://www.mosaichostels.com/gallery/">
<meta property="og:type"        content="website">
<meta property="og:image"       content="https://www.mosaichostels.com/wp-content/uploads/2026/06/mosaic-hostel-og-image.png">
<meta property="og:locale"      content="en_IN">
<meta name="twitter:card"  content="summary_large_image">
<meta name="twitter:title" content="Photo Gallery — Mosaic Hostel Varanasi">
<meta name="twitter:image" content="https://www.mosaichostels.com/wp-content/uploads/2026/06/mosaic-hostel-og-image.png">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"ImageGallery","name":"Mosaic Hostel Varanasi Photo Gallery","url":"https://www.mosaichostels.com/gallery/"}</script>
<script>
const LOGO_COLORS=['#C8860A','#8B1A1A','#1A6B7A','#1A3A6B','#5C3A1E','#E8B84B','#3D6B3A','#A02020','#2D9AAA','#7A4F2A'];
const PALS={
  'gold-teal': ['#C8860A','#E8B84B','#D4930F','#1A6B7A','#2D9AAA'],
  'teal-cobalt':['#1A6B7A','#2D9AAA','#0D4A55','#1A3A6B','#2A5A9B'],
  'burg-gold': ['#8B1A1A','#A02020','#6B1010','#C8860A','#E8B84B'],
  'cobalt-sage':['#1A3A6B','#2A5A9B','#3D6B3A','#2D5A2A'],
  'sage-gold':  ['#3D6B3A','#2D5A2A','#C8860A','#E8B84B'],
};
function pick(a){return a[Math.floor(Math.random()*a.length)];}
function fillStrip(el,cols){if(!el)return;cols.forEach(c=>{const s=document.createElement('span');s.style.flex='1';s.style.background=c;el.appendChild(s);});}
function fillById(id,cols){fillStrip(document.getElementById(id),cols);}

// tile dividers
fillById('heroStripe',LOGO_COLORS);
fillById('div0',LOGO_COLORS);
fillById('div1',LOGO_COLORS);
fillById('footerStrip',['#C8860A','#8B1A1A','#1A6B7A','#1A3A6B','#3D6B3A']);

// gallery item accent bars
document.querySelectorAll('.gal-accent').forEach(el=>{
  const pal=PALS[el.dataset.pal]||PALS['gold-teal'];
  for(let i=0;i<20;i++){const s=document.createElement('span');s.style.flex='1';s.style.background=pick(pal);el.appendChild(s);}
});

// Custom cursor
const cur=document.getElementById('cursor'),ring=document.getElementById('cursor-ring');
document.addEventListener('mousemove',e=>{
  cur.style.left=e.clientX+'px';cur.style.top=e.clientY+'px';
  ring.style.left=e.clientX+'px';ring.style.top=e.clientY+'px';
});
document.querySelectorAll('a,button,.gal-item').forEach(el=>{
  el.addEventListener('mouseenter',()=>{cur.style.width='18px';cur.style.height='18px';ring.style.width='48px';ring.style.height='48px';});
  el.addEventListener('mouseleave',()=>{cur.style.width='10px';cur.style.height='10px';ring.style.width='36px';ring.style.height='36px';});
});

// Scroll progress
const prog=document.getElementById('progress');
window.addEventListener('scroll',()=>{
  prog.style.width=((window.scrollY/(document.body.scrollHeight-window.innerHeight))*100)+'%';
},{passive:true});

// ── FILTER ──
const items=Array.from(document.querySelectorAll('.gal-item'));
const countEl=document.getElementById('photoCount');
const noRes=document.getElementById('noResults');

function applyFilter(cat){
  let visible=0;
  items.forEach(item=>{
    const match=cat==='all'||item.dataset.cat===cat;
    item.classList.toggle('hidden',!match);
    if(match) visible++;
  });
  countEl.textContent=visible+' Photo'+(visible!==1?'s':'');
  noRes.style.display=visible===0?'block':'none';
}

document.querySelectorAll('.filter-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    applyFilter(btn.dataset.filter);
  });
});

// init count
countEl.textContent=items.length+' Photos';

// ── LIGHTBOX ──
const lb=document.getElementById('lightbox');
const lbImg=document.getElementById('lb-img');
const lbTitle=document.getElementById('lb-title');
const lbCat=document.getElementById('lb-cat');
const lbStrip=document.getElementById('lb-strip');
const lbCounter=document.getElementById('lb-counter');
let currentIdx=0;

function getVisible(){return items.filter(i=>!i.classList.contains('hidden'));}

function openLightbox(idx){
  const visible=getVisible();
  if(!visible[idx]) return;
  currentIdx=idx;
  const item=visible[idx];
  lbImg.src=item.dataset.full||item.querySelector('.gal-photo').src;
  lbImg.alt=item.dataset.title;
  lbTitle.textContent=item.dataset.title;
  lbCat.textContent=item.querySelector('.gal-cat-tag').textContent;
  // fill strip
  lbStrip.innerHTML='';
  fillStrip(lbStrip,LOGO_COLORS.slice(0,6));
  lbCounter.textContent=(idx+1)+' / '+visible.length;
  lb.classList.add('open');
  document.body.style.overflow='hidden';
}

function closeLightbox(){
  lb.classList.remove('open');
  document.body.style.overflow='';
  lbImg.src='';
}

function navigate(dir){
  const visible=getVisible();
  currentIdx=(currentIdx+dir+visible.length)%visible.length;
  openLightbox(currentIdx);
}

items.forEach((item,i)=>{
  item.addEventListener('click',()=>{
    const visible=getVisible();
    const visIdx=visible.indexOf(item);
    openLightbox(visIdx);
  });
});

document.getElementById('lb-close').addEventListener('click',closeLightbox);
document.getElementById('lb-prev').addEventListener('click',()=>navigate(-1));
document.getElementById('lb-next').addEventListener('click',()=>navigate(1));
lb.addEventListener('click',e=>{if(e.target===lb)closeLightbox();});
document.addEventListener('keydown',e=>{
  if(!lb.classList.contains('open')) return;
  if(e.key==='ArrowLeft') navigate(-1);
  if(e.key==='ArrowRight') navigate(1);
  if(e.key==='Escape') closeLightbox();
});

// Scroll reveal
const obs=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add('visible');});},{threshold:0.05});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));

// Magnetic nav-book
const navBook=document.querySelector('.nav-book');
if(navBook){
  navBook.addEventListener('mousemove',e=>{
    const r=navBook.getBoundingClientRect();
    const x=(e.clientX-r.left-r.width/2)*0.2;
    const y=(e.clientY-r.top-r.height/2)*0.2;
    navBook.style.transform=`translate(${x}px,${y}px)`;
  });
  navBook.addEventListener('mouseleave',()=>{navBook.style.transform='';});
}



(function(){
  var ham=document.getElementById('navHam');
  var nl=document.querySelector('.nav-links');
  if(!ham||!nl)return;
  ham.addEventListener('click',function(){
    nl.classList.toggle('open');ham.classList.toggle('open');
    document.body.style.overflow=nl.classList.contains('open')?'hidden':'';
  });
  nl.querySelectorAll('a').forEach(function(a){
    a.addEventListener('click',function(){
      nl.classList.remove('open');ham.classList.remove('open');
      document.body.style.overflow='';
    });
  });
})();
</script>
