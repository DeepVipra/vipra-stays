window.__rEd=()=>[...document.querySelectorAll('[contenteditable=true]')].filter(e=>e.offsetParent);
window.__rNext=()=>{const b=[...document.querySelectorAll('[role=button],button')].filter(e=>e.offsetParent&&e.innerText.trim()==='Next');if(b.length)b[b.length-1].click();return b.length;};
window.__rPrep=async d=>{const p=__vsCal[d];const b=await __vsGet(p.files[0]);window.__vsQueue=[new File([b],p.files[0],{type:'video/mp4'})];const btn=__vsText('Add Video').pop();(btn.closest('[role=button]')||btn).click();
 for(let i=0;i<40;i++){await __S(1500);if(/100%/.test(document.body.innerText))break;}
 __vsSwitch('Customize post for Facebook and Instagram',true);await __S(1000);__vsTab('Facebook');await __S(600);__vsPasteInto(__rEd()[0],p.fb);await __S(700);__vsTab('Instagram');await __S(600);__vsPasteInto(__rEd()[0],p.ig);await __S(700);document.activeElement.blur();
 __vsTab('Facebook');await __S(500);const fb=__rEd()[0].innerText.slice(0,25);__vsTab('Instagram');await __S(500);const ig=__rEd()[0].innerText.slice(-25);
 __rNext();await __S(3000);__rNext();await __S(3000);
 const s=[...document.querySelectorAll('div,span')].filter(e=>e.offsetParent&&e.innerText&&e.innerText.trim()==='Schedule');(s[0].closest('[role=button],[role=radio],label')||s[0]).click();await __S(1500);
 await __vsSetDates(p.mdy);return {fb,ig,st:__vsState()};};
window.__rFinal=async d=>{const p=__vsCal[d];await __vsSetDates(p.mdy);const st=__vsState();const want=[p.h,p.m,p.ampm].join();const ok=st.spins.length===6&&st.spins.slice(0,3).join()===want&&st.spins.slice(3).join()===want&&st.dates.length===2;if(!ok)return {ok,st};
 const b=[...document.querySelectorAll('[role=button],button')].filter(e=>e.offsetParent&&e.innerText.trim()==='Schedule');b[b.length-1].click();let done=false;for(let i=0;i<20&&!done;i++){await __S(1500);done=/Reel scheduled/i.test(document.body.innerText);}const msg=(document.body.innerText.match(/Your reel is scheduled[^\n]*/)||[''])[0];const dn=__vsText('Done');if(dn.length)(dn[0].closest('[role=button]')||dn[0]).click();return {ok,done,msg,st};};
