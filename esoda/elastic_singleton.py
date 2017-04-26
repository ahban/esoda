from elasticsearch import Elasticsearch


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance


class EsAdaptor(object):
    __metaclass__ = Singleton

    def __init__(self, host='localhost', index='test', doctype='sentences'):
        self.es = Elasticsearch(host)
        self.index = index
        self.doctype = doctype

    def build(self):
        if not self.es.indices.exists(index=self.index):
            self.es.indices.create(index=self.index)
            mappings = {
                self.doctype: {
                    "properties": {
                        "p": {"type": "integer"},
                        "c": {"type": "text", "index": "not_analyzed"},
                        "t": {
                            "type": "nested",
                            "properties": {
                                "t": {"type": "text", "index": "not_analyzed"},
                                "l": {"type": "text", "fielddata": True, "index": "not_analyzed"}
                            }
                        },
                        "d": {
                            "type": "nested",
                            "properties": {
                                "dt": {"type": "text", "fielddata": True, "index": "not_analyzed"},
                                "l1": {"type": "text", "fielddata": True, "index": "not_analyzed"},
                                "l2": {"type": "text", "fielddata": True, "index": "not_analyzed"},
                                "i1": {"type": "text", "index": "not_analyzed"},
                                "i2": {"type": "text", "index": "not_analyzed"}
                            }
                        }
                    }
                }
            }
            self.es.indices.put_mapping(index=self.index, doc_type=self.doctype, body=mappings)

    def search(self, t, d, ref, sp=0):
        action = {
            "_source": ["p", "c"],
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": []
                        }
                    },
                    "script_score": {
                        "script": {
                            "lang": "painless",
                            "file": "calculate-cost",
                            "params": {
                                "tList": t,
                                "dList": d,
                                "rList": ref
                            }
                        }
                    }
                }
            },
            "script_fields": {
                "sentence": {
                    "script": {
                        "lang": "painless",
                        "file": "highlight-sentence",
                        "params": {
                            "tList": t,
                            "dList": d,
                            "rList": ref
                        }
                    }
                }
            }
        }
        if sp:
            action['size'] = sp

        for tt in t:
            tq = {
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {}
                    }
                }
            }
            tq['nested']['query']['match'] = {'t.l': tt}
            action['query']['function_score']['query']['bool']['must'].append(tq)

        for dd in d:
            dq = {
                "nested": {
                    "path": "d",
                    "query": {
                        "bool": {
                            "must": []
                        }
                    }
                }
            }
            if 'dt' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.dt': dd['dt']}})
            if 'i1' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.l1': t[dd['i1']]}})
            if 'i2' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.l2': t[dd['i2']]}})
            action['query']['function_score']['query']['bool']['must'].append(dq)
        res = self.es.search(index=self.index, doc_type=self.doctype, body=action, filter_path=[
            'hits.total', 'hits.hits._id', 'hits.hits._source', 'hits.hits.fields'])
        return res['hits']

    def collocation(self, t, sp=0):
        if not t or len(t) > 2:
            return {}
        action = {
            "_source": False,
            "query": {
            },
            "aggs": {
                "d": {
                    "nested": {
                        "path": "d"
                    },
                    "aggs": {
                        "d": {
                            "aggs": {
                                "d": {
                                    "terms": {
                                        "field": "d.dt"
                                    }
                                }
                            },
                            "filter": {
                            }
                        }
                    }
                }
            }
        }

        if len(t) > 1:
            ddq = [{'match': {'d.l1': t[0]}}, {'match': {'d.l2': t[1]}}]
            dq = {
                "nested": {
                    "path": "d",
                    "query": {
                        "bool": {
                            "must": ddq
                        }
                    }
                }
            }
            action['query'] = dq
            df = {
                'bool': {
                    'must': ddq
                }
            }
            action['aggs']['d']['aggs']['d']['filter'] = df
            ret = self.__checkResult(action)
        else:
            ret = []
            for ps in ['d.l1', 'd.l2']:
                ddq = {'match': {ps: t[0]}}
                dq = {
                    "nested": {
                        "path": "d",
                        "query": ddq
                    }
                }
                action['query'] = dq
                action['aggs']['d']['aggs']['d']['filter'] = ddq
                ret += self.__checkResult(action)

        return ret

    def __checkResult(self, action):
        res = self.es.search(index=self.index, doc_type=self.doctype, body=action, filter_path=[
            'hits.total', 'aggregations'])
        ret = [False] * 4
        for agg in res['aggregations']['d']['d']['d']['buckets']:
            ret[ord(agg['key']) - 49] = True
            # ord('0') = 48
        return ret

    def group(self, t, d, sp=0):
        if not d or len(d) > 1:
            return {}
        action = {
            "_source": False,
            "query": {
                "bool": {
                    "must": []
                }
            },
            "aggs": {
                "d": {
                    "nested": {
                        "path": "d"
                    },
                    "aggs": {
                        "d": {
                            "aggs": {
                                "d": {
                                    "terms": {
                                        "size": sp if sp else 10
                                    }
                                }
                            },
                            "filter": {
                                "bool": {
                                    "must": []
                                }
                            }
                        }
                    }
                }
            }
        }

        for i, tt in enumerate(t):
            tq = {
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {}
                    },
                }
            }
            tq['nested']['query']['match'] = {'t.l': tt}
            action['query']['bool']['must'].append(tq)

        dq = [{
            "nested": {
                "path": "d",
                "query": {
                    "bool": {
                        "must": []
                    }
                }
            }
        }]
        dd = d[0]
        ddq = []
        if 'dt' in dd:
            ddq.append({'match': {'d.dt': str(dd['dt'])}})
        if 'l1' in dd:
            ddq.append({'match': {'d.l1': dd['l1']}})
        if 'l2' in dd:
            ddq.append({'match': {'d.l2': dd['l2']}})
        dq[0]['nested']['query']['bool']['must'] += ddq

        action['query']['bool']['must'] += dq
        action['aggs']['d']['aggs']['d']['filter']['bool']['must'] += ddq

        cnt = 0
        st = ''
        if 'dt' not in dd:
            st = 'd.dt'
            cnt += 1
        if 'l1' not in dd:
            st = 'd.l1'
            cnt += 1
        if 'l2' not in dd:
            st = 'd.l2'
            cnt += 1
        if cnt != 1:
            return {}

        action['aggs']['d']['aggs']['d']['aggs']['d']['terms']['field'] = st

        res = self.es.search(index=self.index, doc_type=self.doctype, body=action, filter_path=[
            'hits.total', 'aggregations'])
        return res
