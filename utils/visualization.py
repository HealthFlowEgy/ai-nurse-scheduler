"""
Visualization utilities for nurse schedules.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from typing import Dict
from core.models import Schedule


def plot_schedule(schedule: Schedule, output_path: str = "schedule.html"):
    """
    Create interactive visualization of the nurse schedule.
    
    Args:
        schedule: Schedule object to visualize
        output_path: Path to save HTML file
    """
    # Prepare data for Gantt chart
    gantt_data = []
    
    for rotation in schedule.rotations:
        nurse = next((n for n in schedule.nurses if n.id == rotation.nurse_id), None)
        if not nurse:
            continue
        
        for shift in rotation.shifts:
            gantt_data.append({
                'Nurse': nurse.name,
                'Start': shift.date,
                'Finish': shift.date,
                'Shift': shift.shift_type.value,
                'Duration': shift.get_duration_hours()
            })
    
    if not gantt_data:
        print("Warning: No data to plot")
        return
    
    df = pd.DataFrame(gantt_data)
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Schedule Timeline', 'Shift Distribution', 
                       'Hours per Nurse', 'Satisfaction Scores'),
        specs=[[{"type": "scatter", "colspan": 2}, None],
               [{"type": "bar"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Timeline (Gantt-style)
    colors = {
        'morning': '#FFD700',
        'afternoon': '#FF8C00',
        'night': '#191970',
        'extended': '#8B0000'
    }
    
    for shift_type in df['Shift'].unique():
        shift_data = df[df['Shift'] == shift_type]
        fig.add_trace(
            go.Scatter(
                x=shift_data['Start'],
                y=shift_data['Nurse'],
                mode='markers',
                name=shift_type.capitalize(),
                marker=dict(
                    size=15,
                    color=colors.get(shift_type, '#808080'),
                    symbol='square'
                )
            ),
            row=1, col=1
        )
    
    # 2. Shift distribution
    shift_counts = df['Shift'].value_counts()
    fig.add_trace(
        go.Bar(
            x=shift_counts.index,
            y=shift_counts.values,
            marker_color=[colors.get(s, '#808080') for s in shift_counts.index],
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 3. Hours per nurse
    nurse_hours = df.groupby('Nurse')['Duration'].sum().sort_values(ascending=True)
    fig.add_trace(
        go.Bar(
            x=nurse_hours.values,
            y=nurse_hours.index,
            orientation='h',
            marker_color='#4682B4',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Nurse Schedule - {schedule.start_date.date()} to {schedule.end_date.date()}",
            x=0.5,
            xanchor='center'
        ),
        height=900,
        showlegend=True,
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Nurse", row=1, col=1)
    fig.update_xaxes(title_text="Shift Type", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_xaxes(title_text="Hours", row=2, col=2)
    fig.update_yaxes(title_text="Nurse", row=2, col=2)
    
    # Save
    fig.write_html(output_path)
    print(f"Interactive visualization saved to {output_path}")


def generate_schedule_report(schedule: Schedule, stats: Dict) -> str:
    """
    Generate text report for schedule.
    
    Args:
        schedule: Schedule object
        stats: Optimization statistics
    
    Returns:
        Formatted report string
    """
    report = []
    
    # Header
    report.append("=" * 80)
    report.append(" " * 25 + "NURSE SCHEDULE REPORT")
    report.append(" " * 20 + "HealthFlow RegTech - Egypt")
    report.append("=" * 80)
    report.append("")
    
    # Schedule info
    report.append("SCHEDULE INFORMATION")
    report.append("-" * 80)
    report.append(f"Hospital ID:       {schedule.hospital_id}")
    report.append(f"Department:        {schedule.department}")
    report.append(f"Start Date:        {schedule.start_date.date()}")
    report.append(f"End Date:          {schedule.end_date.date()}")
    report.append(f"Duration:          {(schedule.end_date - schedule.start_date).days} days")
    report.append(f"Created:           {schedule.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Optimization stats
    report.append("OPTIMIZATION STATISTICS")
    report.append("-" * 80)
    report.append(f"Total Time:        {stats['solve_time']:.2f} seconds")
    report.append(f"ML Time:           {stats['ml_time']:.2f} seconds")
    report.append(f"Iterations:        {stats['iterations']}")
    report.append(f"Best Objective:    {stats['best_objective']:.2f}")
    report.append("")
    
    # Schedule metrics
    metrics = schedule.get_metrics()
    report.append("SCHEDULE METRICS")
    report.append("-" * 80)
    report.append(f"Total Nurses:      {metrics['total_nurses']}")
    report.append(f"Total Shifts:      {metrics['total_shifts']}")
    report.append(f"Total Rotations:   {metrics['total_rotations']}")
    report.append(f"Total Cost:        {metrics['total_cost']:.2f}")
    report.append(f"Feasibility:       {'FEASIBLE' if metrics['is_feasible'] else 'INFEASIBLE'}")
    report.append(f"Nurse Satisfaction: {metrics['nurse_satisfaction']:.1%}")
    report.append(f"Avg Hours/Nurse:   {metrics['average_hours_per_nurse']:.1f}")
    report.append("")
    
    # Shift coverage
    report.append("SHIFT COVERAGE")
    report.append("-" * 80)
    
    covered = sum(1 for s in schedule.shifts if s.is_fully_staffed())
    uncovered = len(schedule.shifts) - covered
    
    report.append(f"Total Shifts:      {len(schedule.shifts)}")
    report.append(f"Covered:           {covered} ({covered/len(schedule.shifts)*100:.1f}%)")
    report.append(f"Uncovered:         {uncovered}")
    report.append("")
    
    # Nurse satisfaction breakdown
    satisfaction = schedule.get_nurse_satisfaction()
    report.append("NURSE SATISFACTION BREAKDOWN")
    report.append("-" * 80)
    
    for nurse in schedule.nurses:
        sat = satisfaction.get(nurse.id, 0)
        report.append(f"{nurse.name:20s} {sat:.1%}")
    
    report.append("")
    
    # Footer
    report.append("=" * 80)
    report.append("Generated by AI-Enhanced Nurse Scheduler")
    report.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    
    return "\n".join(report)


if __name__ == "__main__":
    print("Visualization utilities loaded successfully")
