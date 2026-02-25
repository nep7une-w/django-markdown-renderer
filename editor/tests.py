from django.test import TestCase
from django.urls import reverse


class EditorViewsTests(TestCase):
    def test_render_markdown_returns_html(self):
        response = self.client.post(
            reverse('render_markdown'),
            {'content': 'Inline math: $a^2 + b^2 = c^2$'},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('html', payload)
        self.assertIn('arithmatex', payload['html'])

    def test_export_md_returns_markdown_file(self):
        response = self.client.post(
            reverse('export_md'),
            {'content': '# Title'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/markdown; charset=utf-8')
        self.assertIn('attachment; filename="document.md"', response['Content-Disposition'])
        self.assertIn('# Title', response.content.decode('utf-8'))

    def test_export_pdf_returns_pdf(self):
        response = self.client.post(
            reverse('export_pdf'),
            {'content': 'Equation: $E=mc^2$'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="document.pdf"', response['Content-Disposition'])
        self.assertGreater(len(response.content), 1000)
