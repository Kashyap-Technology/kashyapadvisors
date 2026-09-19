import {Link} from '@tanstack/react-router';
import {ArrowUpRight,Building2,ExternalLink} from 'lucide-react';
import type {Course,Department,CourseDetailField} from './api';
import {safeUrl} from './api';

function FieldContent({field}:{field:CourseDetailField}){
  return <><p className="course-prose">{field.value}</p>{field.source_url&&<a className="text-link" href={safeUrl(field.source_url)} target="_blank" rel="noreferrer">{field.link_label||'Further information'}<ExternalLink size={15}/></a>}</>;
}

export function formatCourseDate(value:string){
  return new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(value+'T00:00:00Z'));
}

export function formatCourseDeadline(value:string,timeZone:string){
  return new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23',timeZone}).format(new Date(value));
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
    ['Other requirements',course.other_requirements],['Entry qualification',course.entry_qualification],['Additional information',course.additional_info],
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
    {(course.studies_commence||fixedSections.length||course.more_information||course.course_link||details.some(f=>f.presentation==='section'))&&<section className="course-requirements"><div className="course-section-heading"><span className="content-kind">Before you apply</span><h2>Requirements & next steps</h2><p>Review the programme requirements carefully, then confirm the current call on the official university website.</p></div><div className="course-requirements-grid">
      {course.studies_commence&&<article className="course-text-card"><h3>Studies commence</h3><p className="course-prose"><time dateTime={course.studies_commence}>{formatCourseDate(course.studies_commence)}</time></p></article>}
      {fixedSections.map(([heading,body])=><article className="course-text-card" key={heading}><h3>{heading}</h3><p className="course-prose">{body}</p></article>)}
      {course.more_information&&<article className="course-text-card course-link-card"><h3>More information</h3><a className="text-link" href={safeUrl(course.more_information)} target="_blank" rel="noreferrer">Visit the official course page<ExternalLink size={15}/></a></article>}
      {course.course_link&&<article className="course-text-card course-link-card"><h3>Course link</h3><a className="text-link" href={safeUrl(course.course_link)} target="_blank" rel="noreferrer">Open application course link<ExternalLink size={15}/></a></article>}
      {details.filter(f=>f.presentation==='section').map(field=><article className="course-text-card" key={field.id}><h3>{field.label}</h3><FieldContent field={field}/></article>)}
    </div></section>}
  </>;
}

export function UniversityDepartments({departments,courses}:{departments:Department[];courses:Course[]}){
  const unassigned=courses.filter(course=>!course.department);
  const courseLink=(course:Course)=><Link className="list-card" to={'/courses/'+course.slug} key={course.id}><span>{course.title}<small>{course.degree} · {course.discipline}</small></span><ArrowUpRight size={18}/></Link>;
  return <>{departments.map(department=><section className="department-card" key={department.id}><div className="department-heading"><Building2 size={23}/><h3>{department.title}</h3></div>{department.address&&<p className="course-prose">{department.address}</p>}{department.description&&<p className="course-prose">{department.description}</p>}{department.website&&<a className="text-link" href={safeUrl(department.website)} target="_blank" rel="noreferrer">Department website<ExternalLink size={15}/></a>}{courses.filter(course=>course.department===department.id).map(courseLink)}</section>)}{unassigned.map(courseLink)}</>;
}
