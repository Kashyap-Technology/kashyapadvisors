import {describe,it,expect} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import {CourseInformation,formatCourseDate,formatCourseDeadline} from './course-details';
import type {Course} from './api';

describe('course details',()=>{
  it('keeps Rome deadlines and date-only study starts independent of the viewer time zone',()=>{
    expect(formatCourseDeadline('2027-03-07T23:59:59+01:00','Europe/Rome')).toBe('7 Mar 2027, 23:59:59');
    expect(formatCourseDeadline('2027-07-07T21:59:59Z','Europe/Rome')).toBe('7 Jul 2027, 23:59:59');
    expect(formatCourseDate('2027-10-01')).toBe('1 Oct 2027');
  });

  it('renders custom content, precise rounds and links while escaping entered text',()=>{
    const course={degree:'Bachelor’s degree',discipline:'Animal science',tuition:'',deadline:null,details:[
      {id:1,key:'nominal-duration',label:'Nominal duration',presentation:'fact',value:'3 years (180 ECTS)',source_url:'',link_label:''},
      {id:2,key:'entry',label:'Entry qualification',presentation:'section',value:'Secondary diploma\n<script>alert(1)</script>',source_url:'https://example.com/call',link_label:'Call for admission'}
    ],admission_calls:[{id:1,title:'Non-EU call',academic_year:'2027/2028',applicant_category:'NON-EU applicants residing outside Italy',application_start:'2027-01-07',application_deadline:'2027-03-07T23:59:59+01:00',timezone:'Europe/Rome',timezone_abbreviation:'CET',studies_commence:'2027-10-01',instructions:'Applicants residing in Italy use the EU and equated call.',available_places:8,source_url:'https://example.com/call'}]} as Course;
    const html=renderToStaticMarkup(<CourseInformation course={course}/>);
    for(const text of ['3 years (180 ECTS)','Entry qualification','7 Mar 2027, 23:59:59','Europe/Rome · CET','1 Oct 2027','NON-EU applicants','EU and equated call','Call for admission'])expect(html).toContain(text);
    expect(html).toContain('&lt;script&gt;');
    expect(html).not.toContain('<script>');
  });
});
