"""Apply the reviewed official-source confirmations to the normalized Italy catalogue.

The workbook is a supplied snapshot, so this is intentionally an explicit audit
map rather than a fuzzy title matcher.  A record is promoted only when its
official university page or official course catalogue entry was checked.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


AUDIT_DATE = "2026-09-19"


def entry(university: str, title: str, url: str, *, row: int | None = None, note: str = ""):
    return (university, row, title), (url, note)


CONFIRMED = dict([
    entry("university-of-florence", "Geography, Spatial Management, Heritage for International Cooperation", "https://www.spatialmanagement.unifi.it/vp-144-about-us.html"),
    entry("university-of-florence", "Physical and Astrophysical Sciences", "https://www.unifi.it/en/study-us/degree-programs/second-cycle-degree/physical-and-astrophysical-sciences"),
    entry("university-of-florence", "Tropical and Subtropical Agriculture", "https://www.tropicalagriculture.unifi.it/"),
    entry("university-of-padua", "Astrophysics and Cosmology", "https://www.unipd.it/en/corsi-di-laurea/astrophysics-and-cosmology"),
    entry("university-of-padua", "Management for Sustainable Firms", "https://www.economia.unipd.it/en/node/2527"),
    entry("university-of-padua", "Food, Nutrition and Health", "https://www.agrariamedicinaveterinaria.unipd.it/en/courses/bachelors-first-cycle-and-masters-second-cycle-degrees/food-nutrition-and-health"),
    entry("university-of-padua", "Electrical Engineering", "https://www.unipd.it/en/corsi-di-laurea/electrical-engineering"),
    entry("university-of-padua", "Energy Engineering", "https://www.unipd.it/en/corsi-di-laurea/energy-engineering"),
    entry("university-of-padua", "Intelligent Civil Infrastructures Engineering", "https://www.dicea.unipd.it/en/courses/courses-held-english/intelligent-civil-infrastructures-engineering/occupational"),
    entry("university-of-padua", "Mathematical Engineering", "https://www.unipd.it/en/ammissioni-ing-mathematical"),
    entry("university-of-padua", "Evolutionary Biology", "https://biologia.biologia.unipd.it/en/laurea-magistrale/master-degree-in-evolutionary-biology/"),
    entry("university-of-padua", "Quantitative and Computational Biosciences", "https://quacbio.biologia.unipd.it/general-overview/"),
    entry("university-of-insubria", "LAW", "https://uninsubria.coursecatalogue.cineca.it/corsi/2026/10351?linguaCC=EN", row=31),
    entry("university-of-insubria", "LAW", "https://uninsubria.coursecatalogue.cineca.it/corsi/2026/10355?linguaCC=EN", row=32),
    entry("university-of-laquila", "Business Administration, Economics and Finance", "https://www.univaq.it/en/section.php?id=806&lang_s=en"),
    entry("university-of-laquila", "Computer and Systems Engineering", "https://www.univaq.it/en/section.php?id=806&lang_s=en"),
    entry("university-of-laquila", "Mathematics", "https://www.univaq.it/en/section.php?id=806&lang_s=en"),
    entry("university-of-laquila", "Mechanical Engineering", "https://www.univaq.it/en/section.php?id=806&lang_s=en"),
    entry("university-of-laquila", "Physics", "https://www.univaq.it/en/section.php?id=806&lang_s=en"),
    entry("university-of-laquila", "Structural and Construction Engineering", "https://www.univaq.it/en/section.php?id=806&lang_s=en"),
    entry("university-of-naples-federico-ii", "Architecture and Heritage", "https://www.corsi.unina.it/DB2/"),
    entry("university-of-pisa", "ECONOMICS AND COMMERCE", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/ECOR-L"),
    entry("university-of-pisa", "GEOLOGY", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/GLYR-L"),
    entry("university-of-pisa", "COMPUTER SCIENCE", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WIF-LM"),
    entry("university-of-pisa", "COMMUNICATIONS ENGINEERING", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WCT-LM"),
    entry("university-of-pisa", "COMPUTER ENGINEERING", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WCN-LM"),
    entry("university-of-pisa", "CYBERSECURITY", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WCYR-LM"),
    entry("university-of-pisa", "ECONOMICS", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WESR-LM"),
    entry("university-of-pisa", "ROBOTICS AND AUTOMATION ENGINEERING", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WIM-LM"),
    entry("university-of-pisa", "AEROSPACE ENGINEERING", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WIAR-LM"),
    entry("university-of-pisa", "NUCLEAR ENGINEERING", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WSNR-LM"),
    entry("university-of-pisa", "MATERIALS AND NANOTECHNOLOGY", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WNN-LM"),
    entry("university-of-pisa", "EXPLORATION AND APPLIED GEOPHYSICS", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WAGR-LM"),
    entry("university-of-pisa", "MATHEMATICS", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WMAR-LM"),
    entry("university-of-pisa", "NEUROSCIENCE", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WNCR-LM"),
    entry("university-of-pisa", "BIONICS ENGINEERING", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WBER-LM"),
    entry("university-of-pisa", "ENGINEERING OF PAPER AND CARDBOARD", "https://unipi.coursecatalogue.cineca.it/corsi-code/2026/WEP-LM"),
    entry("university-of-palermo", "Nursing (Professional Practice)", "https://www.unipa.it/Avvio-procedure-di-definizione-dellOfferta-Formativa-2026-2027/"),
    entry("university-of-palermo", "Automation and Systems Engineering", "https://www.unipa.it/dipartimenti/ingegneria/cds/automationandsystemsengineering2332"),
    entry("university-of-palermo", "Business Economic Sciences", "https://www.unipa.it/dipartimenti/seas/cds/scienzeeconomicoaziendali2340/en/"),
    entry("university-of-palermo", "Computer Science and Artificial Intelligence", "https://www.unipa.it/dipartimenti/matematicaeinformatica/cds/computerscienceandartificialintelligence2323/index.html"),
    entry("university-of-palermo", "Cooperation, Development, Migrations", "https://www.unipa.it/dipartimenti/cultureesocieta/cds/cooperazionesviluppoemigrazioni2232/en/presentation/"),
    entry("university-of-palermo", "Economic and Financial Sciences", "https://www.unipa.it/dipartimenti/seas/cds/scienzeeconomicheefinanziarie2063/"),
    entry("university-of-palermo", "Environmental Science and Technologies", "https://www.unipa.it/dipartimenti/distem/cds/scienzeetecnologieambientali2405/en/?pagina=presentazione"),
    entry("university-of-palermo", "Electronics and Telecommunications Engineering (fully online)", "https://www.unipa.it/dipartimenti/ingegneria/cds/electronicsandtelecommunicationsengineeringfullyonline2258"),
    entry("university-of-palermo", "Electronics Engineering", "https://www.unipa.it/dipartimenti/ingegneria/cds/electronicsengineering2234/en/index.html"),
    entry("university-of-palermo", "International Relations", "https://www.unipa.it/dipartimenti/dems/cds/internationalrelationsrelazioniinternazionali2342/en/"),
    entry("university-of-palermo", "International Relations, Politics & Trade (fully online)", "https://www.unipa.it/dipartimenti/dems/cds/internationalrelationspoliticstradefullyonline2262"),
    entry("university-of-palermo", "Management Engineering", "https://www.unipa.it/dipartimenti/ingegneria/cds/managementengineering2255"),
    entry("university-of-palermo", "Management Engineering (online)", "https://www.unipa.it/dipartimenti/ingegneria/cds/managementengineering2256"),
    entry("university-of-palermo", "Mediterranean Food Science and Technology", "https://www.unipa.it/dipartimenti/saaf/cds/mediterraneanfoodscienceandtechnology2238/en/?pagina=presentazione"),
    entry("university-of-palermo", "Migrations, Rights, Integration", "https://www.unipa.it/dipartimenti/di.gi./cds/migrationrightsintegration2337/"),
    entry("university-of-palermo", "Neuroscience", "https://www.unipa.it/dipartimenti/bi.n.d./cds/neuroscience2331"),
    entry("university-of-palermo", "Spatial Planning", "https://www.unipa.it/dipartimenti/architettura/cds/spatialplanning2333/?pagina=presentazione"),
    entry("university-of-palermo", "Statistics and Data Science", "https://www.unipa.it/dipartimenti/seas/cds/statisticaedatascience2235/en/?pagina=presentazione"),
    entry("university-of-palermo", "Tourism Systems and Hospitality Management", "https://www.unipa.it/dipartimenti/seas/cds/tourismsystemsandhospitalitymanagement2338"),
    entry("university-of-palermo", "Transnational German Studies", "https://www.unipa.it/dipartimenti/scienzeumanistiche/cds/transnationalgermanstudies2230/"),
])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", type=Path)
    args = parser.parse_args()
    data = json.loads(args.data_path.read_text(encoding="utf-8"))
    updated = 0
    missing = []
    for course in data["courses"]:
        key = (course["university_slug"], course["source_row"], course["title"])
        fallback = (course["university_slug"], None, course["title"])
        match = CONFIRMED.get(key) or CONFIRMED.get(fallback)
        if not match or course.get("verification_status") == "verified":
            if course.get("verification_status") != "verified" and match is None:
                missing.append(key)
            continue
        url, note = match
        course["verified"] = True
        course["verification_status"] = "verified"
        course["verified_source_url"] = url
        course["verified_at"] = AUDIT_DATE
        course["source_url"] = url
        if url not in course["source_urls"]:
            course["source_urls"].insert(0, url)
        course["source_note"] = note or f"Verified against the official university course page or official course catalogue on {AUDIT_DATE}."
        updated += 1

    data["verification_summary"] = {
        "verified_courses": sum(c.get("verification_status") == "verified" for c in data["courses"]),
        "pending_courses": sum(c.get("verification_status") != "verified" for c in data["courses"]),
        "excluded_blocks": len(data.get("excluded", [])),
        "method": "Official university course pages and official course catalogues were checked record by record; records without a confirmed official source remain pending and unpublished.",
    }
    args.data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated {updated} records")
    print(data["verification_summary"])
    if missing:
        print("still pending:")
        for item in missing:
            print(item)


if __name__ == "__main__":
    main()
