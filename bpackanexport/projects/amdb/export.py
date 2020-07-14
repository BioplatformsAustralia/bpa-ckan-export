from __future__ import print_function
from ...util import make_logger, safe_path
from collections import defaultdict
logger = make_logger(__name__)


class AMDBExport(object):
    def __init__(self):
        pass

    def get_resources(self, ckan):
        "returns a mapping (url, (d1, d2, d3, ...), filename)"
        organization = ckan.action.organization_show(
            id='australian-microbiome', include_datasets=True)
        dataset_ids = [t['id'] for t in organization['packages']]
        resources = []
        md5sums = defaultdict(list)
        for dataset_id in dataset_ids[:10]:
            dataset = ckan.action.package_show(
                id=dataset_id, include_resources=True)
            if 'amplicon' in dataset:
                target_path = safe_path(
                    ['amplicon', dataset['data_type'], dataset['type'], dataset['ticket'], dataset['title']])
            else:
                target_path = safe_path(
                    ['shotgun', dataset['data_type'], dataset['type'], dataset['ticket'], dataset['title']])

            for resource in dataset['resources']:
                info = (resource['url'], target_path,
                        resource['name'], resource.get('sha256'))
                resources.append(info)
                md5sums[target_path].append(
                    (resource['md5'], resource['name']))
        return resources, md5sums
