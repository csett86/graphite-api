# coding: utf-8
"""Tests that require Cairo for image rendering (PNG/SVG/PDF)."""
import json
import os
import time

from graphite_render._vendor import whisper

from . import TestCase, WHISPER_DIR

try:
    from flask_caching import Cache
except ImportError:
    Cache = None


class RenderCairoTest(TestCase):
    """Tests that require Cairo for rendering images."""
    db = os.path.join(WHISPER_DIR, 'test.wsp')
    url = '/render'

    def create_db(self):
        whisper.create(self.db, [(1, 60)])

        self.ts = int(time.time())
        whisper.update(self.db, 1.0, self.ts - 2)
        whisper.update(self.db, 0.5, self.ts - 1)
        whisper.update(self.db, 1.5, self.ts)

    def test_render_view_pdf(self):
        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'pdf'})
        self.assertEqual(response.headers['Content-Type'], 'application/x-pdf')

    def test_render_view_png(self):
        response = self.app.get(self.url, query_string={'target': 'test'})
        self.assertEqual(response.headers['Content-Type'], 'image/png')

    def test_render_constant_line_png(self):
        response = self.app.get(self.url, query_string={
            'target': 'constantLine(12)'})
        self.assertEqual(response.headers['Content-Type'], 'image/png')

    def test_render_options(self):
        self.create_db()
        db2 = os.path.join(WHISPER_DIR, 'foo.wsp')
        whisper.create(db2, [(1, 60)])
        ts = int(time.time())
        whisper.update(db2, 0.5, ts - 2)

        for qs in [
            {'logBase': 'e'},
            {'logBase': 1},
            {'logBase': 0.5},
            {'logBase': 10},
            {'margin': -1},
            {'colorList': 'orange,green,blue,#0f00f0'},
            {'bgcolor': 'orange'},
            {'bgcolor': '000000'},
            {'bgcolor': '#000000'},
            {'bgcolor': '123456'},
            {'bgcolor': '#123456'},
            {'bgcolor': '#12345678'},
            {'bgcolor': 'aaabbb'},
            {'bgcolor': '#aaabbb'},
            {'bgcolor': '#aaabbbff'},
            {'fontBold': 'true'},
            {'title': 'Hellò'},
            {'title': 'true'},
            {'vtitle': 'Hellò'},
            {'title': 'Hellò', 'yAxisSide': 'right'},
            {'uniqueLegend': 'true', '_expr': 'secondYAxis({0})'},
            {'uniqueLegend': 'true', 'vtitleRight': 'foo',
             '_expr': 'secondYAxis({0})'},
            {'rightWidth': '1', '_expr': 'secondYAxis({0})'},
            {'rightDashed': '1', '_expr': 'secondYAxis({0})'},
            {'rightColor': 'black', '_expr': 'secondYAxis({0})'},
            {'leftWidth': '1', 'target': ['secondYAxis(foo)', 'test']},
            {'leftDashed': '1', 'target': ['secondYAxis(foo)', 'test']},
            {'leftColor': 'black', 'target': ['secondYAxis(foo)', 'test']},
            {'width': '10', '_expr': 'secondYAxis({0})'},
            {'logBase': 'e', 'target': ['secondYAxis(foo)', 'test']},
            {'graphOnly': 'true', 'yUnitSystem': 'si'},
            {'graphOnly': 'true', 'yUnitSystem': 'wat'},
            {'lineMode': 'staircase'},
            {'lineMode': 'slope'},
            {'lineMode': 'slope', 'from': '-1s'},
            {'lineMode': 'connected'},
            {'min': 1, 'max': 2, 'thickness': 2, 'yUnitSystem': 'none'},
            {'yMax': 5, 'yLimit': 0.5, 'yStep': 0.1},
            {'yMax': 'max', 'yUnitSystem': 'binary'},
            {'yMaxLeft': 5, 'yLimitLeft': 0.5, 'yStepLeft': 0.1,
             '_expr': 'secondYAxis({0})'},
            {'yMaxRight': 5, 'yLimitRight': 0.5, 'yStepRight': 0.1,
             '_expr': 'secondYAxis({0})'},
            {'yMin': 0, 'yLimit': 0.5, 'yStep': 0.1},
            {'yMinLeft': 0, 'yLimitLeft': 0.5, 'yStepLeft': 0.1,
             '_expr': 'secondYAxis({0})'},
            {'yMinRight': 0, 'yLimitRight': 0.5, 'yStepRight': 0.1,
             '_expr': 'secondYAxis({0})'},
            {'areaMode': 'stacked', '_expr': 'stacked({0})'},
            {'lineMode': 'staircase', '_expr': 'stacked({0})'},
            {'areaMode': 'first', '_expr': 'stacked({0})'},
            {'areaMode': 'all', '_expr': 'stacked({0})'},
            {'areaMode': 'all', 'areaAlpha': 0.5, '_expr': 'secondYAxis({0})'},
            {'areaMode': 'all', 'areaAlpha': 0.5,
             'target': ['secondYAxis(foo)', 'test']},
            {'areaMode': 'stacked', 'areaAlpha': 0.5, '_expr': 'stacked({0})'},
            {'areaMode': 'stacked', 'areaAlpha': 'a', '_expr': 'stacked({0})'},
            {'areaMode': 'stacked', '_expr': 'drawAsInfinite({0})'},
            {'_expr': 'dashed(lineWidth({0}, 5))'},
            {'target': 'areaBetween(*)'},
            {'drawNullAsZero': 'true'},
            {'_expr': 'drawAsInfinite({0})'},
            {'graphType': 'pie', 'pieMode': 'average', 'title': 'Pie'},
            {'graphType': 'pie', 'pieMode': 'maximum', 'title': 'Pie'},
            {'graphType': 'pie', 'pieMode': 'minimum', 'title': 'Pie'},
            {'graphType': 'pie', 'pieMode': 'average', 'hideLegend': 'true'},
            {'graphType': 'pie', 'pieMode': 'average', 'valueLabels': 'none'},
            {'graphType': 'pie', 'pieMode': 'average',
             'valueLabels': 'number'},
            {'graphType': 'pie', 'pieMode': 'average', 'pieLabels': 'rotated'},
            {'graphType': 'pie', 'pieMode': 'average', 'areaAlpha': '0.1'},
            {'graphType': 'pie', 'pieMode': 'average', 'areaAlpha': 'none'},
            {'graphType': 'pie', 'pieMode': 'average',
             'valueLabelsColor': 'white'},
            {'noCache': 'true'},
            {'cacheTimeout': 5},
            {'cacheTimeout': 5},  # cache hit
            {'tz': 'Europe/Berlin'},
        ]:
            if qs.setdefault('target', ['foo', 'test']) == ['foo', 'test']:
                if '_expr' in qs:
                    expr = qs.pop('_expr')
                    qs['target'] = [expr.format(t) for t in qs['target']]
            response = self.app.get(self.url, query_string=qs)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'image/png')
            if Cache is None or qs.get('noCache'):
                self.assertEqual(response.headers['Pragma'], 'no-cache')
                self.assertEqual(response.headers['Cache-Control'], 'no-cache')
                self.assertFalse('Expires' in response.headers)
            else:
                self.assertEqual(response.headers['Cache-Control'],
                                 'max-age={0}'.format(
                                     qs.get('cacheTimeout', 60)))
                self.assertNotEqual(response.headers['Cache-Control'],
                                    'no-cache')
                self.assertFalse('Pragma' in response.headers)

        for qs in [
            {'bgcolor': 'foo'},
        ]:
            qs['target'] = 'test'
            with self.assertRaises(ValueError):
                response = self.app.get(self.url, query_string=qs)

        for qs in [
            {'lineMode': 'stacked'},
        ]:
            qs['target'] = 'test'
            with self.assertRaises(AssertionError):
                response = self.app.get(self.url, query_string=qs)

    def test_render_validation_png(self):
        whisper.create(self.db, [(1, 60)])

        response = self.app.get(self.url, query_string={
            'target': 'foo',
            'width': 100,
            'thickness': '1.5',
            'fontBold': 'true',
            'fontItalic': 'default',
        })
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.url, query_string={
            'target': ['test', 'foo:1.2'], 'graphType': 'pie'})
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.url, query_string={'target': ['test',
                                                                   '']})
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.url, query_string={
            'target': 'sum(test)',
        })
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.url, query_string={
            'target': ['sinFunction("a test", 2)',
                       'sinFunction("other test", 2.1)',
                       'sinFunction("other test", 2e1)'],
        })
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.url, query_string={
            'target': ['percentileOfSeries(sin("foo bar"), 95, true)']
        })
        self.assertEqual(response.status_code, 200)

    def test_render_validation_svg(self):
        whisper.create(self.db, [(1, 60)])

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'svg',
                                                        'jsonp': 'foo'})
        jsonpsvg = response.data.decode('utf-8')
        self.assertTrue(jsonpsvg.startswith('foo("<?xml version=\\"1.0\\"'))
        self.assertTrue(jsonpsvg.endswith('</script>\\n</svg>")'))

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'svg'})
        svg = response.data.decode('utf-8')
        self.assertTrue(svg.startswith('<?xml version="1.0"'))

        response = self.app.get(self.url, query_string={'target': 'inexisting',
                                                        'format': 'svg'})
        self.assertEqual(response.status_code, 200)
        svg = response.data.decode('utf-8')
        self.assertTrue(svg.startswith('<?xml version="1.0"'))

    def test_bootstrap_fetch_outside_range(self):
        self.create_db()
        response = self.app.get(
            self.url, query_string={
                'target': "aliasByNode(movingMedian(test, '15min'), 0)",
            },
        )
        self.assertEqual(response.status_code, 200)
