import React from 'react';
import {gsap} from 'gsap';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
import {useGSAP} from '@gsap/react';

gsap.registerPlugin(ScrollTrigger, useGSAP);

export function MotionShell({children,path}:{children:React.ReactNode;path:string}){
  const scope=React.useRef<HTMLDivElement>(null);
  const activePath=path;
  useGSAP(()=>{
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    const root=scope.current;
    if(!root)return;
    const reveal=gsap.utils.toArray<HTMLElement>('.section, .map-section, .journey-preview, .blog-section, .cta, .page-hero, .detail-layout, .contact-layout',root);
    reveal.forEach(section=>{
      gsap.fromTo(section,{y:22},{y:0,duration:.65,ease:'power3.out',
        scrollTrigger:{trigger:section,start:'top 94%',once:true}});
    });
    gsap.fromTo('.hero-copy > *',{opacity:0,y:20},{opacity:1,y:0,duration:.7,stagger:.1,ease:'power3.out',clearProps:'opacity,transform'});
    gsap.fromTo('.hero-photo',{scale:1.03},{scale:1,duration:1.1,ease:'power2.out'});
    gsap.fromTo('.hero-stamp, .floating-note',{opacity:0,y:12},{opacity:1,y:0,delay:.5,duration:.6,stagger:.12,clearProps:'opacity,transform'});
  },{scope,dependencies:[activePath],revertOnUpdate:true});
  React.useEffect(()=>{
    const label=activePath==='/'?'Study in Italy from Nepal':activePath.split('/').filter(Boolean).slice(-1)[0]?.replace(/-/g,' ')||'Kashyap Advisors';
    document.title=`${label.replace(/\b\w/g,x=>x.toUpperCase())} | Kashyap Advisors`;
    const description=activePath.includes('vfs')?'VFS Nepal and VFS Kolkata guidance for Italy student visa documents, appointment preparation and submission planning.':activePath.includes('geneva')?'Geneva attestation and document verification guidance for Nepalese students applying to study in Italy.':activePath.includes('caf')||activePath.includes('isee')?'CAF and ISEE scholarship documentation guidance for students from Nepal applying for Italian regional benefits.':activePath.includes('region')?'Explore all 20 regions of Italy, student cities, universities, scholarships and living options with Kashyap Advisors.':activePath.includes('cimea')||activePath.includes('dov')?'CIMEA and DOV guidance for students from Nepal applying to Italian universities, including qualification recognition and document planning.':activePath.includes('legaliz')||activePath.includes('translat')?'Prepare document legalization and certified translation for Italian university applications and student visa documents from Nepal.':activePath.includes('imat')||activePath.includes('entrance')?'Prepare for IMAT, TOLC, CEnT-S and Italian university entrance tests with a clear study and registration plan.':activePath.includes('universit')?'Explore Italian universities, courses and English-taught study options with Kashyap Advisors.':activePath.includes('scholar')?'Understand Italian scholarships and right-to-study benefits with practical guidance from Nepal.':'Study in Italy from Nepal with personal guidance for universities, scholarships, applications, visas, CIMEA, DOV, VFS, legalization, translation and arrival.';
    const setMeta=(name:string,content:string,property=false)=>{const selector=property?`meta[property="${name}"]`:`meta[name="${name}"]`;let el=document.head.querySelector<HTMLMetaElement>(selector);if(!el){el=document.createElement('meta');property?el.setAttribute('property',name):el.setAttribute('name',name);document.head.appendChild(el)}el.content=content};
    setMeta('description',description);setMeta('keywords','study in Italy from Nepal, Italian universities, CIMEA, DOV, Declaration of Value, IMAT, document legalization, certified translation, student visa Italy');setMeta('og:title',document.title,true);setMeta('og:description',description,true);setMeta('twitter:title',document.title);setMeta('twitter:description',description);
    let canonical=document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');if(!canonical){canonical=document.createElement('link');canonical.rel='canonical';document.head.appendChild(canonical)}canonical.href=`https://kashyapadvisors.com${activePath}`;
  },[activePath]);
  return <div ref={scope} className="site-shell">{children}</div>;
}
