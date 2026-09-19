"""Reviewed test guidance. Existing slugs are retained for bookmarked pages."""
from datetime import date

REVIEWED = date(2026, 9, 7)
IELTS = 'https://ielts.org/take-a-test/test-types/ielts-academic-test'
PADUA = 'https://www.unipd.it/en/requisito-linguistico-ammissione-corsi-studio-ateneo'
CISIA = 'https://www.cisiaonline.it/en/cent/cent-s/structure-and-syllabus'
SAPIENZA = 'https://i3s.web.uniroma1.it/it/prove-di-accesso'
BOLOGNA = 'https://corsi.unibo.it/1cycle/EconomicsFinance/how-to-enrol'
MEDICINE = 'https://www.unibo.it/en/study/enrolment-fees-and-other-procedures/degree-programmes/admission-tests'
SAT = 'https://satsuite.collegeboard.org/sat/whats-on-the-test/structure'


def section(heading, body, source=''):
    return dict(heading=heading, body=body, kind='guidance', source_url=source)


TEST_PAGES = [
    dict(slug='english-proficiency-tests', title='IELTS Academic & English language requirements',
         summary='Understand IELTS, what each section tests, and when an English-medium qualification can replace a language certificate for bachelor’s or master’s admission.',
         source_url=IELTS, sections=[
             section('What is IELTS Academic?',
                     'IELTS Academic is an English proficiency test for university study. It assesses listening, reading, writing and speaking; it does not test your suitability for medicine or engineering. It can be used for undergraduate and postgraduate applications. Choose a test version and delivery format accepted by every programme on your shortlist.', IELTS),
             section('The four sections, explained',
                     'Listening: approximately 30 minutes, working with spoken English.\nReading: 60 minutes, interpreting written passages.\nWriting: 60 minutes, producing written responses.\nSpeaking: 11–14 minutes, demonstrating spoken communication.\nIELTS lists an overall test duration of 2 hours 45 minutes. Academic and General Training differ in Reading and Writing; do not book General Training just because it sounds easier.', IELTS),
             section('Do bachelor’s students need IELTS while master’s students do not?',
                     'There is no such Italy-wide rule. Language evidence and academic selection are separate requirements. A master’s applicant may need a certificate; a bachelor’s applicant may qualify for an exemption. Do not assume that a Nepalese qualification automatically proves English proficiency.'),
             section('A verified example: University of Padua',
                     'Padua’s published English-taught admissions policy generally requires B2; its IELTS B2 threshold is 6.0. It permits an exemption where the entry qualification was completed entirely in English: secondary education for bachelor’s entry, or the bachelor’s qualification for master’s entry. The English Studies master’s curriculum has a different C1 rule. Padua says 2027/28 language requirements will be published on 15 September; this example was reviewed on 7 September 2026.', PADUA),
             section('How to use a Medium of Instruction letter',
                     'If your programme accepts this exemption, ask your school or university for official evidence stating the qualification and that instruction was entirely in English. Submit it where the application requests language evidence and keep the admission office’s acceptance. A letter is evidence for an exemption, not an automatic replacement accepted everywhere.'),
             section('A preparation plan you can follow',
                     'Start with a timed practice test. Keep an error log for missed reading details and listening answers. Practise writing with feedback on organisation and clarity, and record short spoken answers to review fluency. Each week, repeat the section that is furthest from your target. Set your target from your programme’s overall and component requirements, not an agent’s universal score.'),
             section('Before paying for a test',
                     'Record the accepted test, overall score, minimum component scores, validity period, permitted delivery format and submission deadline for each programme. Compare any TOEFL, Cambridge or other alternatives named in that programme’s rules. Admission acceptance and visa documentation are separate checks.')
         ]),
    dict(slug='tolc-cisia', title='CEnT-S & TOLC: science, engineering and economics entry',
         summary='Learn the difference between the newer English CEnT-S and TOLC variants, including subjects, timing, scoring and a Sapienza programme example.',
         source_url=CISIA, sections=[
             section('Which test are you actually being asked to take?',
                     'CISIA is the test provider, not a single examination. CEnT-S replaced English TOLC-E, English TOLC-I and English TOLC-F from late November 2025. Other TOLC variants remain; an old English TOLC checklist should not be treated as a current booking instruction.',
                     'https://www.cisiaonline.it/cent/tutto-sul-CEnT/tutto-sul-CEnT'),
             section('CEnT-S format and scoring',
                     '55 questions in 110 minutes: Mathematics 15/30 minutes; Reasoning on texts and data 15/30; Biology 10/20; Chemistry 10/20; Physics 5/10. A correct answer earns 1 point, an unanswered question earns 0, and an incorrect answer loses 0.25. The official result is normalised; do not compare a raw practice total directly with an admission ranking.', CISIA),
             section('Which courses use it?',
                     'CEnT-S serves participating English-taught engineering, economics, pharmacy and other scientific programmes. Sapienza’s Applied Computer Science and Artificial Intelligence entry information lists CEnT-S and SAT options. That does not mean every Sapienza course accepts either test. Read the selection category for non-EU applicants living abroad before choosing a route.', SAPIENZA),
             section('How to prepare',
                     'Make a subject checklist from the syllabus. Practise mathematics without skipping algebra and data interpretation; review biology, chemistry and physics vocabulary in English. Use timed sections rather than borrowing time from your strongest subject. Review wrong answers before taking another full mock.'),
             section('Booking is not a university application',
                     'Registering for CISIA does not place you in a university ranking. Complete the programme application separately and submit the accepted result by its deadline. Check whether the programme accepts home testing, university-centre testing, or both, and allow time for the official result.')
         ]),
    dict(slug='imat', title='IMAT: English-taught Medicine and Surgery',
         summary='Find out when IMAT applies, how it differs from IELTS, and how to plan medicine admissions as a Nepalese applicant.',
         source_url=MEDICINE, sections=[
             section('What is IMAT?',
                     'IMAT is an academic entrance test associated with restricted-entry English-taught medicine programmes. It is not a general language certificate and is not the entrance test for every science course. Medicine and Surgery is a single-cycle degree entered after secondary education, rather than a standard two-year master’s after a bachelor’s.', MEDICINE),
             section('University examples and IELTS',
                     'Bologna lists IMAT for its English-taught Medicine and Surgery admission route. Padua’s language policy explicitly exempts candidates sitting IMAT for its English-taught Medicine and Surgery programme from a separate English certificate. Do not extend Padua’s exemption to another university.', PADUA),
             section('What should I study?',
                     'Use a preparation plan covering scientific understanding, quantitative reasoning and comprehension. Diagnose weaknesses first, then practise science questions in English and complete timed mocks. The academic-year ministry notice determines the assessed subjects, question distribution, time limit and scoring; no previous-year format or cut-off is presented here as a confirmed 2026/27 rule.'),
             section('Your application sequence from Nepal',
                     'Choose the programme, identify the applicant category and selection round, prepare the academic documents, complete the required university steps, and register for the examination through the route in the current notice. Keep a separate calendar for test registration, university selection and enrolment. A qualifying result is not itself an admission offer.'),
             section('What about private medicine programmes?',
                     'Do not assume IMAT is accepted. A private university may operate a separate test and selection process. Obtain the named programme’s examination instructions before paying for an IMAT preparation course.'),
             section('Dates, fees and score targets',
                     'There is no single guaranteed admission score. Seats and ranking category matter. This guide does not confirm a 2026/27 examination date, fee or seat allocation; use the published annual notice to complete those fields in your plan.',
                     'https://accessoprogrammato.mur.gov.it/')
         ]),
    dict(slug='sat', title='SAT: selected Italian bachelor’s programmes',
         summary='Understand the digital SAT, its Reading and Writing and Math sections, and examples at Bologna and Sapienza.',
         source_url=SAT, sections=[
             section('What is the SAT?',
                     'The SAT is an academic admission test. The digital test contains Reading and Writing plus Math. It has 54 Reading and Writing questions in 64 minutes and 44 Math questions in 70 minutes: 2 hours 14 minutes of testing, with a 10-minute break. Each section has two modules; the second module adapts to performance in the first.', SAT),
             section('Where is it used in Italy?',
                     'Bologna’s Economics and Finance bachelor’s admissions page provides a SAT-based application route and its 2026/27 call. Sapienza’s Applied Computer Science and Artificial Intelligence information lists SAT alongside CEnT-S. These are programme examples, not university-wide rules.', BOLOGNA),
             section('SAT versus IELTS',
                     'Use SAT for academic selection where it is accepted. Treat proof of English as a separate item until the programme explicitly says a SAT result satisfies that requirement too. Taking two tests unnecessarily costs money; omitting a required language certificate can leave an application incomplete.'),
             section('How to prepare and submit',
                     'Practise short reading passages, editing and mathematics under timed conditions. Review errors by topic rather than only watching the total score. Plan the test date backwards from the university’s score-receipt deadline, and follow its official score-reporting instructions. A booking confirmation is not a score report.')
         ]),
    dict(slug='university-specific-entrance-tests', title='Programme-specific tests, interviews & portfolios',
         summary='A practical checklist for courses with their own selection process, especially master’s programmes that assess your previous degree and subject knowledge.',
         source_url='https://www.universitaly.it/', sections=[
             section('Why there is no one test for all Italian universities',
                     'The course is the right unit for planning. Record its exact title, degree level, teaching language, academic year and applicant category. Two programmes at the same university can have different admission methods.'),
             section('Applying for a master’s after a Nepalese bachelor’s',
                     'Read the course’s academic prerequisites before booking any test. Prepare your transcript, subject descriptions and evidence of relevant coursework. Check whether the selection includes an interview, subject assessment, portfolio or a named standardised test. A language-certificate exemption does not waive academic assessment.'),
             section('Preparing for an interview or portfolio assessment',
                     'For an interview, practise explaining your previous coursework, projects and motivation with specific examples. For a portfolio, follow the page limit and file format, explain your own contribution and choose work that demonstrates the requested skills. Do not submit a generic collection to every programme.'),
             section('The checklist to complete before applying',
                     'Academic qualification and required subjects; language proof or accepted exemption; examination name and format; score and reporting method; interview or portfolio; application round for non-EU residents abroad; result date; enrolment deadline. Mark an item “not required” only when the programme says so.')
         ]),
]
