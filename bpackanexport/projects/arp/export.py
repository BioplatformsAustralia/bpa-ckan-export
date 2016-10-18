from __future__ import print_function
from ...util import make_logger, safe_path

logger = make_logger(__name__)


class ARPExport(object):
    def __init__(self):
        pass

    def get_resources(self, ckan):
        "returns a mapping (url, (d1, d2, d3, ...), filename)"
        organization = ckan.action.organization_show(id='bpa-sepsis', include_datasets=True)
        resources = []
        for dataset_id in [t['id'] for t in organization['packages']]:
            dataset = ckan.action.package_show(id=dataset_id, include_resources=True)
            target_path = safe_path([dataset['taxon_or_organism'], dataset['strain_or_isolate'], dataset['omics'], dataset['type'].split('-')[-1], 'raw'])
            for resource in dataset['resources']:
                info = (resource['url'], target_path, resource['name'], resource.get('sha256'))
                resources.append(info)
        return resources
