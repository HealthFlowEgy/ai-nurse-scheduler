import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, FileDown, FileSpreadsheet } from "lucide-react";
import ConnectionStatus from "@/components/ConnectionStatus";
import { exportScheduleToPDF, exportScheduleToExcel } from "@/lib/export";

type ShiftType = "morning" | "evening" | "night" | "off";

interface Shift {
  date: string;
  nurse: string;
  nurseAr?: string;
  type: ShiftType;
  hours: number;
}

// Sample schedule data
const SAMPLE_SHIFTS: Shift[] = [
  { date: "2025-12-01", nurse: "Ahmed Mohamed", nurseAr: "أحمد محمد", type: "morning", hours: 8 },
  { date: "2025-12-01", nurse: "Fatima Hassan", nurseAr: "فاطمة حسن", type: "evening", hours: 8 },
  { date: "2025-12-01", nurse: "Omar Ali", nurseAr: "عمر علي", type: "night", hours: 8 },
  { date: "2025-12-02", nurse: "Mariam Ibrahim", nurseAr: "مريم إبراهيم", type: "morning", hours: 8 },
  { date: "2025-12-02", nurse: "Ahmed Mohamed", nurseAr: "أحمد محمد", type: "evening", hours: 8 },
  { date: "2025-12-02", nurse: "Fatima Hassan", nurseAr: "فاطمة حسن", type: "night", hours: 8 },
  { date: "2025-12-03", nurse: "Omar Ali", nurseAr: "عمر علي", type: "morning", hours: 8 },
  { date: "2025-12-03", nurse: "Mariam Ibrahim", nurseAr: "مريم إبراهيم", type: "evening", hours: 8 },
  { date: "2025-12-03", nurse: "Ahmed Mohamed", nurseAr: "أحمد محمد", type: "night", hours: 8 },
  { date: "2025-12-04", nurse: "Fatima Hassan", nurseAr: "فاطمة حسن", type: "morning", hours: 8 },
  { date: "2025-12-04", nurse: "Omar Ali", nurseAr: "عمر علي", type: "evening", hours: 8 },
  { date: "2025-12-04", nurse: "Mariam Ibrahim", nurseAr: "مريم إبراهيم", type: "night", hours: 8 },
  { date: "2025-12-05", nurse: "Ahmed Mohamed", nurseAr: "أحمد محمد", type: "morning", hours: 8 },
  { date: "2025-12-05", nurse: "Fatima Hassan", nurseAr: "فاطمة حسن", type: "evening", hours: 8 },
  { date: "2025-12-05", nurse: "Omar Ali", nurseAr: "عمر علي", type: "night", hours: 8 },
  { date: "2025-12-06", nurse: "Mariam Ibrahim", nurseAr: "مريم إبراهيم", type: "off", hours: 0 },
  { date: "2025-12-06", nurse: "Ahmed Mohamed", nurseAr: "أحمد محمد", type: "morning", hours: 8 },
  { date: "2025-12-06", nurse: "Fatima Hassan", nurseAr: "فاطمة حسن", type: "evening", hours: 8 },
];

export default function Schedules() {
  const [currentDate, setCurrentDate] = useState(new Date(2025, 11, 1)); // December 2025
  const [selectedSchedule, setSelectedSchedule] = useState<string>("1");

  // Create a map of shifts by date
  const mockShifts: Record<string, Shift> = {};
  SAMPLE_SHIFTS.forEach(shift => {
    if (!mockShifts[shift.date]) {
      mockShifts[shift.date] = shift;
    }
  });

  const handleExportPDF = () => {
    const schedule = schedules.find(s => s.id === selectedSchedule);
    if (schedule) {
      const shifts = generateShiftsData();
      exportScheduleToPDF(schedule, shifts);
    }
  };

  const handleExportExcel = () => {
    const schedule = schedules.find(s => s.id === selectedSchedule);
    if (schedule) {
      const shifts = generateShiftsData();
      exportScheduleToExcel(schedule, shifts);
    }
  };

  const generateShiftsData = () => {
    const shifts: any[] = [];
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const shift = mockShifts[dateStr];
      
      shifts.push({
        date: dateStr,
        nurse_name: shift?.nurse || "-",
        shift_type: shift?.type || "off",
        hours: shift?.type === "morning" ? "8" : shift?.type === "evening" ? "8" : shift?.type === "night" ? "12" : "0",
      });
    }
    
    return shifts;
  };

  const schedules = [
    { id: "1", name: "December 2025", status: "active", period: "Dec 1-31, 2025", start_date: "2025-12-01", end_date: "2025-12-31", department: "General" },
    { id: "2", name: "November 2025", status: "completed", period: "Nov 1-30, 2025", start_date: "2025-11-01", end_date: "2025-11-30", department: "General" },
    { id: "3", name: "October 2025", status: "completed", period: "Oct 1-31, 2025", start_date: "2025-10-01", end_date: "2025-10-31", department: "General" },
  ];

  const getShiftColor = (type: ShiftType) => {
    switch (type) {
      case "morning": return "bg-blue-100 text-blue-700 border-blue-200";
      case "evening": return "bg-orange-100 text-orange-700 border-orange-200";
      case "night": return "bg-purple-100 text-purple-700 border-purple-200";
      case "off": return "bg-gray-100 text-gray-500 border-gray-200";
    }
  };

  const getShiftIcon = (type: ShiftType) => {
    switch (type) {
      case "morning": return "☀️";
      case "evening": return "🌅";
      case "night": return "🌙";
      case "off": return "🏖️";
    }
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    return { daysInMonth, startingDayOfWeek, year, month };
  };

  const { daysInMonth, startingDayOfWeek, year, month } = getDaysInMonth(currentDate);

  const getShiftsForDate = (day: number) => {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return SAMPLE_SHIFTS.filter(shift => shift.date === dateStr);
  };

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <>
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold text-foreground">Schedules</h1>
          <ConnectionStatus />
        </div>
        <p className="text-muted-foreground">
          View and manage nurse schedules
        </p>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" onClick={handleExportPDF}>
          <FileDown className="h-4 w-4 mr-2" />
          Export PDF
        </Button>
        <Button variant="outline" onClick={handleExportExcel}>
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          Export Excel
        </Button>
      </div>
    </div>

    <div className="space-y-6">

      {/* Schedule Selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {schedules.map((schedule) => (
          <Card
            key={schedule.id}
            className={`cursor-pointer transition-all ${
              selectedSchedule === schedule.name
                ? "ring-2 ring-primary"
                : "hover:shadow-md"
            }`}
            onClick={() => setSelectedSchedule(schedule.name)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{schedule.name}</CardTitle>
                <Badge
                  variant="outline"
                  className={
                    schedule.status === "active"
                      ? "bg-green-100 text-green-700 border-green-200"
                      : "bg-gray-100 text-gray-700 border-gray-200"
                  }
                >
                  {schedule.status}
                </Badge>
              </div>
              <CardDescription>{schedule.period}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>

      {/* Calendar View */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5" />
              {monthNames[month]} {year}
            </CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={previousMonth}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={nextMonth}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-2">
            {/* Day Headers */}
            {dayNames.map((day) => (
              <div
                key={day}
                className="text-center font-semibold text-sm text-muted-foreground py-2"
              >
                {day}
              </div>
            ))}

            {/* Empty cells for days before month starts */}
            {Array.from({ length: startingDayOfWeek }).map((_, index) => (
              <div key={`empty-${index}`} className="min-h-[120px]" />
            ))}

            {/* Calendar days */}
            {Array.from({ length: daysInMonth }).map((_, index) => {
              const day = index + 1;
              const shifts = getShiftsForDate(day);
              const isFriday = (startingDayOfWeek + index) % 7 === 5;

              return (
                <div
                  key={day}
                  className={`min-h-[120px] p-2 border rounded-lg ${
                    isFriday ? "bg-accent/5" : "bg-card"
                  }`}
                >
                  <div className="text-sm font-semibold text-foreground mb-2">
                    {day}
                    {isFriday && <span className="text-xs ml-1 text-accent">🕌</span>}
                  </div>
                  <div className="space-y-1">
                    {shifts.map((shift, idx) => (
                      <div
                        key={idx}
                        className={`text-xs p-1.5 rounded border ${getShiftColor(shift.type)}`}
                      >
                        <div className="flex items-center gap-1">
                          <span>{getShiftIcon(shift.type)}</span>
                          <span className="font-medium truncate">{shift.nurse}</span>
                        </div>
                        <div className="text-[10px] opacity-75 mt-0.5">
                          {shift.type} {shift.hours > 0 && `(${shift.hours}h)`}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Shift Legend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded border ${getShiftColor("morning")}`} />
              <span className="text-sm">☀️ Morning (6AM-2PM)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded border ${getShiftColor("evening")}`} />
              <span className="text-sm">🌅 Evening (2PM-10PM)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded border ${getShiftColor("night")}`} />
              <span className="text-sm">🌙 Night (10PM-6AM)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded border ${getShiftColor("off")}`} />
              <span className="text-sm">🏖️ Off Day</span>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
            <span className="text-accent">🕌</span>
            <span>Friday - Jumu'ah Prayer Day</span>
          </div>
        </CardContent>
      </Card>
    </div>
    </>
  );
}
