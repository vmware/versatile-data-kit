package com.vmware.taurus.gpu;

import com.vmware.taurus.gpu.jpa.*;
import lombok.RequiredArgsConstructor;
import org.joda.time.LocalDate;
import org.springframework.stereotype.Component;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import com.google.ortools.Loader;
import com.google.ortools.linearsolver.MPConstraint;
import com.google.ortools.linearsolver.MPObjective;
import com.google.ortools.linearsolver.MPSolver;
import com.google.ortools.linearsolver.MPVariable;


@Component
@RequiredArgsConstructor
public class GpuResourceManager {

    private final GpuResourcesPerTeamRepo gpuResourcesPerTeamRepo;
    private final GpuConsumingJobRepo gpuConsumingJobRepo;
    private final NodeWithGPURepo nodeWithGPURepo;


    public void jobEnded(String jobName, String teamName){
        gpuConsumingJobRepo.deleteByJobNameAndGpTeamName(jobName, teamName);
    }

    public void tryProvisionResources(String teamName,String jobName,float amount){
        float resourcesTotal = gpuResourcesPerTeamRepo.findById(teamName).get().getResources();

        Float v = gpuConsumingJobRepo.sumConsumedResourcesByTeam(teamName);

        if(v + amount <= resourcesTotal){
            Optional<NodeWithGPUs> nodesWithAvailableGPUs = nodeWithGPURepo.findNodesWithAvailableGPUs(amount);
            if(nodesWithAvailableGPUs.isPresent()) {
                gpuConsumingJobRepo.save(new GpuConsumingJob(gpuResourcesPerTeamRepo.getReferenceById(teamName),
                        jobName, amount, nodesWithAvailableGPUs.get()));
            }else{
                // cleanup
                Map<NodeWithGPUs, List<GpuConsumingJob>> collect = gpuResourcesPerTeamRepo.findTeamsOverusingResources().stream().flatMap(a -> a.getGpuConsumingJobs().stream())
                        .filter(GpuConsumingJob::isLowPriority)
                        .collect(Collectors.groupingBy(GpuConsumingJob::getNodeWithGPUs))
                        .entrySet().stream()
                        .filter(a -> a.getValue().stream().map(GpuConsumingJob::getConsumedResources).reduce(Float::sum).orElse(0f)>=amount)
                        .filter(a -> myFunction(a))



                        .collect(Collectors.toMap(Map.Entry::getKey,
                                entry-> entry.getValue() , a.getValue().stream().map(GpuConsumingJob::getConsumedResources).reduce(Float::sum)))
                        .map(a-> new Map.Entry<>(a.getKey(),  );

                a -> a.getGpuConsumingJobs().stream().toList().stream()
                                .sorted()
                                .takeWhile()
                );
            }
        }
        gpuConsumingJobRepo.sumConsumedResourcesByTeam(teamName);
    }
//
//    private boolean myFunction(Map.Entry<NodeWithGPUs, List<GpuConsumingJob>> a) {
//        for (GpuConsumingJob gpuConsumingJob : a.getValue()) {
//            gpuConsumingJob.getGpuResourcesPerTeam().getResources()-
//            gpuConsumingJob.getGpuResourcesPerTeam().getGpuConsumingJobs().stream().map(b -> b.getConsumedResources());
//        }
//    }

    public void packBins(){
        // Create the linear solver with the SCIP backend.
        MPSolver solver = MPSolver.createSolver("SCIP");
        if (solver == null) {
            System.out.println("Could not create solver SCIP");
            return;
        }

        MPVariable[][] x = new MPVariable[data.numItems][data.numBins];
        for (int i = 0; i < data.numItems; ++i) {
            for (int j = 0; j < data.numBins; ++j) {
                x[i][j] = solver.makeIntVar(0, 1, "");
            }
        }
        MPVariable[] y = new MPVariable[data.numBins];
        for (int j = 0; j < data.numBins; ++j) {
            y[j] = solver.makeIntVar(0, 1, "");
        }


        double infinity = java.lang.Double.POSITIVE_INFINITY;
        for (int i = 0; i < data.numItems; ++i) {
            MPConstraint constraint = solver.makeConstraint(1, 1, "");
            for (int j = 0; j < data.numBins; ++j) {
                constraint.setCoefficient(x[i][j], 1);
            }
        }
// The bin capacity contraint for bin j is
//   sum_i w_i x_ij <= C*y_j
// To define this constraint, first subtract the left side from the right to get
//   0 <= C*y_j - sum_i w_i x_ij
//
// Note: Since sum_i w_i x_ij is positive (and y_j is 0 or 1), the right side must
// be less than or equal to C. But it's not necessary to add this constraint
// because it is forced by the other constraints.

        for (int j = 0; j < data.numBins; ++j) {
            MPConstraint constraint = solver.makeConstraint(0, infinity, "");
            constraint.setCoefficient(y[j], data.binCapacity);
            for (int i = 0; i < data.numItems; ++i) {
                constraint.setCoefficient(x[i][j], -data.weights[i]);
            }
        }
    }

}
