import {Link} from '@tanstack/react-router';

export function TestGuide(){
  return <section className="container test-guide" aria-labelledby="test-choice">
    <h2 id="test-choice">Which test do you actually need?</h2>
    <p>Start with your course, not a test booking. English proficiency and academic entrance exams answer two different questions. A course can require both, one, or an approved alternative.</p>
    <div className="notice"><p><strong>Bachelor’s does not automatically mean IELTS. Master’s does not automatically mean an exemption.</strong> Your previous teaching language, accepted evidence and programme rules decide this. A Medium of Instruction letter works only where the university accepts that exemption.</p></div>
    <div className="table-scroll" tabIndex={0} role="region" aria-label="Test selection guide">
      <table>
        <caption>Starting points for students applying from Nepal</caption>
        <thead><tr><th scope="col">Your study plan</th><th scope="col">What to prepare</th><th scope="col">Read the guide</th></tr></thead>
        <tbody>
          <tr><th scope="row">English-taught bachelor’s or master’s</th><td>Language certificate or an accepted exemption. Assess academic selection separately.</td><td><Link to="/test-preparation/english-proficiency-tests">IELTS & English proof</Link></td></tr>
          <tr><th scope="row">Selected science, engineering or economics bachelor’s</th><td>The specified CEnT-S, TOLC variant, SAT or programme test. They are not universally interchangeable.</td><td><Link to="/test-preparation/tolc-cisia">CEnT-S & TOLC</Link></td></tr>
          <tr><th scope="row">English-taught Medicine and Surgery</th><td>IMAT where the programme specifies it; check private-university selection separately.</td><td><Link to="/test-preparation/imat">IMAT explained</Link></td></tr>
          <tr><th scope="row">A programme that accepts SAT</th><td>Academic test result plus any separate language evidence.</td><td><Link to="/test-preparation/sat">SAT explained</Link></td></tr>
          <tr><th scope="row">Master’s with an interview or portfolio</th><td>Evidence of relevant prior study and the exact assessment requested.</td><td><Link to="/test-preparation/university-specific-entrance-tests">Programme selection</Link></td></tr>
        </tbody>
      </table>
    </div>
    <h3>Verified university examples</h3>
    <p>Padua’s English-language policy covers both degree levels and accepts qualifying English-medium education exemptions. Bologna’s Economics and Finance page sets out its SAT route. Sapienza’s Applied Computer Science and AI information lists SAT and CEnT-S options. The individual guides explain these examples and include the supporting university references.</p>
    <p className="fine-print">Reviewed 7 September 2026. Examples are programme-specific, not an exhaustive list of Italian universities. Applicants living in Nepal should identify the non-EU resident-abroad selection round before booking.</p>
    <h2>Understand each test before you prepare</h2>
  </section>;
}
