"""Normalize the supplied Italy Courses workbook into importable JSON.

The workbook is deliberately kept outside the repository. Run this script
locally after receiving a refreshed workbook, then review the generated JSON
before importing it into Django.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile
from xml.etree import ElementTree as ET

NS = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
URL_RE = re.compile(r'https?://[^\s|)]+')
BARE_DOMAIN_RE = re.compile(r'(?<![@/])(?:[a-z0-9-]+\.)+(?:it|eu|org|com)(?:/[^\s|)]*)?', re.I)

UNIVERSITIES = {
    'Florence': ('University of Florence', 'university-of-florence', 'Florence', 9, 'https://www.unifi.it/en', ['unifi.it']),
    'Padova': ('University of Padua', 'university-of-padua', 'Padua', 5, 'https://www.unipd.it/en/', ['unipd.it']),
    'Cafoscari': ("Ca' Foscari University of Venice", 'ca-foscari-university-of-venice', 'Venice', 5, 'https://www.unive.it/en/', ['unive.it']),
    'Sapienza': ('Sapienza University of Rome', 'sapienza-university-of-rome', 'Rome', 12, 'https://www.uniroma1.it/en', ['uniroma1.it']),
    'Siena': ('University of Siena', 'university-of-siena', 'Siena', 9, 'https://en.unisi.it/', ['unisi.it']),
    'Turin': ('University of Turin', 'university-of-turin', 'Turin', 1, 'https://en.unito.it/', ['unito.it']),
    'trieste': ('University of Trieste', 'university-of-trieste', 'Trieste', 6, 'https://www.units.it/en', ['units.it']),
    'Milan': ('University of Milan', 'university-of-milan', 'Milan', 3, 'https://www.unimi.it/en', ['unimi.it']),
    'Bergamo': ('University of Bergamo', 'university-of-bergamo', 'Bergamo', 3, 'https://en.unibg.it/', ['unibg.it']),
    'Pavia': ('University of Pavia', 'university-of-pavia', 'Pavia', 3, 'https://en.unipv.it/', ['unipv.eu', 'unipv.it']),
    'Politenico': ('Politecnico di Milano', 'politecnico-di-milano', 'Milan', 3, 'https://www.polimi.it/en', ['polimi.it']),
    'Degree Programmes (Insubria)': ('University of Insubria', 'university-of-insubria', 'Varese', 3, 'https://www.uninsubria.eu/', ['uninsubria.eu', 'cineca.it']),
    'Trento Masters Degrees': ('University of Trento', 'university-of-trento', 'Trento', 4, 'https://www.unitn.it/en', ['unitn.it']),
    'University di Bolzano Bachelors': ('Free University of Bozen-Bolzano', 'free-university-of-bozen-bolzano', 'Bolzano', 4, 'https://www.unibz.it/en/', ['unibz.it']),
    'University di Bolzano Master Co': ('Free University of Bozen-Bolzano', 'free-university-of-bozen-bolzano', 'Bolzano', 4, 'https://www.unibz.it/en/', ['unibz.it']),
    'LAquila': ("University of L'Aquila", 'university-of-laquila', "L'Aquila", 13, 'https://www.univaq.it/en/', ['univaq.it']),
    'Calabria': ('University of Calabria', 'university-of-calabria', 'Rende', 18, 'https://www.unical.it/', ['unical.it']),
    'Phd University of Cagliari': ('University of Cagliari', 'university-of-cagliari', 'Cagliari', 20, 'https://www.unica.it/en', ['unica.it']),
    'Naples Federico II': ('University of Naples Federico II', 'university-of-naples-federico-ii', 'Naples', 15, 'https://www.unina.it/en', ['unina.it']),
    'Masters (Messina)': ('University of Messina', 'university-of-messina', 'Messina', 15, 'https://international.unime.it/', ['unime.it']),
    'Bachelors (Messina)': ('University of Messina', 'university-of-messina', 'Messina', 15, 'https://international.unime.it/', ['unime.it']),
    'University of Pisa (Bachelor+Ma': ('University of Pisa', 'university-of-pisa', 'Pisa', 9, 'https://www.unipi.it/en/', ['unipi.it', 'cineca.it']),
    'University of Pisa(Phdcourse)': ('University of Pisa', 'university-of-pisa', 'Pisa', 9, 'https://www.unipi.it/en/', ['unipi.it']),
    'Bachelors (Parma)': ('University of Parma', 'university-of-parma', 'Parma', 8, 'https://www.unipr.it/en', ['unipr.it']),
    'Master (Parma)': ('University of Parma', 'university-of-parma', 'Parma', 8, 'https://www.unipr.it/en', ['unipr.it']),
    'Bachelors (Ca Foscari Universit': ("Ca' Foscari University of Venice", 'ca-foscari-university-of-venice', 'Venice', 5, 'https://www.unive.it/en/', ['unive.it']),
    'Masters (Ca Foscari University': ("Ca' Foscari University of Venice", 'ca-foscari-university-of-venice', 'Venice', 5, 'https://www.unive.it/en/', ['unive.it']),
    'Bachelors (Palermo)': ('University of Palermo', 'university-of-palermo', 'Palermo', 19, 'https://www.unipa.it/', ['unipa.it']),
    'Masters (Palermo)': ('University of Palermo', 'university-of-palermo', 'Palermo', 19, 'https://www.unipa.it/', ['unipa.it']),
    'University of Cassino and South': ('University of Cassino and Southern Lazio', 'university-of-cassino-and-southern-lazio', 'Cassino', 12, 'https://www.unicas.it/', ['unicas.it']),
    'University of Cassinoand Southe': ('University of Cassino and Southern Lazio', 'university-of-cassino-and-southern-lazio', 'Cassino', 12, 'https://www.unicas.it/', ['unicas.it']),
    'Universita_L_Orientale_Masters_': ("University of Naples L'Orientale", 'university-of-naples-lorientale', 'Naples', 15, 'https://www.unior.it/en', ['unior.it']),
    'Universita_Parthenope(Master)': ('University of Naples Parthenope', 'university-of-naples-parthenope', 'Naples', 15, 'https://www.uniparthenope.it/', ['uniparthenope.it']),
    'Universita_Bologna_Bachelors.': ('University of Bologna', 'university-of-bologna', 'Bologna', 8, 'https://www.unibo.it/en', ['unibo.it']),
    'Universita_Bologna_Masters.': ('University of Bologna', 'university-of-bologna', 'Bologna', 8, 'https://www.unibo.it/en', ['unibo.it']),
    'Universita_Tuscia-Unitus(Master': ('University of Tuscia', 'university-of-tuscia', 'Viterbo', 12, 'https://www.unitus.it/en/', ['unitus.it']),
    'University of Genova': ('University of Genoa', 'university-of-genoa', 'Genoa', 7, 'https://unige.it/en', ['unige.it']),
}

OFFICIAL_LOGO_URLS = {
    'university-of-padua': 'https://www.unipd.it/favicon.ico?favicon.fe08e1ad.ico',
    'university-of-trieste': 'https://portale.units.it/sites/default/files/favicon_5.ico',
    'university-of-pavia': 'https://en.unipv.it/themes/custom/unipv_fed/favicons/favicon.ico',
    'politecnico-di-milano': 'https://www.polimi.it/_assets/4b51f00386267395f41e0940abbcd656/Icons/favicon.ico',
    'university-of-insubria': 'https://www.uninsubria.eu/themes/custom/uninsubria_base/favicon/favicon.ico',
    'university-of-trento': '',
    'free-university-of-bozen-bolzano': 'https://www.unibz.it/_resources/themes/unibz/images/fav/apple-touch-icon-57x57.png',
    'university-of-laquila': 'https://www.univaq.it/images/graphics/header/logo-univaqit.svg',
    'university-of-calabria': 'https://cdn.jsdelivr.net/gh/UniversitaDellaCalabria/unicms-template-unical@1.9.3/src/unicms_template_unical/static/images/favicon/favicon-32x32.png',
    'university-of-naples-federico-ii': 'https://www.unina.it/o/ThemaL74GA66_3/images/favicon.ico',
    'university-of-messina': 'https://international.unime.it/themes/custom/unime_base/icons/favicon.ico',
    'university-of-pisa': 'https://www.unipi.it/wp-content/uploads/Raggruppa-3020.svg',
    'university-of-parma': 'https://www.unipr.it/themes/custom/unipr_2025/assets/favicon/apple-touch-icon.png',
    'university-of-palermo': 'https://skin-new.unipa.it/images/favicon.ico',
    'university-of-cassino-and-southern-lazio': 'https://www.unicas.it/media/tfrlxtmu/favicon.ico',
    'university-of-naples-lorientale': 'https://www.unior.it/themes/custom/unior_base/favicon/apple-touch-icon.png',
    'university-of-tuscia': 'https://www.unitus.it/wp-content/uploads/2023/11/cropped-favicon-1-32x32.jpg',
    'university-of-genoa': 'https://unige.it/core/misc/favicon.ico',
}

CORE_LABELS = {
    'Course Name': 'title',
    'Department': 'department',
    'Deparment': 'department',
    'Degree Class Code': 'degree_class_code',
    'Course Code': 'degree_class_code',
    'Study location': 'study_location',
    'Type': 'course_type',
    'Nominal duration': 'nominal_duration',
    'Study language': 'study_language',
    'Application fee': 'application_fee',
    'Pre-Enrollment fee': 'pre_enrollment_fee',
    'Tuition fee': 'tuition_fee',
    'CEnT Requirements': 'cent_requirements',
    'Language Requirements': 'language_requirements',
    'Other Requirements': 'other_requirements',
    'Entry qualification': 'entry_qualification',
    'Studies commence': 'studies_commence',
    'More information': 'more_information',
    'Course Link': 'course_link',
    'Additional Info': 'additional_info',
    'Additonal Info': 'additional_info',
}


def clean(value: str) -> str:
    return re.sub(r'\s+', ' ', value or '').strip()


def slugify(value: str) -> str:
    value = value.lower().replace('&', ' and ')
    value = re.sub(r"[^a-z0-9]+", '-', value).strip('-')
    return value[:230]


def display_title(value: str) -> str:
    value = clean(value)
    value = re.sub(r"^(?:bachelor'?s degree|bachelor'?s|master of science|master'?s degree|master|phd|ph\.d\.)\s+in\s+", '', value, flags=re.I)
    return value or 'Untitled course'


def urls_in(value: str) -> list[str]:
    result = []
    for url in URL_RE.findall(value or ''):
        url = url.rstrip('.,;')
        if url not in result:
            result.append(url)
    return result


def source_candidates(value: str) -> list[str]:
    result = urls_in(value)
    for bare in BARE_DOMAIN_RE.findall(value or ''):
        bare = bare.rstrip('.,;')
        candidate = bare if bare.startswith('http') else f'https://{bare}'
        if candidate not in result:
            result.append(candidate)
    return result


def domain_allowed(url: str, domains: list[str]) -> bool:
    host = urlparse(url).netloc.lower().split(':')[0]
    return any(host == domain or host.endswith('.' + domain) for domain in domains)


def derive_degree(course_type: str, title: str) -> str:
    value = f'{course_type} {title}'.lower()
    if 'phd' in value or 'dottorato' in value or 'doctoral' in value:
        return 'PhD'
    if 'master' in value or 'graduate' in value or 'laurea magistrale' in value or 'second-cycle' in value:
        return "Master's degree"
    if 'bachelor' in value or 'first-cycle' in value or 'laurea (' in value:
        return "Bachelor's degree"
    return 'Degree programme'


def parse_workbook(path: Path):
    with ZipFile(path) as archive:
        shared = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        strings = [''.join(t.text or '' for t in si.findall('.//a:t', NS)) for si in shared.findall('a:si', NS)]
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        rels_root = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        rels = {rel.attrib['Id']: rel.attrib['Target'] for rel in rels_root}
        for sheet in workbook.findall('a:sheets/a:sheet', NS):
            name = sheet.attrib['name'].strip()
            target = rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target = f'xl/{target}' if not target.startswith('xl/') else target
            root = ET.fromstring(archive.read(target))
            rows = []
            for row in root.findall('.//a:sheetData/a:row', NS):
                values = []
                for cell in row.findall('a:c', NS):
                    value = cell.find('a:v', NS)
                    text = '' if value is None else value.text or ''
                    if cell.attrib.get('t') == 's':
                        text = strings[int(text)]
                    elif cell.attrib.get('t') == 'inlineStr':
                        text = ''.join(t.text or '' for t in cell.findall('.//a:t', NS))
                    text = clean(text)
                    if text:
                        values.append(text)
                if values:
                    rows.append(values)
            blocks = []
            current = None
            for row in rows:
                if any(re.fullmatch(r'#\d+', value) for value in row):
                    if current:
                        blocks.append(current)
                    current = []
                elif current is not None:
                    current.append(row)
            if current:
                blocks.append(current)
            yield name, blocks


def normalize(path: Path) -> dict:
    universities = OrderedDict()
    courses = []
    excluded = []
    for sheet_name, blocks in parse_workbook(path):
        if sheet_name not in UNIVERSITIES:
            excluded.append({'sheet': sheet_name, 'reason': 'No university metadata mapping'})
            continue
        university_name, university_slug, city, region_code, website, domains = UNIVERSITIES[sheet_name]
        universities[university_slug] = {
            'name': university_name,
            'slug': university_slug,
            'city': city,
            'region_code': region_code,
            'website': website,
            'logo_url': OFFICIAL_LOGO_URLS.get(university_slug, ''),
            'source_domains': domains,
        }
        for number, block in enumerate(blocks, 1):
            raw = OrderedDict()
            for row in block:
                label = clean(row[0]).rstrip(':')
                value = clean(' | '.join(row[1:]))
                if value:
                    raw[label] = f"{raw[label]}\n{value}" if label in raw else value
            title = display_title(raw.get('Course Name', ''))
            if title == 'Untitled course':
                excluded.append({'sheet': sheet_name, 'number': number, 'reason': 'Missing course name'})
                continue
            all_urls = []
            for value in raw.values():
                for url in source_candidates(value):
                    if url not in all_urls:
                        all_urls.append(url)
            official_urls = [url for url in all_urls if domain_allowed(url, domains)]
            labeled_priority = []
            for label in ('Course Link', 'More information'):
                for url in source_candidates(raw.get(label, '')):
                    if domain_allowed(url, domains) and url not in labeled_priority:
                        labeled_priority.append(url)
            primary = (labeled_priority + official_urls + all_urls[:1])[0] if (labeled_priority or official_urls or all_urls) else ''
            field_values = []
            normalized = {}
            for label, value in raw.items():
                key = CORE_LABELS.get(label)
                if key:
                    normalized[key] = value
                elif value:
                    field_values.append({'label': label[:160], 'value': value[:10000]})
            course_type = normalized.get('course_type', '')
            department = normalized.get('department', '') or 'Academic department not specified in source'
            slug_base = slugify(title)
            slug = slug_base if university_slug == 'university-of-padua' else f'{university_slug}-{slug_base}'
            source_url = primary
            if not domain_allowed(source_url, domains):
                source_url = ''
            source_note = f"Workbook source URLs: {' | '.join(official_urls[:8])}" if official_urls else 'No official university-domain URL found in workbook.'
            summary = normalized.get('additional_info', '').split('\n')[0][:1000]
            if not summary:
                summary = f"{title} at {university_name}."
            courses.append({
                'sheet': sheet_name,
                'source_row': number,
                'university_slug': university_slug,
                'title': title,
                'slug': slug,
                'summary': summary,
                'department': department[:240],
                'degree': derive_degree(course_type, title),
                'discipline': department[:100] if department else title[:100],
                'degree_class_code': normalized.get('degree_class_code', '')[:80],
                'study_location': normalized.get('study_location', '')[:240],
                'course_type': course_type[:160],
                'nominal_duration': normalized.get('nominal_duration', '')[:100],
                'study_language': normalized.get('study_language', '')[:120],
                'application_fee': normalized.get('application_fee', '')[:200],
                'pre_enrollment_fee': normalized.get('pre_enrollment_fee', '')[:200],
                'tuition_fee': normalized.get('tuition_fee', '')[:200],
                'cent_requirements': normalized.get('cent_requirements', ''),
                'language_requirements': normalized.get('language_requirements', ''),
                'other_requirements': normalized.get('other_requirements', ''),
                'studies_commence': normalized.get('studies_commence', ''),
                'more_information': normalized.get('more_information', '')[:10000],
                'entry_qualification': normalized.get('entry_qualification', ''),
                'course_link': normalized.get('course_link', '')[:10000],
                'additional_info': normalized.get('additional_info', ''),
                'source_url': source_url,
                'source_urls': official_urls[:12],
                'source_note': source_note,
                'extra_fields': field_values,
                'verified': bool(source_url),
            })
    duplicate_counts = {}
    for course in courses:
        duplicate_counts[course['slug']] = duplicate_counts.get(course['slug'], 0) + 1
    for course in courses:
        if duplicate_counts[course['slug']] > 1:
            course['slug'] = f"{course['slug']}-{course['source_row']}"[:240]
    return {'version': 1, 'workbook': path.name, 'universities': list(universities.values()), 'courses': courses, 'excluded': excluded}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('workbook', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = normalize(args.workbook)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"wrote {len(data['courses'])} courses for {len(data['universities'])} universities")
    print(f"excluded {len(data['excluded'])} workbook blocks")
    print(f"official-source candidates {sum(1 for c in data['courses'] if c['verified'])}")


if __name__ == '__main__':
    main()
