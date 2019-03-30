# -*- coding: utf-8 -*-
# Copyright 2014 Google Inc. All rights reserved.
#
# Modifications Copyright (C) 2018 HeiGIT, University of Heidelberg.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
"""Tests for the Valhalla module."""

from routingpy import Valhalla
from tests.test_helper import *
import tests as _test

import json
import responses
from copy import deepcopy


class ValhallaTest(_test.TestCase):

    name = 'valhalla'

    def setUp(self):
        self.client = Valhalla('https://api.mapbox.com/valhalla/v1')

    @responses.activate
    def test_full_directions(self):
        query = ENDPOINTS_QUERIES[self.name]['directions']
        expected = ENDPOINTS_EXPECTED[self.name]['directions']

        responses.add(
            responses.POST,
            'https://api.mapbox.com/valhalla/v1/route',
            status=200,
            json=expected,
            content_type='application/json')
        routes = self.client.directions(**query)

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(json.loads(responses.calls[0].request.body), expected)

    @responses.activate
    def test_waypoint_generator(self):
        query = deepcopy(ENDPOINTS_QUERIES[self.name]['directions'])
        expected = deepcopy(ENDPOINTS_EXPECTED[self.name]['directions'])

        extra_params = {
            'type': 'break',
            'heading': PARAM_INT_SMALL,
            'heading_tolerance': PARAM_INT_SMALL,
            'minimum_reachability': PARAM_INT_SMALL,
            'radius': PARAM_INT_SMALL,
            'rank_candidates': True
        }

        query['coordinates'].append(
            Valhalla.Waypoint(PARAM_POINT, **extra_params))
        expected['locations'].append({
            'lat': PARAM_POINT[1],
            'lon': PARAM_POINT[0],
            **extra_params
        })

        responses.add(
            responses.POST,
            'https://api.mapbox.com/valhalla/v1/route',
            status=200,
            json=expected,
            content_type='application/json')
        routes = self.client.directions(**query)

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(json.loads(responses.calls[0].request.body), expected)

    @responses.activate
    def test_full_isochrones(self):
        query = ENDPOINTS_QUERIES[self.name]['isochrones']
        expected = ENDPOINTS_EXPECTED[self.name]['isochrones']

        responses.add(
            responses.POST,
            'https://api.mapbox.com/valhalla/v1/isochrone',
            status=200,
            json=expected,
            content_type='application/json')

        routes = self.client.isochrones(**query)

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(json.loads(responses.calls[0].request.body), expected)

    # TODO: test colors having less items than range
    @responses.activate
    def test_full_matrix(self):
        query = ENDPOINTS_QUERIES[self.name]['matrix']
        expected = ENDPOINTS_EXPECTED[self.name]['matrix']

        responses.add(
            responses.POST,
            'https://api.mapbox.com/valhalla/v1/sources_to_targets',
            status=200,
            json=expected,
            content_type='application/json')

        routes = self.client.distance_matrix(**query)

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(json.loads(responses.calls[0].request.body), expected)

    @responses.activate
    def test_few_sources_destinations_matrix(self):
        query = deepcopy(ENDPOINTS_QUERIES[self.name]['matrix'])
        query['sources'] = [2]
        query['destinations'] = [0]

        expected = deepcopy(ENDPOINTS_EXPECTED[self.name]['matrix'])
        del expected['sources'][0]
        del expected['sources'][0]
        del expected['targets'][1]
        del expected['targets'][1]

        responses.add(
            responses.POST,
            'https://api.mapbox.com/valhalla/v1/sources_to_targets',
            status=200,
            json=expected,
            content_type='application/json')

        routes = self.client.distance_matrix(**query)

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(json.loads(responses.calls[0].request.body), expected)
