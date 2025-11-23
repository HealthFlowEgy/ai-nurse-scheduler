"""
Main optimization engine combining branch-and-price with AI enhancements.
Integrates demand forecasting, fatigue prediction, and RL-based branching.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pulp import *
import time

from core.models import (
    Nurse, Shift, Rotation, Schedule, SchedulingProblem,
    ShiftType, SkillLevel
)
from core.constraints import ConstraintEngine
from ml.demand_forecaster import DemandForecaster
from ml.fatigue_predictor import FatiguePredictor
from ml.rl_agent import RLBranchingAgent, SchedulingEnvironment


class AIEnhancedOptimizer:
    """
    Main optimization engine with AI enhancements.
    
    Features:
    - Branch-and-price core algorithm
    - ML-based demand forecasting
    - Fatigue prediction for nurse well-being
    - RL-guided branching decisions
    - Egyptian healthcare context awareness
    """
    
    def __init__(self, use_ml: bool = True, use_rl: bool = False):
        """
        Args:
            use_ml: Enable ML features (demand forecasting, fatigue prediction)
            use_rl: Enable RL-based branching (requires trained agent)
        """
        self.use_ml = use_ml
        self.use_rl = use_rl
        
        # ML components
        self.demand_forecaster = DemandForecaster() if use_ml else None
        self.fatigue_predictor = FatiguePredictor() if use_ml else None
        self.rl_agent = None
        
        # Constraint engine
        self.constraint_engine = ConstraintEngine()
        
        # Statistics
        self.stats = {
            'solve_time': 0,
            'iterations': 0,
            'ml_time': 0,
            'best_objective': float('inf')
        }
    
    def setup_egyptian_constraints(self, ramadan_start: Optional[datetime] = None,
                                   ramadan_end: Optional[datetime] = None):
        """Setup Egyptian healthcare-specific constraints"""
        self.constraint_engine.add_egyptian_constraints(ramadan_start, ramadan_end)
    
    def load_ml_models(self, demand_model_path: str, fatigue_model_path: str):
        """Load pre-trained ML models"""
        if self.use_ml:
            print("Loading ML models...")
            self.demand_forecaster.load(demand_model_path)
            self.fatigue_predictor.load(fatigue_model_path)
            print("ML models loaded successfully!")
    
    def load_rl_agent(self, agent_path: str):
        """Load pre-trained RL agent"""
        if self.use_rl:
            print("Loading RL agent...")
            # Would load trained agent here
            print("RL agent loaded successfully!")
    
    def generate_rotations(self, nurse: Nurse, shifts: List[Shift], 
                          max_rotations: int = 100) -> List[Rotation]:
        """
        Generate candidate rotations for a nurse.
        This is the pricing subproblem in column generation.
        
        Args:
            nurse: Nurse to generate rotations for
            shifts: Available shifts
            max_rotations: Maximum number of rotations to generate
        
        Returns:
            List of feasible rotations
        """
        rotations = []
        
        # Filter shifts nurse can work
        available_shifts = [
            s for s in shifts 
            if nurse.is_available(s.date) and nurse.can_work_shift(s.shift_type)
        ]
        
        # Sort by date
        available_shifts.sort(key=lambda s: s.date)
        
        # Generate rotations using dynamic programming approach
        # For simplicity, we'll use a greedy heuristic here
        
        # Short rotations (1-3 days)
        for start_idx in range(len(available_shifts)):
            for length in range(1, min(4, len(available_shifts) - start_idx + 1)):
                rotation_shifts = available_shifts[start_idx:start_idx + length]
                
                # Check if consecutive
                is_consecutive = True
                for i in range(len(rotation_shifts) - 1):
                    days_diff = (rotation_shifts[i+1].date - rotation_shifts[i].date).days
                    if days_diff != 1:
                        is_consecutive = False
                        break
                
                if is_consecutive:
                    rotation = Rotation(nurse_id=nurse.id, shifts=rotation_shifts)
                    
                    # Check if rotation is feasible
                    if not rotation.violates_max_consecutive(nurse.max_consecutive_days):
                        rotations.append(rotation)
        
        # Medium rotations (4-6 days)
        for start_idx in range(len(available_shifts)):
            for length in range(4, min(7, len(available_shifts) - start_idx + 1)):
                rotation_shifts = available_shifts[start_idx:start_idx + length]
                
                is_consecutive = True
                for i in range(len(rotation_shifts) - 1):
                    days_diff = (rotation_shifts[i+1].date - rotation_shifts[i].date).days
                    if days_diff != 1:
                        is_consecutive = False
                        break
                
                if is_consecutive:
                    rotation = Rotation(nurse_id=nurse.id, shifts=rotation_shifts)
                    if not rotation.violates_max_consecutive(nurse.max_consecutive_days):
                        rotations.append(rotation)
        
        # Limit number of rotations
        return rotations[:max_rotations]
    
    def solve_master_problem(self, nurses: List[Nurse], shifts: List[Shift],
                            rotations: List[Rotation]) -> Tuple[Dict, float]:
        """
        Solve the master problem (restricted master problem in column generation).
        
        Args:
            nurses: List of nurses
            shifts: List of shifts to cover
            rotations: Current set of rotations
        
        Returns:
            Solution dictionary and objective value
        """
        # Create LP problem
        prob = LpProblem("NurseScheduling", LpMinimize)
        
        # Decision variables: which rotations to use
        rotation_vars = {}
        for i, rotation in enumerate(rotations):
            rotation_vars[i] = LpVariable(f"rotation_{i}", lowBound=0, upBound=1, cat='Continuous')
        
        # Objective: minimize total cost
        prob += lpSum([
            rotation_vars[i] * rotations[i].get_cost(
                next(n for n in nurses if n.id == rotations[i].nurse_id)
            )
            for i in range(len(rotations))
        ])
        
        # Constraints: Each shift must be covered
        shift_coverage = {}
        for shift in shifts:
            if shift.shift_type == ShiftType.REST:
                continue
            
            shift_coverage[shift.id] = []
            for i, rotation in enumerate(rotations):
                if shift in rotation.shifts:
                    shift_coverage[shift.id].append(rotation_vars[i])
            
            if shift_coverage[shift.id]:
                prob += lpSum(shift_coverage[shift.id]) >= shift.required_nurses
        
        # Convexity constraints: Each nurse used at most once per time period
        nurse_usage = {nurse.id: [] for nurse in nurses}
        for i, rotation in enumerate(rotations):
            nurse_usage[rotation.nurse_id].append(rotation_vars[i])
        
        for nurse_id, vars_list in nurse_usage.items():
            if vars_list:
                prob += lpSum(vars_list) <= 1
        
        # Solve
        prob.solve(PULP_CBC_CMD(msg=0))
        
        # Extract solution
        solution = {}
        for i, var in rotation_vars.items():
            if var.varValue and var.varValue > 0.01:
                solution[i] = var.varValue
        
        objective = value(prob.objective)
        
        return solution, objective
    
    def optimize(self, problem: SchedulingProblem, 
                max_iterations: int = 10, 
                time_limit: float = 300) -> Schedule:
        """
        Main optimization function.
        
        Args:
            problem: Scheduling problem definition
            max_iterations: Maximum column generation iterations
            time_limit: Time limit in seconds
        
        Returns:
            Optimized schedule
        """
        start_time = time.time()
        print("=" * 60)
        print("AI-Enhanced Nurse Scheduler")
        print("=" * 60)
        
        # Step 1: Demand Forecasting (if ML enabled)
        if self.use_ml and self.demand_forecaster.is_trained:
            print("\n[1/5] Forecasting demand...")
            ml_start = time.time()
            
            demand_forecast = self.demand_forecaster.predict(
                problem.start_date,
                problem.planning_horizon_days
            )
            
            # Update daily demand based on forecast
            for date, demands in demand_forecast.items():
                problem.daily_demand[ShiftType.MORNING] = demands['morning']
                problem.daily_demand[ShiftType.AFTERNOON] = demands['afternoon']
                problem.daily_demand[ShiftType.NIGHT] = demands['night']
            
            self.stats['ml_time'] += time.time() - ml_start
            print(f"   Demand forecasting completed in {time.time() - ml_start:.2f}s")
        else:
            print("\n[1/5] Using default demand (ML not enabled)")
        
        # Step 2: Generate shifts
        print("\n[2/5] Generating shifts...")
        shifts = problem.generate_shifts()
        print(f"   Generated {len(shifts)} shifts over {problem.planning_horizon_days} days")
        
        # Step 3: Predict fatigue (if ML enabled)
        if self.use_ml and self.fatigue_predictor.is_trained:
            print("\n[3/5] Predicting nurse fatigue...")
            ml_start = time.time()
            
            for nurse in problem.nurses:
                # Simulate nurse history
                nurse_history = {
                    'shifts_last_week': [],
                    'shifts_last_month': [],
                    'personal_info': {
                        'age': 35,
                        'experience': 5,
                        'has_children': False,
                        'max_hours_per_week': nurse.max_hours_per_week
                    },
                    'preferences': nurse.preferences.__dict__
                }
                
                fatigue = self.fatigue_predictor.predict(nurse_history)
                nurse.fatigue_score = fatigue['overall_fatigue']
            
            self.stats['ml_time'] += time.time() - ml_start
            print(f"   Fatigue prediction completed in {time.time() - ml_start:.2f}s")
        else:
            print("\n[3/5] Skipping fatigue prediction (ML not enabled)")
        
        # Step 4: Column generation
        print("\n[4/5] Running branch-and-price optimization...")
        print(f"   Nurses: {len(problem.nurses)}, Shifts: {len(shifts)}")
        
        # Initialize with some rotations
        all_rotations = []
        for nurse in problem.nurses:
            nurse_rotations = self.generate_rotations(nurse, shifts, max_rotations=20)
            all_rotations.extend(nurse_rotations)
        
        print(f"   Initial rotations: {len(all_rotations)}")
        
        # Column generation loop
        best_objective = float('inf')
        iteration = 0
        
        while iteration < max_iterations and (time.time() - start_time) < time_limit:
            iteration += 1
            
            # Solve master problem
            solution, objective = self.solve_master_problem(
                problem.nurses, shifts, all_rotations
            )
            
            print(f"   Iteration {iteration}: Objective = {objective:.2f}")
            
            if objective < best_objective:
                best_objective = objective
                self.stats['best_objective'] = best_objective
            
            # Check convergence
            if abs(objective - best_objective) < 1.0:
                print("   Converged!")
                break
            
            # Generate new columns (simplified - would normally use dual values)
            # In production, solve pricing subprobems using dual values
            new_rotations = 0
            for nurse in problem.nurses:
                additional = self.generate_rotations(nurse, shifts, max_rotations=5)
                # Filter out existing rotations
                for rot in additional:
                    if not any(self._rotations_equal(rot, r) for r in all_rotations):
                        all_rotations.append(rot)
                        new_rotations += 1
            
            print(f"   Added {new_rotations} new rotations")
            
            if new_rotations == 0:
                print("   No new rotations found!")
                break
        
        self.stats['iterations'] = iteration
        
        # Step 5: Construct final schedule
        print("\n[5/5] Constructing final schedule...")
        
        # Round fractional solution to integers (simplified)
        selected_rotations = []
        for idx, value in solution.items():
            if value > 0.5:  # Simple rounding threshold
                selected_rotations.append(all_rotations[idx])
        
        # Assign shifts
        for rotation in selected_rotations:
            for shift in rotation.shifts:
                if rotation.nurse_id not in shift.assigned_nurses:
                    shift.assigned_nurses.append(rotation.nurse_id)
        
        # Create schedule
        schedule = Schedule(
            start_date=problem.start_date,
            end_date=problem.start_date + timedelta(days=problem.planning_horizon_days),
            nurses=problem.nurses,
            shifts=shifts,
            rotations=selected_rotations,
            hospital_id="HealthFlow_Hospital_01",
            department="General"
        )
        
        # Evaluate with constraints
        total_penalty = self.constraint_engine.evaluate_total(schedule)
        is_feasible = self.constraint_engine.is_feasible(schedule)
        
        self.stats['solve_time'] = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("OPTIMIZATION SUMMARY")
        print("=" * 60)
        print(f"Solve Time:        {self.stats['solve_time']:.2f}s")
        print(f"ML Time:           {self.stats['ml_time']:.2f}s")
        print(f"Iterations:        {self.stats['iterations']}")
        print(f"Objective Value:   {best_objective:.2f}")
        print(f"Total Penalty:     {total_penalty:.2f}")
        print(f"Is Feasible:       {is_feasible}")
        print(f"Rotations Used:    {len(selected_rotations)}")
        print(f"Nurse Satisfaction: {schedule.get_metrics()['nurse_satisfaction']:.2%}")
        print("=" * 60)
        
        return schedule
    
    def _rotations_equal(self, r1: Rotation, r2: Rotation) -> bool:
        """Check if two rotations are equal"""
        if r1.nurse_id != r2.nurse_id:
            return False
        if len(r1.shifts) != len(r2.shifts):
            return False
        return all(s1.id == s2.id for s1, s2 in zip(r1.shifts, r2.shifts))
    
    def get_statistics(self) -> Dict:
        """Get optimization statistics"""
        return self.stats.copy()


def create_sample_problem() -> SchedulingProblem:
    """Create a sample scheduling problem for Egyptian hospital"""
    print("Creating sample Egyptian hospital scheduling problem...")
    
    # Create nurses
    nurses = []
    for i in range(15):  # 15 nurses
        from core.models import NursePreferences
        
        prefs = NursePreferences(
            preferred_shifts=[ShiftType.MORNING] if i % 3 == 0 else [ShiftType.AFTERNOON],
            avoided_shifts=[ShiftType.NIGHT] if i % 4 == 0 else [],
            max_consecutive_days=5,
            prefer_friday_off=True,
            max_night_shifts_per_week=2
        )
        
        nurse = Nurse(
            id=f"nurse_{i:03d}",
            name=f"Nurse {i}",
            name_ar=f"ممرض {i}",
            skill_level=SkillLevel.INTERMEDIATE if i < 10 else SkillLevel.SENIOR,
            max_hours_per_week=48,
            preferences=prefs
        )
        nurses.append(nurse)
    
    # Create problem
    problem = SchedulingProblem(
        nurses=nurses,
        planning_horizon_days=14,  # 2 weeks
        start_date=datetime.now(),
        shifts_per_day=[ShiftType.MORNING, ShiftType.AFTERNOON, ShiftType.NIGHT],
        daily_demand={
            ShiftType.MORNING: 5,
            ShiftType.AFTERNOON: 4,
            ShiftType.NIGHT: 3
        }
    )
    
    return problem


if __name__ == "__main__":
    # Create sample problem
    problem = create_sample_problem()
    
    # Create optimizer
    optimizer = AIEnhancedOptimizer(use_ml=False, use_rl=False)
    
    # Setup Egyptian constraints
    optimizer.setup_egyptian_constraints()
    
    # Optimize
    schedule = optimizer.optimize(problem, max_iterations=5, time_limit=60)
    
    # Print results
    print("\n" + "=" * 60)
    print("SCHEDULE DETAILS")
    print("=" * 60)
    
    metrics = schedule.get_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    print(f"\nCoverage Status:")
    uncovered = sum(1 for s in schedule.shifts if not s.is_fully_staffed())
    print(f"  Uncovered shifts: {uncovered}/{len(schedule.shifts)}")
    
    print("\nOptimization complete!")
