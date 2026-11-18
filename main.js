(function(){
  var header=document.querySelector('.site-header');
  var onScroll=function(){header&&header.classList.toggle('scrolled',window.scrollY>8)};
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  var btn=document.querySelector('.menu-btn'),nav=document.querySelector('.mobile-nav');
  if(btn&&nav){
    btn.addEventListener('click',function(){var o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o)});
  }
  var yr=document.getElementById('yr');if(yr)yr.textContent=new Date().getFullYear();

  // Conversion tracking hooks for Google Analytics 4 / Google Ads.
  // Pushes to dataLayer only; nothing is sent until a GA4/Ads tag is added in <head>.
  window.dataLayer=window.dataLayer||[];
  function track(name,params){window.dataLayer.push(Object.assign({event:name,page_path:location.pathname},params||{}))}
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a');if(!a)return;
    if(a.href.indexOf('calendly.com')>-1)track('calendly_click',{cta:a.getAttribute('data-cta')||a.textContent.trim()});
    else if(a.href.indexOf('mailto:')===0)track('email_click',{cta:a.getAttribute('data-cta')||'email'});
    else if(a.href.indexOf('tel:')===0)track('phone_click');
  });
  // Calendly inline widget events (booked meeting = primary conversion)
  window.addEventListener('message',function(e){
    if(e.origin!=='https://calendly.com'||!e.data||!e.data.event)return;
    if(e.data.event==='calendly.event_scheduled')track('calendly_booked');
    if(e.data.event==='calendly.date_and_time_selected')track('calendly_time_selected');
  });

  // Forms: POST to /api/contact (emails Ryan's inbox). If the endpoint isn't reachable
  // (e.g. a static preview), fall back to a prefilled email to info@javelinre.com.
  document.querySelectorAll('form[data-mail]').forEach(function(f){
    var started=Date.now();
    var hp=document.createElement('input');hp.type='text';hp.name='company_website';hp.tabIndex=-1;hp.autocomplete='off';
    hp.setAttribute('aria-hidden','true');hp.style.cssText='position:absolute;left:-9999px;width:1px;height:1px;opacity:0';
    f.appendChild(hp);
    f.addEventListener('submit',function(e){
      e.preventDefault();if(!f.reportValidity())return;
      var d=new FormData(f),payload={form:f.getAttribute('data-mail'),page:location.pathname,started:started};
      d.forEach(function(v,k){if(v)payload[k]=v});
      var note=f.querySelector('.form-note'),btn=f.querySelector('button[type=submit]'),label=btn&&btn.textContent;
      if(btn){btn.disabled=true;btn.textContent='Sending...'}
      function done(msg,ok){if(note)note.textContent=msg;if(btn){btn.disabled=false;btn.textContent=label}if(ok)f.reset()}
      function mailto(){
        var lines=[];Object.keys(payload).forEach(function(k){if(['started','company_website','page'].indexOf(k)<0)lines.push(k.charAt(0).toUpperCase()+k.slice(1)+': '+payload[k])});
        done('Opening your email app. If nothing opens, write to info@javelinre.com.');
        location.href='mailto:info@javelinre.com?subject='+encodeURIComponent(payload.form)+'&body='+encodeURIComponent(lines.join('\n'));
      }
      fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
        .then(function(r){return r.json().catch(function(){return{ok:false,unreachable:true}}).then(function(j){j.status=r.status;return j})})
        .then(function(j){
          if(j.ok){track('form_submit',{form:payload.form});done('Thank you. Your message was sent and we\'ll reply within one business day.',true)}
          else if(j.unreachable||j.status===404||j.status===405)mailto();
          else done(j.error||'Something went wrong. Please email info@javelinre.com.');
        })
        .catch(mailto);
    });
  });
  // expertise flip tiles
  document.querySelectorAll('.flip').forEach(function (t) {
    t.addEventListener('click', function () {
      var on = t.classList.toggle('on');
      t.setAttribute('aria-pressed', on ? 'true' : 'false');
      t.querySelector('.front').setAttribute('aria-hidden', on ? 'true' : 'false');
      t.querySelector('.back').setAttribute('aria-hidden', on ? 'false' : 'true');
      if (window.dataLayer && on) window.dataLayer.push({ event: 'expertise_flip', tile: t.querySelector('strong').textContent });
    });
  });
})();
