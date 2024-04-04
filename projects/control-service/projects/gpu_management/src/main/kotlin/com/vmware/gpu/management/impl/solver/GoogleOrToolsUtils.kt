package com.vmware.gpu.management.impl.solver

import com.google.ortools.linearsolver.MPObjective
import com.google.ortools.linearsolver.MPSolver
import com.google.ortools.linearsolver.MPVariable

data class Coefficient(val mpVar: MPVariable, val coefficient: Float)
data class Constraint(
    val sumOfCoefficients: List<Coefficient>,
    val mustBeMoreThanOrEqual: Float = 0.0f,
    val mustBeLessThanOrEqual: Float = Float.MAX_VALUE
)

operator fun MPVariable.times(a : Float) : Coefficient {
    return Coefficient(this, a)
}

operator fun MPVariable.times(a : Double) : Coefficient {
    return Coefficient(this, a.toFloat())
}

fun MPVariable.isEnabled() : Boolean {
    return this.solutionValue() == 1.0
}
fun MPVariable.isDisabled() : Boolean {
    return this.solutionValue() == 0.0
}


fun List<Coefficient>.mustBeLessThanOrEqual(a: Float): Constraint {
    return Constraint(this, mustBeLessThanOrEqual = a)
}
fun List<Coefficient>.mustBeExactly(a: Float): Constraint {
    return Constraint(this,
        mustBeMoreThanOrEqual = a, mustBeLessThanOrEqual = a)
}

fun MPSolver.maximize(coefficients: List<Coefficient>): MPSolver.ResultStatus {
    val objective: MPObjective = this.objective()
    for (i in coefficients) {
        objective.setCoefficient(i.mpVar, i.coefficient.toDouble())
    }
    objective.setMaximization()
    return this.solve()
}

fun MPSolver.createConstraint(
    constraint: Constraint,
) {
    return constraint.let {
        this.makeConstraint(
            constraint.mustBeMoreThanOrEqual.toDouble(),
            constraint.mustBeLessThanOrEqual.toDouble()
        ).apply {
            it.sumOfCoefficients.map {
            this.setCoefficient(it.mpVar, it.coefficient.toDouble())
        };
    }
    }
}
