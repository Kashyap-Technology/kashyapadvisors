import {Link} from '@tanstack/react-router';
import type {ReactNode} from 'react';
import {ArrowUpRight,Building2,ExternalLink,FileText,Mail,School} from 'lucide-react';
import type {Course,Department,CourseDetailField} from './api';
import {safeUrl} from './api';

type CourseNote={label:string;value:string};
type CourseContact={label:string;email:string};
type CourseNotes={notes:CourseNote[];links:{label:string;url:string}[];contacts:CourseContact[];context:string[]};

const urlPattern=/https?:\/\/[^\s|]+/gi;
const emailPattern=/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi;

function trimToken(value:string){return value.replace(/[.,;:)}\]]+$/,'');}

function LinkedText({text}:{text:string}){
  const tokens=[...text.matchAll(/https?:\/\/[^\s|]+|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi)];
  if(!tokens.length)return <>{text}</>;
  const parts:ReactNode[]=[];
  let cursor=0;
  tokens.forEach((match,index)=>{
    const raw=match[0];
    const token=trimToken(raw);
    const start=match.index||0;
    const trailing=raw.slice(token.length);
    if(start>cursor)parts.push(text.slice(cursor,start));
    const href=token.includes('@')&&!token.startsWith('http')?`mailto:${token}`:safeUrl(token);
    parts.push(<a key={`${token}-${index}`} href={href} target={href.startsWith('http')?'_blank':undefined} rel={href.startsWith('http')?'noreferrer':undefined}>{token}</a>);
    if(trailing)parts.push(trailing);
    cursor=start+raw.length;
  });
  if(cursor<text.length)parts.push(text.slice(cursor));
  return <>{parts}</>;
}

function splitUrls(value:string){return (value.match(urlPattern)||[]).map(trimToken).filter(Boolean);}

function contactLabel(value:string){
  return value.replace(/^\s*Contacts?:\s*/i,'').replace(/^[\s,;:)\-]+|[\s,;()\-]+$/g,'').replace(/\s+/g,' ').trim();
}

function parseContacts(value:string){
  const contacts:CourseContact[]=[];
  const text=value.replace(/^\s*Contacts?:\s*/i,'');
  const matches=[...text.matchAll(emailPattern)];
  matches.forEach((match,index)=>{
    const start=index?((matches[index-1].index||0)+matches[index-1][0].length):0;
    const label=contactLabel(text.slice(start,match.index||0));
    if(label)contacts.push({label,email:match[0]});
  });
  return contacts;
}

export function parseCourseNotes(value:string):CourseNotes{
  const result:CourseNotes={notes:[],links:[],contacts:[],context:[]};
  const chunks=value.split(/\s*\|\s*/).map(chunk=>chunk.trim()).filter(Boolean);
  chunks.forEach(chunk=>{
    const urls=splitUrls(chunk);
    if(/^Contacts?:/i.test(chunk)&&/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(chunk)){
      emailPattern.lastIndex=0;
      result.contacts.push(...parseContacts(chunk));
      const remainder=chunk.replace(/^\s*Contacts?:\s*/i,'').replace(emailPattern,'').replace(/[(),;]/g,' ').replace(/\s+/g,' ').trim();
      if(remainder&&result.contacts.length===0)result.context.push(remainder);
      return;
    }
    if(/^Programme Regulations?:/i.test(chunk)){
      urls.forEach(url=>result.links.push({label:'Programme Regulations',url}));
      if(!urls.length)result.context.push(chunk);
      return;
    }
    if(/^School:/i.test(chunk)||/^Faculty:/i.test(chunk)||/^Department:/i.test(chunk)){
      result.context.push(chunk);
      urls.forEach(url=>result.links.push({label:'School or department website',url}));
      return;
    }
    result.notes.push({label:noteLabel(chunk),value:chunk});
  });
  return result;
}

function noteLabel(value:string){
  if(/delivered entirely in|study language|english/i.test(value))return 'Teaching language';
  if(/tuition fee|scholarship|non-eu/i.test(value))return 'Fees & scholarships';
  if(/application fee/i.test(value))return 'Application fee';
  if(/italian b2|italian language/i.test(value))return 'Italian language';
  return 'Important note';
}

export function courseLead(course:Course){
  const lead=course.summary.split(/\s*\|\s*/)[0].trim();
  return lead||`${course.degree||'Degree'} programme${course.discipline?` in ${course.discipline}`:''}.`;
}

function FieldContent({field}:{field:CourseDetailField}){
  return <><p className="course-prose"><LinkedText text={field.value}/></p>{field.source_url&&<a className="text-link" href={safeUrl(field.source_url)} target="_blank" rel="noreferrer">{field.link_label||'Further information'}<ExternalLink size={15}/></a>}</>;
}

export function formatCourseDate(value:string){
  return new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(value+'T00:00:00Z'));
}

export function formatCourseDeadline(value:string,timeZone:string){
  return new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23',timeZone}).format(new Date(value));
}

function CourseNotes({course}:{course:Course}){
  const parsed=parseCourseNotes(course.additional_info||'');
  const links=[...parsed.links];
  splitUrls(course.more_information||'').forEach(url=>{if(!links.some(link=>link.url===url))links.push({label:'More programme information',url})});
  splitUrls(course.course_link||'').forEach(url=>{if(!links.some(link=>link.url===url))links.push({label:'Programme page',url})});
  const hasContent=parsed.notes.length||links.length||parsed.contacts.length||parsed.context.length;
  if(!hasContent)return null;
  return <section className="course-notes">
    <div className="course-section-heading"><span className="content-kind official">Official programme notes</span><h2>Details worth knowing before you apply.</h2><p>Important conditions, contacts and official documents, organised for quick review.</p></div>
    <div className="course-notes-grid">
      {!!parsed.notes.length&&<article className="course-note-card course-note-card-wide"><div className="course-note-heading"><span className="course-note-icon"><School size={18}/></span><div><span className="course-note-kicker">Read carefully</span><h3>Key programme notes</h3></div></div><ul className="course-note-list">{parsed.notes.map((note,index)=><li key={`${note.label}-${index}`}><strong>{note.label}</strong><p><LinkedText text={note.value}/></p></li>)}</ul></article>}
      {!!parsed.contacts.length&&<article className="course-note-card"><div className="course-note-heading"><span className="course-note-icon"><Mail size={18}/></span><div><span className="course-note-kicker">Need clarification?</span><h3>Programme contacts</h3></div></div><div className="course-contact-list">{parsed.contacts.map((contact,index)=><a className="course-contact" href={`mailto:${contact.email}`} key={`${contact.email}-${index}`}><span>{contact.label}</span><strong>{contact.email}</strong></a>)}</div></article>}
      {!!links.length&&<article className="course-note-card course-link-card"><div className="course-note-heading"><span className="course-note-icon"><FileText size={18}/></span><div><span className="course-note-kicker">Official sources</span><h3>Documents & websites</h3></div></div><div className="course-official-links">{links.map((link,index)=><a className="course-official-link" href={safeUrl(link.url)} target="_blank" rel="noreferrer" key={`${link.url}-${index}`}><span>{link.label}</span><small>{link.url.replace(/^https?:\/\//,'').split('/')[0].replace(/^www\./,'')}</small><ExternalLink size={15}/></a>)}</div></article>}
      {!!parsed.context.length&&<article className="course-note-card"><div className="course-note-heading"><span className="course-note-icon"><Building2 size={18}/></span><div><span className="course-note-kicker">Academic structure</span><h3>School & programme context</h3></div></div>{parsed.context.map((text,index)=><p className="course-prose" key={`${text}-${index}`}><LinkedText text={text}/></p>)}</article>}
    </div>
  </section>;
}

export function CourseInformation({course}:{course:Course}){
  const details=course.details||[];
  const fixedFacts:[string,string][]=[
    ['Degree',course.degree],['Degree class code',course.degree_class_code],['Study location',course.study_location],
    ['Type',course.course_type],['Nominal duration',course.nominal_duration],['Study language',course.study_language],
    ['Application fee',course.application_fee],['Pre-enrollment fee',course.pre_enrollment_fee],['Tuition fee',course.tuition_fee||course.tuition],
  ].filter(([,value])=>Boolean(value)) as [string,string][];
  const fixedSections:[string,string][]=[
    ['CEnT requirements',course.cent_requirements],['Language requirements',course.language_requirements],
    ['Other requirements',course.other_requirements],['Entry qualification',course.entry_qualification],
  ].filter(([,value])=>Boolean(value)) as [string,string][];
  return <>
    <section className="course-overview-panel">
      <div className="course-overview-heading"><div><span className="content-kind official">Programme snapshot</span><h2>Everything important, at a glance.</h2></div><span className="course-degree-pill">{course.course_type||course.degree||'Degree programme'}</span></div>
      <dl className="course-facts">
        {course.discipline&&<div><dt>Discipline</dt><dd>{course.discipline}</dd></div>}
        {fixedFacts.map(([label,value])=><div key={label}><dt>{label}</dt><dd><p className="course-prose">{value}</p></dd></div>)}
        {details.filter(f=>f.presentation==='fact').map(field=><div key={field.id}><dt>{field.label}</dt><dd><FieldContent field={field}/></dd></div>)}
      </dl>
    </section>
    {!!course.admission_calls?.length&&<section className="course-admissions"><h2>Application calls & dates</h2><p>Choose the round that matches your applicant category.</p>{course.admission_calls.map(call=><article className="admission-call" key={call.id}>
      <span className="eyebrow">Academic year {call.academic_year}</span><h3>{call.title}</h3><p className="applicant-category">{call.applicant_category}</p>
      <dl className="admission-dates">
        {call.application_start&&<div><dt>Application start</dt><dd><time dateTime={call.application_start}>{formatCourseDate(call.application_start)}</time></dd></div>}
        {call.application_deadline&&<div><dt>Application deadline</dt><dd><time dateTime={call.application_deadline}>{formatCourseDeadline(call.application_deadline,call.timezone)}</time><small>{call.timezone} · {call.timezone_abbreviation}</small></dd></div>}
        {call.studies_commence&&<div><dt>Studies commence</dt><dd><time dateTime={call.studies_commence}>{formatCourseDate(call.studies_commence)}</time></dd></div>}
        {call.available_places!==null&&<div><dt>Available places</dt><dd>{call.available_places}</dd></div>}
      </dl>
      {call.instructions&&<p className="course-prose">{call.instructions}</p>}
      {call.source_url&&<a className="text-link" href={safeUrl(call.source_url)} target="_blank" rel="noreferrer">Read the official call<ExternalLink size={15}/></a>}
    </article>)}</section>}
    {!course.admission_calls?.length&&course.deadline&&<p>Application deadline: <time dateTime={course.deadline}>{formatCourseDate(course.deadline)}</time></p>}
    {(course.studies_commence||fixedSections.length||details.some(f=>f.presentation==='section'))&&<section className="course-requirements"><div className="course-section-heading"><span className="content-kind">Before you apply</span><h2>Requirements & next steps</h2><p>Review the programme requirements carefully, then confirm the current call on the official university website.</p></div><div className="course-requirements-grid">
      {course.studies_commence&&<article className="course-text-card"><h3>Studies commence</h3><p className="course-prose"><time dateTime={course.studies_commence}>{formatCourseDate(course.studies_commence)}</time></p></article>}
      {fixedSections.map(([heading,body])=><article className="course-text-card" key={heading}><h3>{heading}</h3><p className="course-prose">{body}</p></article>)}
      {details.filter(f=>f.presentation==='section').map(field=><article className="course-text-card" key={field.id}><h3>{field.label}</h3><FieldContent field={field}/></article>)}
    </div></section>}
    <CourseNotes course={course}/>
  </>;
}

export function UniversityDepartments({departments,courses}:{departments:Department[];courses:Course[]}){
  const unassigned=courses.filter(course=>!course.department);
  const courseLink=(course:Course)=><Link className="list-card" to={'/courses/'+course.slug} key={course.id}><span>{course.title}<small>{course.degree} · {course.discipline}</small></span><ArrowUpRight size={18}/></Link>;
  return <>{departments.map(department=><section className="department-card" key={department.id}><div className="department-heading"><Building2 size={23}/><h3>{department.title}</h3></div>{department.address&&<p className="course-prose">{department.address}</p>}{department.description&&<p className="course-prose">{department.description}</p>}{department.website&&<a className="text-link" href={safeUrl(department.website)} target="_blank" rel="noreferrer">Department website<ExternalLink size={15}/></a>}{courses.filter(course=>course.department===department.id).map(courseLink)}</section>)}{unassigned.map(courseLink)}</>;
}
