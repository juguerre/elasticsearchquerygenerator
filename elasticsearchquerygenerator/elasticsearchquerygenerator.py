from typing import List


class Operation(object):
    SHOULD = "should"
    MUST = "must"
    FILTER = "filter"


class AggType(object):
    TERMS = "terms"


class Sort(object):
    ASC = "asc"
    DESC = "des"


class ElasticSearchQuery(object):
    def __init__(
        self,
        size: int = 10,
        bucket_name: str = None,
        source: List[str] = None,
        min_score: float = 0.5,
    ):
        """

        :param size:
        :param bucket_name:
        :param source:
        :param min_score:
        """

        self.size = size
        self.bucket_name = bucket_name
        self.min_score = min_score
        self.source = source if source else []
        self.base_query = {
            "_source": source,
            "size": self.size,
            "min_score": self.min_score,
            "query": {"bool": {"must": [], "filter": [], "should": [], "must_not": []}},
        }
        self.geo_base_query = {
            "_source": self.source,
            "size": self.size,
            "query": {"bool": {"must": {"match_all": {}}, "should": [], "filter": {}}},
        }
        self.aggtem = []
        self.base_higghlight = {
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"],
            "tags_schema": "styled",
            "fields": {},
        }

    def match(
        self,
        field: str = None,
        value: str = None,
        boost: float = None,
        operation: str = "should",
        analyzer: str = None,
    ):

        fragment = {"match": {field: {"query": value}}}
        if boost is None:
            self.base_query["query"]["bool"][operation].append(fragment)
        else:
            fragment["match"][field]["boost"] = boost

        if analyzer:
            fragment["match"][field]["analyzer"] = analyzer

        self.base_query["query"]["bool"][operation].append(fragment)

        return self.base_query

    def match_phrase(
        self,
        field: str = None,
        value: str = None,
        boost: float = None,
        operation: str = "should",
        analyzer: str = None,
    ):
        fragment = {"match_phrase": {field: {"query": value}}}
        if boost:
            self.base_query["query"]["bool"][operation].append(fragment)
        else:
            fragment["match_phrase"][field]["boost"] = boost

        if analyzer:
            fragment["match_phrase"][field]["analyzer"] = analyzer

        self.base_query["query"]["bool"][operation].append(fragment)

        return self.base_query

    def terms(
        self,
        field: str = None,
        value: str = None,
        boost: float = None,
        operation: str = "should",
    ):
        fragment = {"term": {field: value}}
        self.base_query["query"]["bool"][operation].append(fragment)
        return self.base_query

    def add_aggregation(
        self,
        aggregate_name: str = None,
        field: str = None,
        agg_type: str = "terms",
        sort: str = "desc",
        size: int = 10,
    ):
        fragment = {
            aggregate_name: {
                agg_type: {"field": field, "order": {"_count": sort}, "size": size}
            }
        }
        self.aggtem.append(fragment)

    def complete_aggregation(self):
        fragment = {"aggs": {}}
        for item in self.aggtem:
            for key, value in item.items():
                fragment["aggs"][key] = value
        self.base_query["aggs"] = fragment["aggs"]
        return self.base_query

    def add_geoqueries(
        self,
        radius: str = None,
        lat: str = None,
        lon: str = None,
        field: str = None,
        operation: str = Operation.FILTER,
    ):
        radius = str(radius) + "mi"
        _ = {"geo_distance": {"distance": radius, field: {"lat": lat, "lon": lon}}}
        self.base_query["query"]["bool"][operation].append(_)
        return self.base_query

    def wildcard(
        self, field: str = None, value=None, boost=None, operation: str = None
    ):
        fragment = {"wildcard": {field: {"value": value}}}
        if boost is None:
            self.base_query["query"]["bool"][operation].append(fragment)
            return self.base_query
        else:
            fragment["wildcard"][field]["boost"] = boost
            self.base_query["query"]["bool"][operation].append(fragment)
            return self.base_query

    def exists(self, field: str = None, operation: str = Operation.MUST):
        fragment = {"exists": {"field": field}}
        self.base_query["query"]["bool"][operation].append(fragment)
        return self.base_query

    def query_string(
        self,
        default_field: str = None,
        query: str = None,
        operation: str = Operation.SHOULD,
    ):
        fragment = {
            "query_string": {
                "default_field": default_field,
                "query": f"{query}",
            }
        }
        self.base_query["query"]["bool"][operation].append(fragment)
        return self.base_query

    def add_geo_aggreation(
        self,
        field: str = None,
        lat: str = None,
        lon: str = None,
        aggregate_name: str = "distance",
    ):
        self.base_query.get("aggs")[aggregate_name] = {
            "geo_distance": {
                "field": field,
                "origin": "{},{}".format(lat, lon),
                "unit": "mi",
                "ranges": [
                    {"to": 0},
                    {"from": 0, "to": 25},
                    {"from": 25, "to": 50},
                    {"from": 50, "to": 75},
                    {"from": 75, "to": 100},
                    {"from": 100},
                ],
            }
        }
        return self.base_query

    def match_phrase_prefix(
        self,
        field: str = None,
        value: str = None,
        boost: float = None,
        operation: str = Operation.SHOULD,
        analyzer: str = None,
    ):
        fragment = {"match_phrase_prefix": {field: {"query": value}}}

        if boost is not None:
            fragment["match_phrase_prefix"][field]["boost"] = boost
        if analyzer is not None:
            fragment["match_phrase_prefix"][field]["analyzer"] = analyzer
        self.base_query["query"]["bool"][operation].append(fragment)
        return self.base_query

    def autocomplete_1(
        self,
        field: str = None,
        size: int = 25,
        value: str = None,
        sort: str = Sort.DESC,
        operation: str = Operation.MUST,
    ):
        self.match_phrase_prefix(field=field, value=value, operation=operation)
        self.add_aggregation(
            field=field, size=size, sort=sort, aggregate_name="auto_complete"
        )
        query = self.complete_aggregation()
        return query
