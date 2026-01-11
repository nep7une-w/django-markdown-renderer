from io import BytesIO
import base64
import html as html_lib
import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import markdown
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from xhtml2pdf import pisa

MARKDOWN_EXTENSIONS = [
    'fenced_code',
    'tables',
    'toc',
    'pymdownx.arithmatex',
]


def markdown_to_html(text):
    return markdown.markdown(
        text,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs={
            'pymdownx.arithmatex': {
                'generic': True,
            }
        },
    )


INLINE_MATH_RE = re.compile(r'\\\((.+?)\\\)', re.DOTALL)
DISPLAY_MATH_RE = re.compile(r'\\\[(.+?)\\\]', re.DOTALL)


def math_to_png_base64(formula, fontsize=14, dpi=200):
    fig = plt.figure()
    text = fig.text(0, 0, f'${formula}$', fontsize=fontsize)
    fig.canvas.draw()
    bbox = text.get_window_extent()
    fig.set_size_inches(bbox.width / dpi, bbox.height / dpi)
    fig.patch.set_alpha(0.0)
    buffer = BytesIO()
    fig.savefig(
        buffer,
        format='png',
        dpi=dpi,
        transparent=True,
        bbox_inches='tight',
        pad_inches=0.05,
    )
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def replace_math_with_images(html):
    def render_inline(match):
        formula = match.group(1).strip()
        encoded = math_to_png_base64(formula, fontsize=14)
        alt = html_lib.escape(formula)
        return f'<img src="data:image/png;base64,{encoded}" alt="{alt}" />'

    def render_block(match):
        formula = match.group(1).strip()
        encoded = math_to_png_base64(formula, fontsize=18)
        alt = html_lib.escape(formula)
        return (
            '<div class="math-block">'
            f'<img src="data:image/png;base64,{encoded}" alt="{alt}" />'
            '</div>'
        )

    html = DISPLAY_MATH_RE.sub(render_block, html)
    return INLINE_MATH_RE.sub(render_inline, html)


@ensure_csrf_cookie
def editor_view(request):
    return render(request, 'editor.html')


@require_POST
def render_markdown(request):
    content = request.POST.get('content', '')
    html = markdown_to_html(content)
    return JsonResponse({'html': html})


@require_POST
def export_md(request):
    content = request.POST.get('content', '')
    response = HttpResponse(content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="document.md"'
    return response


@require_POST
def export_pdf(request):
    content = request.POST.get('content', '')
    html = markdown_to_html(content)
    html = replace_math_with_images(html)
    html_doc = f"""
    <html>
    <head>
        <meta charset='utf-8' />
        <style>
            body {{ font-family: 'DejaVu Sans', sans-serif; }}
            pre {{ background: #f6f6f6; padding: 12px; border-radius: 6px; }}
            code {{ font-family: 'DejaVu Sans Mono', monospace; }}
            .math-block {{ margin: 12px 0; text-align: center; }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

    pdf_file = BytesIO()
    result = pisa.CreatePDF(src=BytesIO(html_doc.encode('utf-8')), dest=pdf_file)
    if result.err:
        return HttpResponse('Failed to generate PDF.', status=500)

    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="document.pdf"'
    return response
