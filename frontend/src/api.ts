export type Section={heading:string;body:string;kind?:string;source_url?:string};
export type Entry={id:number;title:string;slug:string;summary:string;image:string;image_url:string;sections:Section[];source_url:string;updated_at:string;reviewed_at:string|null;kind?:string;order:number};
export type Region=Entry&{code:number;cities:string[];scholarship:number|null;living_cost:string};
export type Country={id:number;name:string;slug:string;code:string;published:boolean};
export type University=Entry&{country:number|null;region:number;city:string;logo:string;logo_url:string;institution_type:string;english_taught:boolean;featured:boolean;disciplines:string[];degrees:string[];latitude:number;longitude:number;tuition:string;deadline:string|null;website:string};
export type Scholarship=Entry&{authority:string;deadline:string|null;eligibility:string};
export type Department={id:number;university:number;title:string;address:string;description:string;website:string;order:number};
export type CourseDetailField={id:number;key:string;label:string;presentation:'fact'|'section';value:string;source_url:string;link_label:string};
export type AdmissionCall={id:number;title:string;academic_year:string;applicant_category:string;application_start:string|null;application_deadline:string|null;timezone:string;timezone_abbreviation?:string;studies_commence:string|null;instructions:string;available_places:number|null;source_url:string};
export type Course=Entry&{university:number;department:number|null;degree:string;discipline:string;english_taught:boolean;deadline:string|null;tuition:string;degree_class_code:string;study_location:string;course_type:string;nominal_duration:string;study_language:string;application_fee:string;pre_enrollment_fee:string;tuition_fee:string;cent_requirements:string;language_requirements:string;other_requirements:string;studies_commence:string|null;more_information:string;entry_qualification:string;course_link:string;additional_info:string;details:CourseDetailField[];admission_calls:AdmissionCall[]};
export type Article=Entry&{category:number;category_name:string;author:string;date:string;reading_time:number};
export type Career=Entry&{location:string;employment_type:string;deadline:string|null;salary:string;minimum_experience:string;minimum_commitment_years:number|null;job_description:string;requirements:string;application_instructions:string;status:'open'|'closed'};
export type OfficialUpdate={id:number;title:string;slug:string;summary:string;body:string;kind:'deadline'|'scholarship'|'admission'|'general';source_label:string;source_url:string;published_at:string;expires_at:string|null;published:boolean;pinned:boolean};
export type Testimonial=Entry&{university:number;course:string;city:string;video_url:string};
export type FAQ={id:number;category:string;question:string;answer:string;university:number|null;page:number|null};
export type Settings={title:string;logo:string;address:string;phone:string;support_phone:string;whatsapp:string;email:string;office_hours:string;announcement:string;hero_title:string;hero_description:string;hero_image:string;footer_text:string;social_links:{label:string;url:string}[]};
export type Data={settings:Settings;countries:Country[];regions:Region[];universities:University[];departments:Department[];scholarships:Scholarship[];courses:Course[];pages:Entry[];articles:Article[];careers:Career[];updates:OfficialUpdate[];testimonials:Testimonial[];faqs:FAQ[];categories:{id:number;title:string;slug:string}[];test_dates:{id:number;test:number;label:string;exam_date:string;registration_deadline:string;source_url:string}[]};
const defaultSettings:Settings={title:'Kashyap Advisors',logo:'',address:'',phone:'',support_phone:'',whatsapp:'',email:'',office_hours:'',announcement:'',hero_title:'',hero_description:'',hero_image:'',footer_text:'',social_links:[]};
function normalizeData(data:Partial<Data>):Data{return {...data,settings:{...defaultSettings,...(data.settings||{}),social_links:Array.isArray(data.settings?.social_links)?data.settings.social_links:[]}} as Data}
const configuredApiOrigin=import.meta.env.VITE_API_URL||'';
const API_ORIGIN=(configuredApiOrigin.includes('kashyapadvisors-frontend.onrender.com')?'':configuredApiOrigin||(import.meta.env.PROD?'https://kashyapadvisors-backend.onrender.com':'')).replace(/\/$/,'');
export async function request<T>(path:string,options?:RequestInit):Promise<T>{const res=await fetch(`${API_ORIGIN}/api/${path}`,{...options,headers:options?.body instanceof FormData?options.headers:{'Content-Type':'application/json',...options?.headers}});if(!res.ok){let message='We couldn’t complete your request. Please try again.';try{const body=await res.json();message=Object.entries(body).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(' '):v}`).join(' ')}catch{}throw new Error(message)}const data=await res.json();return (path==='content/'?normalizeData(data):data) as T}
export const imageOf=(e:Entry)=>('logo_url' in e&&typeof e.logo_url==='string'&&e.logo_url)||e.image||e.image_url||(('logo' in e&&typeof e.logo==='string'&&e.logo)||'/assets/logo.png');
export const safeUrl=(s:string)=>/^https?:\/\//i.test(s)?s:'#';

export type StudentProfile={id:number;email:string;first_name:string;last_name:string;phone:string;date_of_birth:string|null;gender:string;nationality:string;passport_number:string;passport_expiry:string|null;citizenship_number:string;address:string;municipality:string;district:string;province:string;emergency_contact_name:string;emergency_contact_phone:string;highest_qualification:string;previous_degree:string;previous_institution:string;field_of_study:string;grading_system:string;overall_percentage:string|null;overall_gpa:string|null;graduation_year:number|null;academic_history:unknown[];english_test:string;english_score:string;english_test_date:string|null;other_language:string;other_language_score:string;target_degree:string;target_disciplines:string[];preferred_cities:string[];profile_status:string;submitted_at:string|null;profile_completion:number};
export type StudentChecklistItem={id:number;key:string;title:string;description:string;required:boolean;accepted_extensions:string;status:string;admin_note:string;visible_to_student:boolean};
export type StudentDocument={id:number;document_type:string;original_name:string;file_size:number;content_type:string;status:string;admin_note:string;uploaded_at:string;checklist_item:number|null};
export type StudentApplication={id:number;reference_code:string;status:string;status_label:string;student_note:string;admin_note:string;submitted_at:string|null;created_at:string;updated_at:string;course:{id:number;title:string;slug:string;degree:string;university:string}|null;stages:{id:number;key:string;title:string;description:string;status:string;status_label:string;order:number}[]};
export type StudentRecommendationRequest={id:number;kind:string;status:string;student_question:string;created_at:string;updated_at:string;recommendations:{id:number;title:string;course_id:number|null;course_title:string;rationale:string;fit_score:number|null}[]};
export type StudentPortalData={profile:StudentProfile;checklist:StudentChecklistItem[];documents:StudentDocument[];applications:StudentApplication[];recommendations:StudentRecommendationRequest[]};

const STUDENT_TOKEN_KEY='kashyap_student_token';
export const getStudentToken=()=>typeof window==='undefined'?'':window.localStorage.getItem(STUDENT_TOKEN_KEY)||'';
export const setStudentToken=(token:string)=>window.localStorage.setItem(STUDENT_TOKEN_KEY,token);
export const clearStudentToken=()=>window.localStorage.removeItem(STUDENT_TOKEN_KEY);
export async function studentRequest<T>(path:string,options?:RequestInit):Promise<T>{
  const token=getStudentToken();
  return request<T>(path,{...options,headers:{...(options?.headers||{}),...(token?{Authorization:`Token ${token}`}:{})}});
}
