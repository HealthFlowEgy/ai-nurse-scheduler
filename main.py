"""
Main entry point for AI-Enhanced Nurse Scheduler.
HealthFlow RegTech - Egypt's Digital Health Infrastructure
"""

import argparse
import yaml
from datetime import datetime
from pathlib import Path

from core.models import SchedulingProblem, Nurse, ShiftType, SkillLevel, NursePreferences
from core.optimizer import AIEnhancedOptimizer
from utils.egyptian_calendar import get_ramadan_dates
from utils.visualization import plot_schedule, generate_schedule_report


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def create_problem_from_config(config: dict) -> SchedulingProblem:
    """Create scheduling problem from configuration"""
    print("Loading problem from configuration...")
    
    # Create nurses
    nurses = []
    for nurse_data in config.get('nurses', []):
        prefs = NursePreferences(
            preferred_shifts=[ShiftType[s.upper()] for s in nurse_data.get('preferred_shifts', [])],
            avoided_shifts=[ShiftType[s.upper()] for s in nurse_data.get('avoided_shifts', [])],
            max_consecutive_days=nurse_data.get('max_consecutive_days', 5),
            prefer_friday_off=nurse_data.get('prefer_friday_off', True),
            avoid_night_shifts_ramadan=nurse_data.get('avoid_night_shifts_ramadan', False),
            max_night_shifts_per_week=nurse_data.get('max_night_shifts_per_week', 3)
        )
        
        nurse = Nurse(
            id=nurse_data['id'],
            name=nurse_data['name'],
            name_ar=nurse_data.get('name_ar'),
            skill_level=SkillLevel[nurse_data.get('skill_level', 'INTERMEDIATE').upper()],
            max_hours_per_week=nurse_data.get('max_hours_per_week', 48),
            preferences=prefs
        )
        nurses.append(nurse)
    
    print(f"   Loaded {len(nurses)} nurses")
    
    # Get schedule parameters
    schedule_config = config.get('schedule', {})
    
    # Parse dates
    start_date = datetime.strptime(schedule_config.get('start_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
    planning_days = schedule_config.get('planning_horizon_days', 14)
    
    # Get shift types
    shifts_per_day = [ShiftType[s.upper()] for s in schedule_config.get('shifts_per_day', ['morning', 'afternoon', 'night'])]
    
    # Get demand
    daily_demand = {}
    demand_config = schedule_config.get('daily_demand', {})
    for shift_name, count in demand_config.items():
        daily_demand[ShiftType[shift_name.upper()]] = count
    
    # Get Ramadan dates if configured
    ramadan_start = None
    ramadan_end = None
    if schedule_config.get('auto_ramadan', True):
        ramadan_start, ramadan_end = get_ramadan_dates(start_date.year)
        print(f"   Ramadan period: {ramadan_start.date()} to {ramadan_end.date()}")
    
    # Create problem
    problem = SchedulingProblem(
        nurses=nurses,
        planning_horizon_days=planning_days,
        start_date=start_date,
        shifts_per_day=shifts_per_day,
        daily_demand=daily_demand,
        ramadan_start=ramadan_start,
        ramadan_end=ramadan_end
    )
    
    print(f"   Planning horizon: {planning_days} days starting {start_date.date()}")
    print(f"   Shifts per day: {len(shifts_per_day)}")
    
    return problem


def main():
    parser = argparse.ArgumentParser(
        description='AI-Enhanced Nurse Scheduler for HealthFlow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default configuration
  python main.py

  # Run with custom configuration
  python main.py --config config/hospital_cairo.yaml

  # Enable ML features with pre-trained models
  python main.py --use-ml --demand-model models/demand.pth --fatigue-model models/fatigue.pkl

  # Generate visualization
  python main.py --visualize --output results/schedule.html
        """
    )
    
    parser.add_argument('--config', type=str, default='config/default.yaml',
                       help='Path to configuration file')
    parser.add_argument('--use-ml', action='store_true',
                       help='Enable ML features (demand forecasting, fatigue prediction)')
    parser.add_argument('--use-rl', action='store_true',
                       help='Enable RL-based branching optimization')
    parser.add_argument('--demand-model', type=str,
                       help='Path to trained demand forecasting model')
    parser.add_argument('--fatigue-model', type=str,
                       help='Path to trained fatigue prediction model')
    parser.add_argument('--rl-agent', type=str,
                       help='Path to trained RL agent')
    parser.add_argument('--max-iterations', type=int, default=10,
                       help='Maximum optimization iterations')
    parser.add_argument('--time-limit', type=float, default=300,
                       help='Time limit in seconds')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate schedule visualization')
    parser.add_argument('--output', type=str, default='results/schedule',
                       help='Output path for results')
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 70)
    print(" " * 15 + "AI-ENHANCED NURSE SCHEDULER")
    print(" " * 10 + "HealthFlow RegTech - Digital Health Egypt")
    print("=" * 70)
    print()
    
    # Load configuration
    print(f"Loading configuration from {args.config}...")
    try:
        config = load_config(args.config)
        print("   Configuration loaded successfully")
    except FileNotFoundError:
        print(f"   Warning: Config file not found, using defaults")
        config = {
            'hospital': {'name': 'HealthFlow Hospital', 'location': 'Cairo'},
            'schedule': {
                'planning_horizon_days': 14,
                'shifts_per_day': ['morning', 'afternoon', 'night'],
                'daily_demand': {'morning': 5, 'afternoon': 4, 'night': 3}
            },
            'optimization': {'max_iterations': 10, 'time_limit': 300}
        }
    
    print()
    
    # Create optimizer
    print("Initializing optimizer...")
    optimizer = AIEnhancedOptimizer(use_ml=args.use_ml, use_rl=args.use_rl)
    
    # Load ML models if specified
    if args.use_ml:
        if args.demand_model:
            try:
                optimizer.load_ml_models(args.demand_model, args.fatigue_model)
            except Exception as e:
                print(f"   Warning: Could not load ML models: {e}")
                print("   Continuing without ML features")
                optimizer.use_ml = False
    
    # Load RL agent if specified
    if args.use_rl and args.rl_agent:
        try:
            optimizer.load_rl_agent(args.rl_agent)
        except Exception as e:
            print(f"   Warning: Could not load RL agent: {e}")
            print("   Continuing without RL optimization")
            optimizer.use_rl = False
    
    print()
    
    # Create problem
    if 'nurses' in config:
        problem = create_problem_from_config(config)
    else:
        print("No nurses in config, creating sample problem...")
        from core.optimizer import create_sample_problem
        problem = create_sample_problem()
    
    print()
    
    # Setup constraints
    print("Setting up Egyptian healthcare constraints...")
    optimizer.setup_egyptian_constraints(
        problem.ramadan_start,
        problem.ramadan_end
    )
    print("   Constraints configured")
    print()
    
    # Run optimization
    max_iter = args.max_iterations or config.get('optimization', {}).get('max_iterations', 10)
    time_limit = args.time_limit or config.get('optimization', {}).get('time_limit', 300)
    
    schedule = optimizer.optimize(
        problem,
        max_iterations=max_iter,
        time_limit=time_limit
    )
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving results to {output_path}...")
    
    # Generate report
    report = generate_schedule_report(schedule, optimizer.get_statistics())
    
    with open(f"{output_path}_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   Report saved: {output_path}_report.txt")
    
    # Generate visualization if requested
    if args.visualize:
        try:
            print("   Generating visualization...")
            plot_schedule(schedule, f"{output_path}.html")
            print(f"   Visualization saved: {output_path}.html")
        except Exception as e:
            print(f"   Warning: Could not generate visualization: {e}")
    
    print()
    print("=" * 70)
    print("OPTIMIZATION COMPLETE!")
    print("=" * 70)
    print()
    
    # Print quick summary
    metrics = schedule.get_metrics()
    print(f"✓ Schedule created for {metrics['total_nurses']} nurses")
    print(f"✓ {metrics['total_shifts']} shifts scheduled")
    print(f"✓ Nurse satisfaction: {metrics['nurse_satisfaction']:.1%}")
    print(f"✓ Feasibility: {'FEASIBLE' if metrics['is_feasible'] else 'INFEASIBLE'}")
    print()
    
    hospital_info = config.get('hospital', {})
    print(f"Hospital: {hospital_info.get('name', 'N/A')}")
    print(f"Location: {hospital_info.get('location', 'N/A')}")
    print()


if __name__ == "__main__":
    main()
