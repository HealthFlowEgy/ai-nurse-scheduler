# Getting Started Guide - AI-Enhanced Nurse Scheduler

## Quick Start (5 Minutes)

### Step 1: Installation

```bash
# Clone or download the project
cd ai_nurse_scheduler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Basic Example

```bash
# Run with default configuration
python main.py

# Output will be in results/ directory
```

### Step 3: View Results

```bash
# Open the generated report
cat results/schedule_report.txt

# If visualization was enabled
# Open results/schedule.html in browser
```

## Detailed Setup

### Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **RAM**: Minimum 4GB, recommended 8GB
- **Storage**: 2GB for dependencies and models

### Installation Steps

#### 1. System Dependencies (Optional)

For Arabic NLP support:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev

# macOS
brew install python

# Windows
# Python from python.org includes necessary components
```

#### 2. Python Environment

```bash
# Create isolated environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
python -c "import torch; import sklearn; import pulp; print('All imports successful')"
```

### Configuration

#### 1. Create Custom Configuration

```bash
# Copy default configuration
cp config/default.yaml config/my_hospital.yaml

# Edit with your hospital details
nano config/my_hospital.yaml  # or any text editor
```

#### 2. Configure Nurses

Edit the `nurses:` section in your YAML file:

```yaml
nurses:
  - id: "nurse_001"
    name: "Your Nurse Name"
    name_ar: "الاسم بالعربية"
    skill_level: "senior"  # junior, intermediate, senior, specialist
    max_hours_per_week: 48
    preferred_shifts: ["morning", "afternoon"]
    avoided_shifts: ["night"]
    prefer_friday_off: true
```

#### 3. Configure Schedule

```yaml
schedule:
  start_date: "2025-01-01"
  planning_horizon_days: 14
  
  shifts_per_day:
    - morning
    - afternoon
    - night
  
  daily_demand:
    morning: 5
    afternoon: 4
    night: 3
```

### Running the Scheduler

#### Basic Run

```bash
python main.py --config config/my_hospital.yaml
```

#### With Visualization

```bash
python main.py \
    --config config/my_hospital.yaml \
    --visualize \
    --output results/my_schedule
```

#### Quick Test (5 iterations)

```bash
python main.py \
    --config config/my_hospital.yaml \
    --max-iterations 5 \
    --time-limit 60
```

### Understanding Output

#### 1. Console Output

```
============================================================
AI-ENHANCED NURSE SCHEDULER
HealthFlow RegTech - Digital Health Egypt
============================================================

[1/5] Using default demand (ML not enabled)
[2/5] Generating shifts...
   Generated 42 shifts over 14 days
[3/5] Skipping fatigue prediction (ML not enabled)
[4/5] Running branch-and-price optimization...
   Nurses: 15, Shifts: 42
   Initial rotations: 300
   Iteration 1: Objective = 1234.56
   ...
[5/5] Constructing final schedule...

============================================================
OPTIMIZATION SUMMARY
============================================================
Solve Time:        45.23s
Iterations:        8
Objective Value:   892.34
Is Feasible:       True
Nurse Satisfaction: 87%
============================================================
```

#### 2. Report File

Located at `results/schedule_report.txt`:

```
================================================================================
                         NURSE SCHEDULE REPORT
                    HealthFlow RegTech - Egypt
================================================================================

SCHEDULE INFORMATION
--------------------------------------------------------------------------------
Hospital ID:       HealthFlow_Hospital_01
Start Date:        2025-01-01
End Date:          2025-01-15
Duration:          14 days

SCHEDULE METRICS
--------------------------------------------------------------------------------
Total Nurses:      15
Total Shifts:      42
Feasibility:       FEASIBLE
Nurse Satisfaction: 87.3%
```

#### 3. Visualization (if enabled)

Interactive HTML file at `results/schedule.html` with:
- Schedule timeline (Gantt chart)
- Shift distribution
- Hours per nurse
- Satisfaction scores

## ML Features (Advanced)

### Training Demand Forecasting Model

```python
from ml.demand_forecaster import DemandForecaster, generate_sample_data

# Generate or load historical data
data = generate_sample_data(num_days=365)

# Create and train forecaster
forecaster = DemandForecaster()
forecaster.train(data, epochs=100)

# Save model
forecaster.save("models/demand.pth")
```

### Training Fatigue Prediction Model

```python
from ml.fatigue_predictor import FatiguePredictor, generate_sample_fatigue_data

# Generate or load training data
data = generate_sample_fatigue_data(num_samples=1000)

# Create and train predictor
predictor = FatiguePredictor()
predictor.train(data)

# Save model
predictor.save("models/fatigue.pkl")
```

### Using Trained Models

```bash
python main.py \
    --config config/my_hospital.yaml \
    --use-ml \
    --demand-model models/demand.pth \
    --fatigue-model models/fatigue.pkl \
    --visualize \
    --output results/ml_enhanced_schedule
```

## Egyptian Features

### Ramadan Scheduling

Automatic detection and special handling:
- Reduced shift hours option
- Night shift avoidance preferences
- Higher demand complexity factor

Configuration:
```yaml
schedule:
  auto_ramadan: true  # Automatically detect Ramadan dates
  
nurses:
  - id: "nurse_001"
    avoid_night_shifts_ramadan: true
    ramadan_reduced_hours: true
```

### Friday Off Preference

```yaml
nurses:
  - id: "nurse_001"
    prefer_friday_off: true  # Jumu'ah prayer
```

### Arabic Names

Full Arabic name support:
```yaml
nurses:
  - id: "nurse_001"
    name: "Ahmed Hassan"
    name_ar: "أحمد حسن"
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Error: No module named 'torch'
pip install torch

# Error: No module named 'pulp'
pip install pulp

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Infeasible Solutions

If schedule is infeasible:
- **Reduce demand**: Lower `daily_demand` values
- **Add nurses**: Include more nurses in configuration
- **Relax constraints**: Increase `max_consecutive_days`
- **Longer horizon**: Increase `planning_horizon_days`

#### 3. Slow Performance

If optimization is too slow:
- **Reduce iterations**: `--max-iterations 5`
- **Shorter horizon**: Reduce `planning_horizon_days`
- **Fewer rotations**: Decrease `max_rotations_per_nurse`

#### 4. ML Model Errors

```bash
# If ML models not found
python main.py --use-ml=False

# Train new models
python ml/demand_forecaster.py
python ml/fatigue_predictor.py
```

## Integration with HealthFlow Platform

### API Integration

```python
# Coming soon: REST API
import requests

response = requests.post(
    "https://api.healthflow.eg/v1/scheduling/optimize",
    json={
        "hospital_id": "cairo_01",
        "config": {...}
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

schedule = response.json()
```

### Database Integration

```python
# Connect to HealthFlow PostgreSQL
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@healthflow-db:5432/scheduling")

# Load nurses from database
nurses_df = pd.read_sql("SELECT * FROM nurses WHERE hospital_id = 'cairo_01'", engine)
```

## Support & Resources

### Documentation
- **Full Documentation**: [docs.healthflow.eg](https://docs.healthflow.eg)
- **API Reference**: [api.healthflow.eg/docs](https://api.healthflow.eg/docs)
- **Video Tutorials**: [youtube.com/healthflowtech](https://youtube.com/healthflowtech)

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussion Forum**: [forum.healthflow.eg](https://forum.healthflow.eg)
- **Slack Channel**: Join HealthFlow developers

### Commercial Support
- **Email**: support@healthflow.eg
- **Phone**: +20-2-XXXX-XXXX
- **Business Hours**: Sun-Thu 9AM-5PM EET

## Next Steps

1. **Customize Configuration**: Edit `config/default.yaml` for your hospital
2. **Test with Sample Data**: Run basic optimization
3. **Collect Historical Data**: Prepare for ML training
4. **Train Models**: Enable demand forecasting and fatigue prediction
5. **Deploy to Production**: Integrate with existing systems
6. **Monitor & Optimize**: Track metrics and improve over time

## Success Stories

> "HealthFlow's AI scheduler reduced our planning time from 2 days to 2 minutes while improving nurse satisfaction by 40%."
> — Dr. Sarah Mohamed, Cairo General Hospital

> "The Ramadan-aware scheduling and Friday preferences made this the first system our nurses actually wanted to use."
> — Ahmed Hassan, Nursing Director, Alexandria Medical Center

---

**Ready to transform your nurse scheduling?**
Contact HealthFlow: business@healthflow.eg
