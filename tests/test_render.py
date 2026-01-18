# coding: utf-8
"""Tests that don't require Cairo (JSON/raw/csv/dygraph/rickshaw formats)."""
import json
import os
import time

from graphite_render._vendor import whisper

from . import TestCase, WHISPER_DIR


class RenderTest(TestCase):
    """Tests that don't require Cairo - use JSON/raw/csv/dygraph/rickshaw formats."""
    db = os.path.join(WHISPER_DIR, 'test.wsp')
    url = '/render'

    def create_db(self):
        whisper.create(self.db, [(1, 60)])

        self.ts = int(time.time())
        whisper.update(self.db, 1.0, self.ts - 2)
        whisper.update(self.db, 0.5, self.ts - 1)
        whisper.update(self.db, 1.5, self.ts)

    def test_render_view_json(self):
        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'json',
                                                        'noCache': 'true'})
        self.assertEqual(json.loads(response.data.decode('utf-8')), [])

    def test_render_view_raw(self):
        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'raw',
                                                        'noCache': 'true'})
        self.assertEqual(response.data.decode('utf-8'), "")
        self.assertEqual(response.headers['Content-Type'], 'text/plain')

    def test_render_view_dygraph(self):
        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'dygraph',
                                                        'noCache': 'true'})
        self.assertEqual(json.loads(response.data.decode('utf-8')), {})

    def test_render_view_rickshaw(self):
        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'rickshaw',
                                                        'noCache': 'true'})
        self.assertEqual(json.loads(response.data.decode('utf-8')), [])

    def test_render_view_with_data(self):
        self.create_db()
        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'json'})
        data = json.loads(response.data.decode('utf-8'))
        end = data[0]['datapoints'][-4:]
        try:
            self.assertEqual(
                end, [[None, self.ts - 3], [1.0, self.ts - 2],
                      [0.5, self.ts - 1], [1.5, self.ts]])
        except AssertionError:
            self.assertEqual(
                end, [[1.0, self.ts - 2], [0.5, self.ts - 1],
                      [1.5, self.ts], [None, self.ts + 1]])

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'maxDataPoints': 2,
                                                        'format': 'json'})
        data = json.loads(response.data.decode('utf-8'))
        # 1 is a time race cond
        self.assertTrue(len(data[0]['datapoints']) in [1, 2])

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'maxDataPoints': 200,
                                                        'format': 'json'})
        data = json.loads(response.data.decode('utf-8'))
        # 59 is a time race cond
        self.assertTrue(len(data[0]['datapoints']) in [59, 60])

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'noNullPoints': 1,
                                                        'format': 'json'})
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data[0]['datapoints'],
                         [[1.0, self.ts - 2],
                          [0.5, self.ts - 1],
                          [1.5, self.ts]])

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'raw'})
        try:
            self.assertEqual(
                response.data.decode('utf-8'),
                'test,%d,%d,1|%s' % (self.ts - 59, self.ts + 1,
                                     'None,' * 57 + '1.0,0.5,1.5\n'))
        except AssertionError:
            self.assertEqual(
                response.data.decode('utf-8'),
                'test,%d,%d,1|%s' % (self.ts - 58, self.ts + 2,
                                     'None,' * 56 + '1.0,0.5,1.5,None\n'))

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'dygraph'})
        data = json.loads(response.data.decode('utf-8'))
        end = data['data'][-4:]
        try:
            self.assertEqual(
                end, [[(self.ts - 3) * 1000, None],
                      [(self.ts - 2) * 1000, 1.0],
                      [(self.ts - 1) * 1000, 0.5],
                      [self.ts * 1000, 1.5]])
        except AssertionError:
            self.assertEqual(
                end, [[(self.ts - 2) * 1000, 1.0],
                      [(self.ts - 1) * 1000, 0.5],
                      [self.ts * 1000, 1.5],
                      [(self.ts + 1) * 1000, None]])

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'rickshaw'})
        data = json.loads(response.data.decode('utf-8'))
        end = data[0]['datapoints'][-4:]
        try:
            self.assertEqual(
                end, [{'x': self.ts - 3, 'y': None},
                      {'x': self.ts - 2, 'y': 1.0},
                      {'x': self.ts - 1, 'y': 0.5},
                      {'x': self.ts, 'y': 1.5}])
        except AssertionError:
            self.assertEqual(
                end, [{'x': self.ts - 2, 'y': 1.0},
                      {'x': self.ts - 1, 'y': 0.5},
                      {'x': self.ts, 'y': 1.5},
                      {'x': self.ts + 1, 'y': None}])

    def test_render_constant_line_json(self):
        response = self.app.get(self.url, query_string={
            'target': 'constantLine(12)', 'format': 'json'})
        data = json.loads(response.data.decode('utf-8'))[0]['datapoints']
        self.assertEqual(len(data), 3)
        for point, _ts in data:
            self.assertEqual(point, 12)

        response = self.app.get(self.url, query_string={
            'target': 'constantLine(12)', 'format': 'json',
            'maxDataPoints': 12})
        data = json.loads(response.data.decode('utf-8'))[0]['datapoints']
        self.assertEqual(len(data), 3)
        for point, _ts in data:
            self.assertEqual(point, 12)

    def test_float_maxdatapoints(self):
        response = self.app.get(self.url, query_string={
            'target': 'sin("foo")', 'format': 'json',
            'maxDataPoints': 5.5})  # rounded to int
        data = json.loads(response.data.decode('utf-8'))[0]['datapoints']
        self.assertEqual(len(data), 5)

    def test_constantline_pathexpr(self):
        response = self.app.get(self.url, query_string={
            'target': 'sumSeries(constantLine(12), constantLine(5))',
            'format': 'json',
        })
        data = json.loads(response.data.decode('utf-8'))[0]['datapoints']
        self.assertEqual([d[0] for d in data], [17, 17, 17])

    def test_area_between(self):
        response = self.app.get(self.url, query_string={
            'target': ['areaBetween(sin("foo"), sin("bar", 2))'],
            'format': 'json',
        })
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 2)

    def test_sumseries(self):
        response = self.app.get(self.url, query_string={
            'target': ['sumSeries(sin("foo"), sin("bar", 2))',
                       'sin("baz", 3)'],
            'format': 'json',
        })
        data = json.loads(response.data.decode('utf-8'))
        agg = {}
        for series in data:
            agg[series['target']] = series['datapoints']
        for index, value in enumerate(agg['baz']):
            self.assertEqual(value, agg['sumSeries(sin(bar),sin(foo))'][index])

        response = self.app.get(self.url, query_string={
            'target': ['sumSeries(sin("foo"), sin("bar", 2))',
                       'sin("baz", 3)'],
            'format': 'json',
            'maxDataPoints': 100,
        })
        data = json.loads(response.data.decode('utf-8'))
        agg = {}
        for series in data:
            self.assertTrue(len(series['datapoints']) <= 100)
            agg[series['target']] = series['datapoints']
        for index, value in enumerate(agg['baz']):
            self.assertEqual(value, agg['sumSeries(sin(bar),sin(foo))'][index])

    def test_correct_timezone(self):
        response = self.app.get(self.url, query_string={
            'target': 'constantLine(12)',
            'format': 'json',
            'from': '07:00_20140226',
            'until': '08:00_20140226',
            # tz is UTC
        })
        data = json.loads(response.data.decode('utf-8'))[0]['datapoints']

        # all the from/until/tz combinations lead to the same window
        expected = [[12, 1393398000], [12, 1393399800], [12, 1393401600]]
        self.assertEqual(data, expected)

        response = self.app.get(self.url, query_string={
            'target': 'constantLine(12)',
            'format': 'json',
            'from': '08:00_20140226',
            'until': '09:00_20140226',
            'tz': 'Europe/Berlin',
        })
        data = json.loads(response.data.decode('utf-8'))[0]['datapoints']
        self.assertEqual(data, expected)

    def test_render_validation(self):
        whisper.create(self.db, [(1, 60)])

        response = self.app.get(self.url)
        self.assertJSON(response, {'errors': {
            'target': 'This parameter is required.'}}, status_code=400)

        response = self.app.get(self.url, query_string={'graphType': 'foo',
                                                        'target': 'test'})
        self.assertJSON(response, {'errors': {
            'graphType': "Invalid graphType 'foo', must be one of 'line', "
            "'pie'."}}, status_code=400)

        response = self.app.get(self.url, query_string={'maxDataPoints': 'foo',
                                                        'target': 'test'})
        self.assertJSON(response, {'errors': {
            'maxDataPoints': 'Must be an integer.'}}, status_code=400)

        response = self.app.get(self.url, query_string={
            'from': '21:2020140313',
            'until': '21:2020140313',
            'target': 'test'})
        self.assertJSON(response, {'errors': {
            'from': 'Invalid empty time range',
            'until': 'Invalid empty time range',
        }}, status_code=400)

        response = self.app.get(self.url, query_string={
            'target': 'foo', 'tz': 'Europe/Lausanne'})
        self.assertJSON(response, {'errors': {
            'tz': "Unknown timezone: 'Europe/Lausanne'.",
        }}, status_code=400)

        response = self.app.get(self.url, query_string={'target': 'test:aa',
                                                        'graphType': 'pie'})
        self.assertJSON(response, {'errors': {
            'target': "Invalid target: 'test:aa'.",
        }}, status_code=400)

    def test_render_validation_csv(self):
        whisper.create(self.db, [(1, 60)])

        response = self.app.get(self.url, query_string={'target': 'test',
                                                        'format': 'csv'})
        lines = response.data.decode('utf-8').strip().split('\n')
        # 59 is a time race cond
        self.assertTrue(len(lines) in [59, 60])
        self.assertFalse(any([l.strip().split(',')[2] for l in lines]))

    def test_raw_data(self):
        whisper.create(self.db, [(1, 60)])

        response = self.app.get(self.url, query_string={'rawData': '1',
                                                        'target': 'test'})
        info, data = response.data.decode('utf-8').strip().split('|', 1)
        path, start, stop, step = info.split(',')
        datapoints = data.split(',')
        try:
            self.assertEqual(datapoints, ['None'] * 60)
            self.assertEqual(int(stop) - int(start), 60)
        except AssertionError:
            self.assertEqual(datapoints, ['None'] * 59)
            self.assertEqual(int(stop) - int(start), 59)
        self.assertEqual(path, 'test')
        self.assertEqual(int(step), 1)

    def test_jsonp(self):
        whisper.create(self.db, [(1, 60)])

        start = int(time.time()) - 59
        response = self.app.get(self.url, query_string={'format': 'json',
                                                        'jsonp': 'foo',
                                                        'target': 'test'})
        data = response.data.decode('utf-8')
        self.assertTrue(data.startswith('foo('))
        data = json.loads(data[4:-1])
        try:
            self.assertEqual(data, [{'datapoints': [
                [None, start + i] for i in range(60)
            ], 'target': 'test'}])
        except AssertionError:  # Race condition when time overlaps a second
            self.assertEqual(data, [{'datapoints': [
                [None, start + i + 1] for i in range(60)
            ], 'target': 'test'}])

    def test_sorted(self):
        for db in (
            ('test', 'foo.wsp'),
            ('test', 'welp.wsp'),
            ('test', 'baz.wsp'),
        ):
            db_path = os.path.join(WHISPER_DIR, *db)
            if not os.path.exists(os.path.dirname(db_path)):
                os.makedirs(os.path.dirname(db_path))
            whisper.create(db_path, [(1, 60)])

        response = self.app.get(self.url, query_string={'rawData': '1',
                                                        'target': 'test.*'})
        dses = response.data.decode('utf-8').strip().split("\n")

        paths = []
        for ds in dses:
            info, data = ds.strip().split('|', 1)
            path, start, stop, step = info.split(',')
            paths.append(path)

        self.assertEqual(paths, ['test.baz', 'test.foo', 'test.welp'])

    def test_templates(self):
        ts = int(time.time())
        value = 1
        for db in (
            ('hosts', 'worker1', 'cpu.wsp'),
            ('hosts', 'worker2', 'cpu.wsp'),
        ):
            db_path = os.path.join(WHISPER_DIR, *db)
            if not os.path.exists(os.path.dirname(db_path)):
                os.makedirs(os.path.dirname(db_path))
            whisper.create(db_path, [(1, 60)])
            whisper.update(db_path, value, ts)
            value += 1

        for query, expected in [
            ({'target': 'template(hosts.worker1.cpu)'}, 'hosts.worker1.cpu'),
            ({'target': 'template(constantLine($1),12)'}, '12'),
            ({'target': 'template(constantLine($1))',
              'template[1]': '12'}, '12.0'),
            ({'target': 'template(constantLine($num),num=12)'}, '12'),
            ({'target': 'template(constantLine($num))',
              'template[num]': '12'}, '12.0'),
            ({'target': 'template(time($1),"nameOfSeries")'}, 'nameOfSeries'),
            ({'target': 'template(time($1))',
              'template[1]': 'nameOfSeries'}, 'nameOfSeries'),
            ({'target': 'template(time($name),name="nameOfSeries")'},
             'nameOfSeries'),
            ({'target': 'template(time($name))',
              'template[name]': 'nameOfSeries'}, 'nameOfSeries'),
            ({'target': 'template(sumSeries(hosts.$1.cpu),"worker1")'},
             'sumSeries(hosts.worker1.cpu)'),
            ({'target': 'template(sumSeries(hosts.$1.cpu))',
              'template[1]': 'worker*'}, 'sumSeries(hosts.worker*.cpu)'),
            ({'target': 'template(sumSeries(hosts.$host.cpu))',
              'template[host]': 'worker*'}, 'sumSeries(hosts.worker*.cpu)'),
        ]:
            query['format'] = 'json'
            response = self.app.get(self.url, query_string=query)
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data[0]['target'], expected)
