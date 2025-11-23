# Quick Reference Card

## 🚀 Common Commands

### Basic Usage
```bash
# Run with defaults
python main.py

# With custom config
python main.py --config config/my_hospital.yaml

# With visualization
python main.py --visualize --output results/schedule

# Quick test (5 minutes)
python main.py --max-iterations 5 --time-limit 60
```

### With ML Features
```bash
# Enable ML
python main.py --use-ml \
    --demand-model models/demand.pth \
    --fatigue-model models/fatigue.pkl

# Train demand forecaster
python ml/demand_forecaster.py

# Train fatigue predictor
python ml/fatigue_predictor.py
```

## 📋 Configuration Essentials

### Hospital Settings
```yaml
hospital:
  name: "Your Hospital"
  location: "Cairo, Egypt"
  department: "General Ward"
```

### Schedule Parameters
```yaml
schedule:
  start_date: "2025-01-01"
  planning_horizon_days: 14
  shifts_per_day: [morning, afternoon, night]
  daily_demand:
    morning: 5
    afternoon: 4
    night: 3
```

### Nurse Definition
```yaml
nurses:
  - id: "nurse_001"
    name: "Ahmed Hassan"
    name_ar: "أحمد حسن"
    skill_level: senior
    max_hours_per_week: 48
    preferred_shifts: [morning]
    prefer_friday_off: true
```

## 🔧 Key Classes

### Core Models
```python
from core.models import Nurse, Shift, Rotation, Schedule, SchedulingProblem

# Create a nurse
nurse = Nurse(
    id="n001",
    name="Ahmed",
    skill_level=SkillLevel.SENIOR,
    max_hours_per_week=48
)

# Create a problem
problem = SchedulingProblem(
    nurses=[nurse1, nurse2, ...],
    planning_horizon_days=14,
    start_date=datetime.now(),
    daily_demand={ShiftType.MORNING: 5}
)
```

### Optimizer
```python
from core.optimizer import AIEnhancedOptimizer

# Create optimizer
optimizer = AIEnhancedOptimizer(use_ml=True)
optimizer.setup_egyptian_constraints()

# Optimize
schedule = optimizer.optimize(problem, max_iterations=10)
```

## 📊 Output Files

```
results/
├── schedule_report.txt      # Text report
├── schedule.html           # Interactive visualization (if --visualize)
└── schedule_data.json      # Raw data (optional)
```

## 🐛 Troubleshooting

### Problem: Infeasible solution
**Solution**: Reduce demand or add more nurses
```yaml
daily_demand:
  morning: 3  # Reduced from 5
  afternoon: 3
  night: 2
```

### Problem: Too slow
**Solution**: Reduce iterations or horizon
```bash
python main.py --max-iterations 5 --time-limit 60
```

### Problem: Import errors
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## 📈 Performance Tuning

### For Speed
- Reduce `max_iterations` (5-10)
- Shorter `planning_horizon_days` (7-14)
- Fewer `max_rotations_per_nurse` (20-30)

### For Quality
- Increase `max_iterations` (15-20)
- Longer `time_limit` (600-900 seconds)
- Enable ML features

## 🇪🇬 Egyptian Features

### Ramadan
```yaml
schedule:
  auto_ramadan: true

nurses:
  - avoid_night_shifts_ramadan: true
    ramadan_reduced_hours: true
```

### Friday Off
```yaml
nurses:
  - prefer_friday_off: true  # Jumu'ah
```

### Arabic Names
```yaml
nurses:
  - name: "Ahmed Hassan"
    name_ar: "أحمد حسن"
```

## 🔗 Key Metrics

### Schedule Quality
- **Feasibility**: All hard constraints satisfied?
- **Cost**: Lower is better (penalties + violations)
- **Satisfaction**: % of preferences matched (target: >85%)
- **Coverage**: % of shifts fully staffed (target: >95%)

### Performance
- **Solve Time**: Seconds to optimize (target: <300s)
- **Iterations**: Column generation rounds (typical: 5-15)
- **Gap**: Distance from optimal (target: <10%)

## 📞 Quick Links

- Documentation: `GETTING_STARTED.md`
- Architecture: `PROJECT_STRUCTURE.md`
- Summary: `IMPLEMENTATION_SUMMARY.md`
- Issues: GitHub Issues
- Support: support@healthflow.eg

## 💡 Pro Tips

1. **Start Small**: Test with 5-10 nurses, 7 days
2. **Incremental**: Add complexity gradually
3. **Monitor**: Check logs for warnings
4. **Visualize**: Always enable `--visualize`
5. **Iterate**: Adjust config based on results

## ⚡ One-Liners

```bash
# Quick test
python main.py --max-iterations 3 --time-limit 30

# Production run with all features
python main.py --use-ml --visualize --output results/prod_schedule

# Train all ML models
python ml/demand_forecaster.py && python ml/fatigue_predictor.py

# Generate sample config
python main.py --config config/default.yaml

# Check installation
python -c "import torch, sklearn, pulp; print('✅ All imports OK')"
```

---
**Quick Reference v1.0** | HealthFlow RegTech | 2025
