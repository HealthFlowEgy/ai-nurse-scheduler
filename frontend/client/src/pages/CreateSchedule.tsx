import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { CalendarPlus, Loader2, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { api, type Nurse } from "@/lib/api";
import ConnectionStatus from "@/components/ConnectionStatus";

const SAMPLE_NURSES: Nurse[] = [
  {
    id: "N001",
    name: "Ahmed Mohamed",
    name_ar: "أحمد محمد",
    skill_level: "SENIOR",
    max_hours_per_week: 48
  },
  {
    id: "N002",
    name: "Fatima Hassan",
    name_ar: "فاطمة حسن",
    skill_level: "EXPERT",
    max_hours_per_week: 40
  },
  {
    id: "N003",
    name: "Omar Ali",
    name_ar: "عمر علي",
    skill_level: "INTERMEDIATE",
    max_hours_per_week: 48
  },
  {
    id: "N004",
    name: "Mariam Ibrahim",
    name_ar: "مريم إبراهيم",
    skill_level: "JUNIOR",
    max_hours_per_week: 44
  }
];

export default function CreateSchedule() {
  const [selectedNurses, setSelectedNurses] = useState<string[]>([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [department, setDepartment] = useState("General");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const toggleNurse = (nurseId: string) => {
    setSelectedNurses(prev =>
      prev.includes(nurseId)
        ? prev.filter(id => id !== nurseId)
        : [...prev, nurseId]
    );
  };

  const selectAll = () => {
    setSelectedNurses(SAMPLE_NURSES.map(n => n.id));
  };

  const deselectAll = () => {
    setSelectedNurses([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedNurses.length === 0) {
      toast.error("Please select at least one nurse");
      return;
    }

    if (!startDate || !endDate) {
      toast.error("Please select start and end dates");
      return;
    }

    if (new Date(startDate) >= new Date(endDate)) {
      toast.error("End date must be after start date");
      return;
    }

    setLoading(true);
    setSuccess(false);

    try {
      const selectedNurseData = SAMPLE_NURSES.filter(n => selectedNurses.includes(n.id));
      
      const response = await api.createSchedule({
        nurses: selectedNurseData,
        start_date: startDate,
        end_date: endDate,
        department
      });

      setSuccess(true);
      toast.success(response.message || "Schedule created successfully!");
      
      // Reset form after 2 seconds
      setTimeout(() => {
        setSelectedNurses([]);
        setStartDate("");
        setEndDate("");
        setDepartment("General");
        setSuccess(false);
      }, 2000);
    } catch (error) {
      toast.error("Failed to create schedule. Please try again.");
      console.error("Schedule creation error:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSkillBadgeColor = (level: string) => {
    switch (level) {
      case "EXPERT": return "bg-purple-100 text-purple-700";
      case "SENIOR": return "bg-blue-100 text-blue-700";
      case "INTERMEDIATE": return "bg-green-100 text-green-700";
      case "JUNIOR": return "bg-orange-100 text-orange-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold text-foreground">Create Schedule</h1>
          <ConnectionStatus />
        </div>
        <p className="text-muted-foreground">
          Generate an AI-optimized nurse schedule
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Schedule Details */}
        <Card>
          <CardHeader>
            <CardTitle>Schedule Details</CardTitle>
            <CardDescription>Set the time period and department</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start-date">Start Date *</Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end-date">End Date *</Label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="department">Department *</Label>
              <Select value={department} onValueChange={setDepartment}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="General">General</SelectItem>
                  <SelectItem value="ICU">ICU</SelectItem>
                  <SelectItem value="Emergency">Emergency</SelectItem>
                  <SelectItem value="Pediatrics">Pediatrics</SelectItem>
                  <SelectItem value="Surgery">Surgery</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Nurse Selection */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Select Nurses</CardTitle>
                <CardDescription>
                  Choose nurses to include in the schedule ({selectedNurses.length} selected)
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button type="button" variant="outline" size="sm" onClick={selectAll}>
                  Select All
                </Button>
                <Button type="button" variant="outline" size="sm" onClick={deselectAll}>
                  Deselect All
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {SAMPLE_NURSES.map((nurse) => (
                <div
                  key={nurse.id}
                  className={`flex items-start gap-3 p-4 rounded-lg border transition-colors cursor-pointer ${
                    selectedNurses.includes(nurse.id)
                      ? "border-primary bg-primary/5"
                      : "border-border hover:bg-accent/50"
                  }`}
                  onClick={() => toggleNurse(nurse.id)}
                >
                  <Checkbox
                    checked={selectedNurses.includes(nurse.id)}
                    onCheckedChange={() => toggleNurse(nurse.id)}
                  />
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{nurse.name}</div>
                    {nurse.name_ar && (
                      <div className="text-sm text-muted-foreground" dir="rtl">
                        {nurse.name_ar}
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`text-xs px-2 py-0.5 rounded ${getSkillBadgeColor(nurse.skill_level)}`}>
                        {nurse.skill_level}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {nurse.max_hours_per_week}h/week
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* AI Features Info */}
        <Card>
          <CardHeader>
            <CardTitle>AI Optimization Features</CardTitle>
            <CardDescription>
              Your schedule will be optimized using these AI capabilities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-sm">Branch-and-Price Optimization</div>
                  <div className="text-xs text-muted-foreground">
                    Advanced algorithm for optimal shift assignments
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-sm">Demand Forecasting</div>
                  <div className="text-xs text-muted-foreground">
                    LSTM-based patient flow prediction
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-sm">Fatigue Prediction</div>
                  <div className="text-xs text-muted-foreground">
                    XGBoost models for nurse well-being
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-sm">Labor Law Compliance</div>
                  <div className="text-xs text-muted-foreground">
                    Egyptian regulations (48h/week, 11h rest)
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-sm">Ramadan Awareness</div>
                  <div className="text-xs text-muted-foreground">
                    Special scheduling for Islamic calendar
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-sm">Preference Learning</div>
                  <div className="text-xs text-muted-foreground">
                    85%+ nurse satisfaction match rate
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className="flex gap-4">
          <Button
            type="submit"
            size="lg"
            disabled={loading || success}
            className="flex-1"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                Generating Schedule...
              </>
            ) : success ? (
              <>
                <CheckCircle2 className="h-5 w-5 mr-2" />
                Schedule Created!
              </>
            ) : (
              <>
                <CalendarPlus className="h-5 w-5 mr-2" />
                Generate Schedule
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
