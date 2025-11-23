"""
Constraint definitions for nurse scheduling.
Implements both hard and soft constraints per Egyptian regulations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.models import Nurse, Shift, Rotation, Schedule, ShiftType
import numpy as np


class Constraint(ABC):
    """Abstract base class for constraints"""
    
    def __init__(self, weight: float = 1.0, is_hard: bool = True):
        self.weight = weight
        self.is_hard = is_hard
    
    @abstractmethod
    def evaluate(self, schedule: Schedule) -> float:
        """
        Evaluate constraint violation.
        Returns 0 if satisfied, positive value for violations.
        """
        pass
    
    @abstractmethod
    def is_satisfied(self, schedule: Schedule) -> bool:
        """Check if constraint is satisfied"""
        pass
    
    def get_penalty(self, schedule: Schedule) -> float:
        """Get weighted penalty for constraint violation"""
        return self.weight * self.evaluate(schedule)


class MaxConsecutiveDaysConstraint(Constraint):
    """Maximum consecutive working days (Egyptian labor law: typically 6 days)"""
    
    def __init__(self, max_days: int = 6, weight: float = 100.0, is_hard: bool = True):
        super().__init__(weight, is_hard)
        self.max_days = max_days
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        
        for nurse in schedule.nurses:
            nurse_shifts = []
            for rotation in schedule.rotations:
                if rotation.nurse_id == nurse.id:
                    nurse_shifts.extend(rotation.shifts)
            
            # Sort by date
            nurse_shifts.sort(key=lambda s: s.date)
            
            # Count consecutive days
            if not nurse_shifts:
                continue
            
            consecutive = 1
            max_consecutive = 1
            
            for i in range(1, len(nurse_shifts)):
                days_diff = (nurse_shifts[i].date - nurse_shifts[i-1].date).days
                
                if days_diff == 1:
                    consecutive += 1
                    max_consecutive = max(max_consecutive, consecutive)
                else:
                    consecutive = 1
            
            if max_consecutive > self.max_days:
                total_violation += (max_consecutive - self.max_days)
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return self.evaluate(schedule) == 0


class MinRestPeriodConstraint(Constraint):
    """Minimum rest period between shifts (Egyptian law: 11 hours)"""
    
    def __init__(self, min_hours: int = 11, weight: float = 200.0, is_hard: bool = True):
        super().__init__(weight, is_hard)
        self.min_hours = min_hours
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        
        for nurse in schedule.nurses:
            nurse_shifts = []
            for rotation in schedule.rotations:
                if rotation.nurse_id == nurse.id:
                    nurse_shifts.extend(rotation.shifts)
            
            nurse_shifts.sort(key=lambda s: s.date)
            
            for i in range(len(nurse_shifts) - 1):
                shift1 = nurse_shifts[i]
                shift2 = nurse_shifts[i + 1]
                
                # Calculate rest period
                end_time1 = datetime.combine(shift1.date, shift1.end_time)
                start_time2 = datetime.combine(shift2.date, shift2.start_time)
                
                # Handle shifts crossing midnight
                if shift1.end_time < shift1.start_time:
                    end_time1 += timedelta(days=1)
                
                rest_hours = (start_time2 - end_time1).total_seconds() / 3600
                
                if rest_hours < self.min_hours:
                    total_violation += (self.min_hours - rest_hours)
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return self.evaluate(schedule) == 0


class MaxWeeklyHoursConstraint(Constraint):
    """Maximum weekly hours (Egyptian labor law: 48 hours standard)"""
    
    def __init__(self, max_hours: float = 48.0, weight: float = 50.0, is_hard: bool = True):
        super().__init__(weight, is_hard)
        self.max_hours = max_hours
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        
        for nurse in schedule.nurses:
            nurse_shifts = []
            for rotation in schedule.rotations:
                if rotation.nurse_id == nurse.id:
                    nurse_shifts.extend(rotation.shifts)
            
            # Group by week
            weeks = {}
            for shift in nurse_shifts:
                week_num = shift.date.isocalendar()[1]
                if week_num not in weeks:
                    weeks[week_num] = []
                weeks[week_num].append(shift)
            
            # Check each week
            for week_shifts in weeks.values():
                total_hours = sum(s.get_duration_hours() for s in week_shifts)
                
                if total_hours > self.max_hours:
                    total_violation += (total_hours - self.max_hours)
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return self.evaluate(schedule) == 0


class ShiftCoverageConstraint(Constraint):
    """All shifts must have required number of nurses"""
    
    def __init__(self, weight: float = 500.0, is_hard: bool = True):
        super().__init__(weight, is_hard)
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        
        for shift in schedule.shifts:
            if shift.shift_type == ShiftType.REST:
                continue
            
            shortage = max(0, shift.required_nurses - len(shift.assigned_nurses))
            total_violation += shortage * shift.complexity_score
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return self.evaluate(schedule) == 0


class SkillMixConstraint(Constraint):
    """Each shift must have appropriate skill mix"""
    
    def __init__(self, weight: float = 100.0, is_hard: bool = False):
        super().__init__(weight, is_hard)
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        nurse_dict = {n.id: n for n in schedule.nurses}
        
        for shift in schedule.shifts:
            if shift.shift_type == ShiftType.REST or not shift.required_skills:
                continue
            
            assigned_skills = [
                nurse_dict[nid].skill_level 
                for nid in shift.assigned_nurses 
                if nid in nurse_dict
            ]
            
            # Check if required skills are present
            for required_skill in shift.required_skills:
                if required_skill not in assigned_skills:
                    total_violation += 1
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return self.evaluate(schedule) == 0


class PreferenceConstraint(Constraint):
    """Soft constraint for nurse preferences"""
    
    def __init__(self, weight: float = 10.0, is_hard: bool = False):
        super().__init__(weight, is_hard)
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        nurse_dict = {n.id: n for n in schedule.nurses}
        
        for rotation in schedule.rotations:
            nurse = nurse_dict.get(rotation.nurse_id)
            if not nurse:
                continue
            
            for shift in rotation.shifts:
                # Avoided shifts
                if shift.shift_type in nurse.preferences.avoided_shifts:
                    total_violation += 3
                
                # Not preferred shifts
                if nurse.preferences.preferred_shifts and \
                   shift.shift_type not in nurse.preferences.preferred_shifts:
                    total_violation += 1
                
                # Night shift limits
                night_shifts = sum(
                    1 for s in rotation.shifts 
                    if s.shift_type == ShiftType.NIGHT
                )
                if night_shifts > nurse.preferences.max_night_shifts_per_week:
                    total_violation += (night_shifts - nurse.preferences.max_night_shifts_per_week)
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        # Soft constraint, always "satisfied" but with penalty
        return True


class FridayOffConstraint(Constraint):
    """Preference for Friday off (Jumu'ah prayer) - Egyptian specific"""
    
    def __init__(self, weight: float = 20.0, is_hard: bool = False):
        super().__init__(weight, is_hard)
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        nurse_dict = {n.id: n for n in schedule.nurses}
        
        for nurse in schedule.nurses:
            if not nurse.preferences.prefer_friday_off:
                continue
            
            nurse_shifts = []
            for rotation in schedule.rotations:
                if rotation.nurse_id == nurse.id:
                    nurse_shifts.extend(rotation.shifts)
            
            # Check Fridays
            friday_shifts = [
                s for s in nurse_shifts 
                if s.date.weekday() == 4  # Friday
            ]
            
            total_violation += len(friday_shifts)
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return True  # Soft constraint


class RamadanConstraint(Constraint):
    """Ramadan-specific scheduling constraints - Egyptian specific"""
    
    def __init__(self, ramadan_start: datetime, ramadan_end: datetime, 
                 weight: float = 15.0, is_hard: bool = False):
        super().__init__(weight, is_hard)
        self.ramadan_start = ramadan_start
        self.ramadan_end = ramadan_end
    
    def evaluate(self, schedule: Schedule) -> float:
        total_violation = 0.0
        nurse_dict = {n.id: n for n in schedule.nurses}
        
        for rotation in schedule.rotations:
            nurse = nurse_dict.get(rotation.nurse_id)
            if not nurse:
                continue
            
            for shift in rotation.shifts:
                # Check if shift is during Ramadan
                if self.ramadan_start <= shift.date <= self.ramadan_end:
                    # Prefer no night shifts during Ramadan
                    if nurse.preferences.avoid_night_shifts_ramadan and \
                       shift.shift_type == ShiftType.NIGHT:
                        total_violation += 2
                    
                    # Reduced hours preference
                    if nurse.preferences.ramadan_reduced_hours:
                        if shift.get_duration_hours() > 6:
                            total_violation += 1
        
        return total_violation
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return True  # Soft constraint


class FairnessConstraint(Constraint):
    """Ensure fair distribution of workload and undesirable shifts"""
    
    def __init__(self, weight: float = 25.0, is_hard: bool = False):
        super().__init__(weight, is_hard)
    
    def evaluate(self, schedule: Schedule) -> float:
        # Calculate workload variance
        nurse_hours = {}
        
        for nurse in schedule.nurses:
            total_hours = 0.0
            for rotation in schedule.rotations:
                if rotation.nurse_id == nurse.id:
                    total_hours += rotation.get_total_hours()
            nurse_hours[nurse.id] = total_hours
        
        if not nurse_hours:
            return 0.0
        
        hours_list = list(nurse_hours.values())
        mean_hours = np.mean(hours_list)
        std_hours = np.std(hours_list)
        
        # Penalize high variance (unfair distribution)
        return std_hours / (mean_hours + 1e-6) * 100
    
    def is_satisfied(self, schedule: Schedule) -> bool:
        return True  # Soft constraint


class ConstraintEngine:
    """Manages and evaluates all constraints"""
    
    def __init__(self):
        self.hard_constraints: List[Constraint] = []
        self.soft_constraints: List[Constraint] = []
    
    def add_constraint(self, constraint: Constraint):
        """Add a constraint to the engine"""
        if constraint.is_hard:
            self.hard_constraints.append(constraint)
        else:
            self.soft_constraints.append(constraint)
    
    def add_egyptian_constraints(self, ramadan_start: Optional[datetime] = None,
                                 ramadan_end: Optional[datetime] = None):
        """Add standard Egyptian healthcare constraints"""
        
        # Hard constraints (must be satisfied)
        self.add_constraint(MaxConsecutiveDaysConstraint(max_days=6, weight=100.0))
        self.add_constraint(MinRestPeriodConstraint(min_hours=11, weight=200.0))
        self.add_constraint(MaxWeeklyHoursConstraint(max_hours=48.0, weight=50.0))
        self.add_constraint(ShiftCoverageConstraint(weight=500.0))
        
        # Soft constraints (preferences)
        self.add_constraint(PreferenceConstraint(weight=10.0, is_hard=False))
        self.add_constraint(FridayOffConstraint(weight=20.0, is_hard=False))
        self.add_constraint(FairnessConstraint(weight=25.0, is_hard=False))
        self.add_constraint(SkillMixConstraint(weight=100.0, is_hard=False))
        
        # Ramadan constraints if applicable
        if ramadan_start and ramadan_end:
            self.add_constraint(
                RamadanConstraint(ramadan_start, ramadan_end, weight=15.0, is_hard=False)
            )
    
    def is_feasible(self, schedule: Schedule) -> bool:
        """Check if schedule satisfies all hard constraints"""
        return all(c.is_satisfied(schedule) for c in self.hard_constraints)
    
    def evaluate_hard_constraints(self, schedule: Schedule) -> float:
        """Get total penalty from hard constraint violations"""
        return sum(c.get_penalty(schedule) for c in self.hard_constraints)
    
    def evaluate_soft_constraints(self, schedule: Schedule) -> float:
        """Get total penalty from soft constraint violations"""
        return sum(c.get_penalty(schedule) for c in self.soft_constraints)
    
    def evaluate_total(self, schedule: Schedule) -> float:
        """Get total constraint penalty"""
        return (self.evaluate_hard_constraints(schedule) + 
                self.evaluate_soft_constraints(schedule))
    
    def get_constraint_violations(self, schedule: Schedule) -> Dict[str, float]:
        """Get detailed breakdown of constraint violations"""
        violations = {}
        
        for constraint in self.hard_constraints + self.soft_constraints:
            constraint_name = constraint.__class__.__name__
            penalty = constraint.get_penalty(schedule)
            if penalty > 0:
                violations[constraint_name] = penalty
        
        return violations
    
    def get_metrics(self, schedule: Schedule) -> Dict:
        """Get comprehensive constraint metrics"""
        return {
            "is_feasible": self.is_feasible(schedule),
            "hard_constraint_penalty": self.evaluate_hard_constraints(schedule),
            "soft_constraint_penalty": self.evaluate_soft_constraints(schedule),
            "total_penalty": self.evaluate_total(schedule),
            "constraint_violations": self.get_constraint_violations(schedule)
        }
