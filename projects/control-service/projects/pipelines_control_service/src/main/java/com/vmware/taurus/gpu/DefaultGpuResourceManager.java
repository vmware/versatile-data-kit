/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.gpu;

import com.google.ortools.linearsolver.MPConstraint;
import com.google.ortools.linearsolver.MPObjective;
import com.google.ortools.linearsolver.MPSolver;
import com.google.ortools.linearsolver.MPVariable;
import com.vmware.taurus.gpu.jpa.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;


@Component
@RequiredArgsConstructor
public class DefaultGpuResourceManager implements GpuResourceManager{

    private final GpuResourcesPerTeamRepo gpuResourcesPerTeamRepo;
    private final GpuConsumingJobRepo gpuConsumingJobRepo;
    private final NodeWithGPURepo nodeWithGPURepo;


    @Override
    public void jobEnded(String jobName, String teamName){
        gpuConsumingJobRepo.deleteByJobNameAndGpuResourcesPerTeam_TeamName(jobName, teamName);
    }


    @Override
    public List<JobAction> tryProvisionResources(String teamName,String jobName,float amount){
        float resourcesTotal = gpuResourcesPerTeamRepo.findById(teamName).get().getResources();

        Float v = gpuConsumingJobRepo.sumConsumedResourcesByTeam(teamName);

        if(v + amount <= resourcesTotal){
            List<NodeWithGPUs> nodesWithAvailableGPUs = nodeWithGPURepo.findNodesWithAvailableGPUs(amount);
            if(!nodesWithAvailableGPUs.isEmpty()) {
                gpuConsumingJobRepo.save(new GpuConsumingJob(gpuResourcesPerTeamRepo.getReferenceById(teamName),
                        jobName, amount, nodesWithAvailableGPUs.get(0)));
                return Arrays.asList(new CreateJob(nodesWithAvailableGPUs.get(0).getName(), jobName));
            }else{
//                // cleanup
//                Map<NodeWithGPUs, List<GpuConsumingJob>> collect = gpuResourcesPerTeamRepo.findTeamsOverusingResources()
//                        .stream().flatMap(a -> a.getGpuConsumingJobs().stream())
//                        .filter(GpuConsumingJob::isLowPriority)
//                        .collect(Collectors.groupingBy(GpuConsumingJob::getNodeWithGPUs))
//                        .entrySet().stream()
//                        .filter(a -> checkIfNodeHasClearableSpace(a, resourcesTotal));
//
//                );
            }
        }
        throw new UnsupportedOperationException();
//        gpuConsumingJobRepo.sumConsumedResourcesByTeam(teamName);
    }

    private boolean checkIfNodeHasClearableSpace(Map.Entry<NodeWithGPUs, List<GpuConsumingJob>> a, float resourcesTotal) {
        Map<GpuResourcesPerTeam, List<GpuConsumingJob>> resourcesForSingleTeamOnSingleNode = a.getValue().stream()
                .collect(Collectors.groupingBy(GpuConsumingJob::getGpuResourcesPerTeam));

        MPSolver solver = new MPSolver(
                "SubsetSumClosest",
                MPSolver.OptimizationProblemType.CBC_MIXED_INTEGER_PROGRAMMING);
        List<MPVariable> allVars = new ArrayList<>();
        ArrayList<Float> allNums = new ArrayList<>();
        for (Map.Entry<GpuResourcesPerTeam, List<GpuConsumingJob>> gpuResourcesPerTeamListEntry : resourcesForSingleTeamOnSingleNode.entrySet()) {
            float overProvisionedBy = gpuResourcesPerTeamListEntry.getValue().stream()
                    .map(GpuConsumingJob::getConsumedResources).reduce(Float::sum).get() - gpuResourcesPerTeamListEntry.getKey().getResources();

            List<Float> nums = gpuResourcesPerTeamListEntry.getValue().stream().map(GpuConsumingJob::getConsumedResources).toList();
            List<MPVariable> vars = new ArrayList<>();
            for (int i = 0; i < nums.size(); i++) {
                vars.add(solver.makeIntVar(0, 1, gpuResourcesPerTeamListEntry.getKey().getTeamName() + i));
            }

            MPConstraint constraint = solver.makeConstraint(0, Math.min(resourcesTotal, overProvisionedBy));
            for (int i = 0; i < nums.size(); i++) {
                constraint.setCoefficient(vars.get(i), nums.get(i));
            }

            allNums.addAll(nums);
            allVars.addAll(vars);

        }

        MPConstraint constraint = solver.makeConstraint(0, resourcesTotal);
        for (int i = 0; i < allVars.size(); i++) {
            constraint.setCoefficient(allVars.get(i), allNums.get(i));
        }

        MPObjective objective = solver.objective();
        for (int i = 0; i < allVars.size(); i++) {
            objective.setCoefficient(allVars.get(i), allNums.get(i));
        }
        objective.setMaximization();

        // Solve the model
        final MPSolver.ResultStatus resultStatus = solver.solve();

        if (resultStatus == MPSolver.ResultStatus.OPTIMAL || resultStatus == MPSolver.ResultStatus.FEASIBLE) {
            System.out.println("Solution found!");
            double total = 0;
            for (int i = 0; i < allVars.size(); ++i) {
                if (Math.abs(allVars.get(i).solutionValue()) > 0.5) {
                    System.out.println("Include number: " + allNums.get(i));
                    total += allNums.get(i);
                }
            }

            System.out.println("Total sum: " + total);
            return true;
        } else {
            System.out.println("No solution found.");
            return false;
        }
    }

    public void packNodes(){
        MPSolver solver = new MPSolver(
                "BinPackingReshuffle",
                MPSolver.OptimizationProblemType.SCIP_MIXED_INTEGER_PROGRAMMING
        );

        int numberOfJobs = (int) gpuConsumingJobRepo.count();
        int numOfNodes = (int) nodeWithGPURepo.count();
        List<GpuConsumingJob> allJobs = gpuConsumingJobRepo.findAll();
        Float[] weights = allJobs.stream()
                .map(GpuConsumingJob::getConsumedResources).toList().toArray(new Float[0]);
        List<NodeWithGPUs> all = nodeWithGPURepo.findAll();
        Integer[] binCapacities = all.stream()
                .map(NodeWithGPUs::getDeviceCount).toList().toArray(new Integer[0]);

        boolean[][] initialAllocation = new boolean[numOfNodes][numberOfJobs];
        for (int i = 0; i < allJobs.size(); i++) {
            initialAllocation[all.indexOf(allJobs.get(i).getNodeWithGPUs())][i] = true;
        }

        // Decision variables
        MPVariable[][] x = new MPVariable[numOfNodes][numberOfJobs];
        for (int i = 0; i < numOfNodes; i++) {
            for (int j = 0; j < numberOfJobs; j++) {
                x[i][j] = solver.makeIntVar(0, 1, "x[" + i + "," + j + "]");
            }
        }

        // Constraints
        // Each item must be in exactly one bin
        for (int j = 0; j < numberOfJobs; j++) {
            MPConstraint constraint = solver.makeConstraint(1, 1, "itemInOneBin" + j);
            for (int i = 0; i < numOfNodes; i++) {
                constraint.setCoefficient(x[i][j], 1);
            }
        }

        // Respect bin capacities
        for (int i = 0; i < numOfNodes; i++) {
            MPConstraint constraint = solver.makeConstraint(0, binCapacities[i], "binCapacity" + i);
            for (int j = 0; j < numberOfJobs; j++) {
                constraint.setCoefficient(x[i][j], weights[j]);
            }
        }

        // Objective: Minimize reshuffling and number of bins used
        MPObjective objective = solver.objective();

        for (int i = 0; i < numOfNodes; i++) {
            MPVariable binUsed = solver.makeIntVar(0, 1, "binUsed" + i);
            MPConstraint binUseConstraint = solver.makeConstraint(0, Double.POSITIVE_INFINITY, "binUseConstraint" + i);

            for (int j = 0; j < numberOfJobs; j++) {
                double reshuffleCost = initialAllocation[i][j] ? 0 : 1; // Lower cost if no reshuffling needed
                objective.setCoefficient(x[i][j], reshuffleCost);
                binUseConstraint.setCoefficient(x[i][j], 1);
            }

            binUseConstraint.setCoefficient(binUsed, -numberOfJobs);
            objective.setCoefficient(binUsed, 1); // Cost for using a bin
        }
        objective.setMinimization();

        // Solve the model
        MPSolver.ResultStatus resultStatus = solver.solve();
        if (resultStatus == MPSolver.ResultStatus.OPTIMAL || resultStatus == MPSolver.ResultStatus.FEASIBLE) {
            System.out.println("Solution:");
            for (int i = 0; i < numOfNodes; i++) {
                for (int j = 0; j < numberOfJobs; j++) {
                    if (x[i][j].solutionValue() > 0.5) {
                        System.out.printf("Item %d is packed in bin %d.\n", j, i);
                    }
                }
            }
        } else {
            System.out.println("The problem does not have an optimal solution.");
        }
    }

}
