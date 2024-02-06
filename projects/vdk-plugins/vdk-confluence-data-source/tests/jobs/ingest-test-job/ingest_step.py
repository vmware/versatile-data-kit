import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    source = SourceDefinition(id="test-data-source",
                              name="confluence-data-source",
                              config=job_input.get_arguments("config", {}))
    destination = DestinationDefinition(id="test-destination", method="memory")

    with DataFlowInput(job_input) as flow_input:
        flow_input.start(DataFlowMappingDefinition(source, destination))
