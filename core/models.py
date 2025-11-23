"""
Core data models for the nurse scheduling system.
Designed for Egyptian healthcare context.
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import List, Dict, Optional, Set
import numpy as np


class ShiftType(Enum):
    """Shift types common in Egyptian hospitals"""
    MORNING = "morning"      # 7:00 - 15:00
    AFTERNOON = "afternoon"  # 15:00 - 23:00
    NIGHT = "night"         # 23:00 - 7:00
    EXTENDED = "extended"    # 12-hour shifts
    REST = "rest"           # Day off


class SkillLevel(Enum):
    """Nurse skill levels per Egyptian Medical Syndicate"""
    JUNIOR = "junior"           # < 2 years experience
    INTERMEDIATE = "intermediate"  # 2-5 years
    SENIOR = "senior"           # 5-10 years
    SPECIALIST = "specialist"   # > 10 years or specialized
    HEAD_NURSE = "head_nurse"   # Supervisory


class ContractType(Enum):
    """Employment contract types in Egypt"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    TEMPORARY = "temporary"
    ON_CALL = "on_call"


@dataclass
class NursePreferences:
    """Nurse scheduling preferences"""
    preferred_shifts: List[ShiftType] = field(default_factory=list)
    avoided_shifts: List[ShiftType] = field(default_factory=list)
    max_consecutive_days: int = 5
    min_rest_days_per_week: int = 1
    preferred_days_off: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    
    # Egyptian-specific preferences
    prefer_friday_off: bool = True  # Jumu'ah prayer
    ramadan_reduced_hours: bool = True
    avoid_night_shifts_ramadan: bool = False
    
    # Personal constraints
    has_childcare_constraints: bool = False
    prefers_morning: bool = False
    max_night_shifts_per_week: int = 3


@dataclass
class Nurse:
    """Nurse entity with Egyptian healthcare context"""
    id: str
    name: str
    name_ar: Optional[str] = None  # Arabic name
    
    # Professional attributes
    skill_level: SkillLevel = SkillLevel.INTERMEDIATE
    specializations: List[str] = field(default_factory=list)
    contract_type: ContractType = ContractType.FULL_TIME
    
    # Work capacity
    max_hours_per_week: int = 48  # Egyptian labor law standard
    max_consecutive_days: int = 6
    min_hours_between_shifts: int = 11  # Rest period requirement
    
    # Preferences and constraints
    preferences: NursePreferences = field(default_factory=NursePreferences)
    
    # Historical data
    average_workload: float = 40.0  # hours per week
    fatigue_score: float = 0.0  # 0-1, higher = more fatigued
    satisfaction_score: float = 0.8  # 0-1
    
    # Availability
    unavailable_dates: Set[datetime] = field(default_factory=set)
    vacation_dates: Set[datetime] = field(default_factory=set)
    
    def is_available(self, date: datetime) -> bool:
        """Check if nurse is available on a specific date"""
        return date not in self.unavailable_dates and date not in self.vacation_dates
    
    def can_work_shift(self, shift_type: ShiftType) -> bool:
        """Check if nurse can work a specific shift type"""
        if shift_type in self.preferences.avoided_shifts:
            return False
        return True
    
    def get_skill_multiplier(self) -> float:
        """Get skill level multiplier for workload calculation"""
        multipliers = {
            SkillLevel.JUNIOR: 0.8,
            SkillLevel.INTERMEDIATE: 1.0,
            SkillLevel.SENIOR: 1.2,
            SkillLevel.SPECIALIST: 1.3,
            SkillLevel.HEAD_NURSE: 1.5
        }
        return multipliers.get(self.skill_level, 1.0)


@dataclass
class Shift:
    """Work shift definition"""
    id: str
    shift_type: ShiftType
    start_time: time
    end_time: time
    date: datetime
    
    # Requirements
    required_nurses: int
    required_skills: List[SkillLevel] = field(default_factory=list)
    required_specializations: List[str] = field(default_factory=list)
    
    # Demand
    expected_patient_load: int = 0
    complexity_score: float = 1.0  # 1.0 = normal, >1.0 = more complex
    
    # Assigned nurses
    assigned_nurses: List[str] = field(default_factory=list)  # Nurse IDs
    
    def get_duration_hours(self) -> float:
        """Calculate shift duration in hours"""
        if self.shift_type == ShiftType.REST:
            return 0.0
        
        # Handle shifts crossing midnight
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        
        if end < start:
            end += timedelta(days=1)
        
        return (end - start).total_seconds() / 3600
    
    def is_fully_staffed(self) -> bool:
        """Check if shift has enough nurses assigned"""
        return len(self.assigned_nurses) >= self.required_nurses
    
    def get_understaffing_penalty(self) -> float:
        """Calculate penalty for understaffing"""
        if self.is_fully_staffed():
            return 0.0
        
        shortage = self.required_nurses - len(self.assigned_nurses)
        return shortage * self.complexity_score * 100  # High penalty


@dataclass
class Rotation:
    """
    A rotation is a sequence of consecutive working days for a nurse.
    This is the core concept from the NurseScheduler paper.
    """
    nurse_id: str
    shifts: List[Shift] = field(default_factory=list)
    
    def get_total_hours(self) -> float:
        """Get total hours in this rotation"""
        return sum(shift.get_duration_hours() for shift in self.shifts)
    
    def get_duration_days(self) -> int:
        """Get number of consecutive days worked"""
        if not self.shifts:
            return 0
        return len(self.shifts)
    
    def violates_max_consecutive(self, max_days: int) -> bool:
        """Check if rotation exceeds max consecutive days"""
        return self.get_duration_days() > max_days
    
    def get_cost(self, nurse: Nurse) -> float:
        """
        Calculate cost of this rotation including:
        - Preference violations
        - Overtime
        - Fatigue
        - Constraint violations
        """
        cost = 0.0
        
        # Base hours cost
        total_hours = self.get_total_hours()
        
        # Overtime penalty (Egyptian labor law: 48h/week standard)
        weekly_hours = total_hours  # Simplified
        if weekly_hours > nurse.max_hours_per_week:
            overtime = weekly_hours - nurse.max_hours_per_week
            cost += overtime * 50  # Overtime penalty
        
        # Consecutive days penalty
        if self.violates_max_consecutive(nurse.max_consecutive_days):
            cost += 200
        
        # Shift preference penalties
        for shift in self.shifts:
            if shift.shift_type in nurse.preferences.avoided_shifts:
                cost += 30
            if shift.shift_type not in nurse.preferences.preferred_shifts and \
               len(nurse.preferences.preferred_shifts) > 0:
                cost += 10
        
        # Night shift penalties
        night_shifts = sum(1 for s in self.shifts if s.shift_type == ShiftType.NIGHT)
        if night_shifts > nurse.preferences.max_night_shifts_per_week:
            cost += (night_shifts - nurse.preferences.max_night_shifts_per_week) * 40
        
        # Fatigue penalty (increases with existing fatigue)
        fatigue_penalty = total_hours * nurse.fatigue_score * 10
        cost += fatigue_penalty
        
        return cost


@dataclass
class Schedule:
    """Complete nurse schedule for a planning horizon"""
    start_date: datetime
    end_date: datetime
    nurses: List[Nurse]
    shifts: List[Shift]
    rotations: List[Rotation] = field(default_factory=list)
    
    # Metadata
    hospital_id: str = ""
    department: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_total_cost(self) -> float:
        """Calculate total schedule cost"""
        cost = 0.0
        
        # Rotation costs
        nurse_dict = {n.id: n for n in self.nurses}
        for rotation in self.rotations:
            if rotation.nurse_id in nurse_dict:
                cost += rotation.get_cost(nurse_dict[rotation.nurse_id])
        
        # Understaffing penalties
        for shift in self.shifts:
            cost += shift.get_understaffing_penalty()
        
        return cost
    
    def is_feasible(self) -> bool:
        """Check if schedule satisfies all hard constraints"""
        # Check all shifts are covered
        for shift in self.shifts:
            if shift.shift_type != ShiftType.REST and not shift.is_fully_staffed():
                return False
        
        # Check nurse constraints
        nurse_assignments = {n.id: [] for n in self.nurses}
        for rotation in self.rotations:
            for shift in rotation.shifts:
                nurse_assignments[rotation.nurse_id].append(shift)
        
        for nurse in self.nurses:
            assignments = nurse_assignments[nurse.id]
            
            # Check max hours
            total_hours = sum(s.get_duration_hours() for s in assignments)
            if total_hours > nurse.max_hours_per_week * 4:  # 4 weeks
                return False
            
            # Check rest periods
            sorted_shifts = sorted(assignments, key=lambda s: s.date)
            for i in range(len(sorted_shifts) - 1):
                time_diff = (sorted_shifts[i+1].date - sorted_shifts[i].date).total_seconds() / 3600
                if time_diff < nurse.min_hours_between_shifts:
                    return False
        
        return True
    
    def get_nurse_satisfaction(self) -> Dict[str, float]:
        """Calculate satisfaction score for each nurse"""
        satisfaction = {}
        nurse_dict = {n.id: n for n in self.nurses}
        
        for nurse in self.nurses:
            nurse_rotations = [r for r in self.rotations if r.nurse_id == nurse.id]
            
            if not nurse_rotations:
                satisfaction[nurse.id] = 1.0
                continue
            
            # Calculate based on preference matching
            total_shifts = sum(len(r.shifts) for r in nurse_rotations)
            preference_matches = 0
            
            for rotation in nurse_rotations:
                for shift in rotation.shifts:
                    if shift.shift_type in nurse.preferences.preferred_shifts:
                        preference_matches += 1
            
            if total_shifts > 0:
                satisfaction[nurse.id] = preference_matches / total_shifts
            else:
                satisfaction[nurse.id] = 1.0
        
        return satisfaction
    
    def get_metrics(self) -> Dict:
        """Get comprehensive schedule metrics"""
        return {
            "total_cost": self.get_total_cost(),
            "is_feasible": self.is_feasible(),
            "nurse_satisfaction": np.mean(list(self.get_nurse_satisfaction().values())),
            "total_nurses": len(self.nurses),
            "total_shifts": len(self.shifts),
            "total_rotations": len(self.rotations),
            "average_hours_per_nurse": np.mean([
                sum(s.get_duration_hours() for r in self.rotations if r.nurse_id == n.id 
                    for s in r.shifts) for n in self.nurses
            ])
        }


@dataclass
class SchedulingProblem:
    """Complete scheduling problem definition"""
    nurses: List[Nurse]
    planning_horizon_days: int
    start_date: datetime
    shifts_per_day: List[ShiftType]
    
    # Demand (can be forecasted)
    daily_demand: Dict[ShiftType, int]  # Required nurses per shift type
    
    # Egyptian-specific
    ramadan_start: Optional[datetime] = None
    ramadan_end: Optional[datetime] = None
    public_holidays: List[datetime] = field(default_factory=list)
    
    def generate_shifts(self) -> List[Shift]:
        """Generate all shifts for the planning horizon"""
        shifts = []
        shift_times = {
            ShiftType.MORNING: (time(7, 0), time(15, 0)),
            ShiftType.AFTERNOON: (time(15, 0), time(23, 0)),
            ShiftType.NIGHT: (time(23, 0), time(7, 0)),
            ShiftType.EXTENDED: (time(7, 0), time(19, 0)),
        }
        
        for day in range(self.planning_horizon_days):
            current_date = self.start_date + timedelta(days=day)
            
            for shift_type in self.shifts_per_day:
                if shift_type == ShiftType.REST:
                    continue
                
                start_time, end_time = shift_times[shift_type]
                
                shift = Shift(
                    id=f"{current_date.date()}_{shift_type.value}",
                    shift_type=shift_type,
                    start_time=start_time,
                    end_time=end_time,
                    date=current_date,
                    required_nurses=self.daily_demand.get(shift_type, 1)
                )
                
                # Adjust for Ramadan
                if self.ramadan_start and self.ramadan_end:
                    if self.ramadan_start <= current_date <= self.ramadan_end:
                        shift.complexity_score = 1.2  # Higher complexity during Ramadan
                
                shifts.append(shift)
        
        return shifts
