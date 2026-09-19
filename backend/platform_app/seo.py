from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape
from . import models as m


def _base_url():
    return getattr(settings, 'PUBLIC_SITE_URL', 'https://kashyapadvisors.com').rstrip('/')


def robots(request):
    body = f'User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {_base_url()}/sitemap.xml\n'
    return HttpResponse(body, content_type='text/plain')


def sitemap(request):
    base = _base_url()
    urls = [
        ('/', '1.0'), ('/study-in-italy', '0.9'), ('/universities', '0.9'),
        ('/regions', '0.8'), ('/scholarships', '0.8'), ('/services', '0.8'),
        ('/test-preparation', '0.7'), ('/student-journey', '0.8'),
        ('/blog', '0.8'), ('/about', '0.6'), ('/careers', '0.5'),
        ('/contact', '0.6'),
    ]
    for model, prefix in ((m.Region, '/regions/'), (m.University, '/universities/'),
                          (m.Scholarship, '/scholarships/'), (m.Article, '/blog/'),
                          (m.Career, '/careers/')):
        urls.extend((f'{prefix}{obj.slug}', '0.7') for obj in model.objects.filter(published=True))
    for obj in m.Page.objects.filter(published=True):
        if obj.kind in {'service', 'test'}:
            prefix = '/services/' if obj.kind == 'service' else '/test-preparation/'
            urls.append((f'{prefix}{obj.slug}', '0.6'))
    entries = ''.join(
        f'<url><loc>{escape(base + path)}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>'
        for path, priority in urls
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>'
    return HttpResponse(xml, content_type='application/xml')
