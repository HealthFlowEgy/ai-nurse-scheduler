import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Plus, Edit, Trash2, User, FileDown, FileSpreadsheet } from "lucide-react";
import { toast } from "sonner";
import type { Nurse } from "@/lib/api";
import { useRealtimeNurses } from "@/hooks/useRealtimeNurses";
import { useWebSocket } from "@/hooks/useWebSocket";
import ConnectionStatus from "@/components/ConnectionStatus";
import { exportNursesToPDF, exportNursesToExcel } from "@/lib/export";
import { PermissionGuard } from "@/components/PermissionGuard";

const SKILL_LEVELS = ["JUNIOR", "INTERMEDIATE", "SENIOR", "EXPERT"] as const;

const INITIAL_NURSES: Nurse[] = [
  {
    id: "N001",
    name: "Ahmed Mohamed",
    name_ar: "أحمد محمد",
    skill_level: "SENIOR",
    max_hours_per_week: 48,
    preferences: {
      prefer_friday_off: true,
      max_consecutive_days: 5,
      max_night_shifts_per_week: 2
    }
  },
  {
    id: "N002",
    name: "Fatima Hassan",
    name_ar: "فاطمة حسن",
    skill_level: "EXPERT",
    max_hours_per_week: 40,
    preferences: {
      prefer_friday_off: true,
      avoid_night_shifts_ramadan: true,
      max_consecutive_days: 4
    }
  },
  {
    id: "N003",
    name: "Omar Ali",
    name_ar: "عمر علي",
    skill_level: "INTERMEDIATE",
    max_hours_per_week: 48,
    preferences: {
      max_consecutive_days: 6,
      max_night_shifts_per_week: 3
    }
  },
  {
    id: "N004",
    name: "Mariam Ibrahim",
    name_ar: "مريم إبراهيم",
    skill_level: "JUNIOR",
    max_hours_per_week: 44,
    preferences: {
      prefer_friday_off: true,
      max_consecutive_days: 5
    }
  }
];

export default function Nurses() {
  const [nurses, setNurses] = useState<Nurse[]>(INITIAL_NURSES);
  const { emit } = useWebSocket();
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [skillFilter, setSkillFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"name" | "skill" | "hours">("name");

  // Real-time updates
  const handleNurseCreated = useCallback((nurse: Nurse) => {
    setNurses(prev => [...prev, nurse]);
  }, []);

  const handleNurseUpdated = useCallback((nurse: Nurse) => {
    setNurses(prev => prev.map(n => n.id === nurse.id ? nurse : n));
  }, []);

  const handleNurseDeleted = useCallback((nurseId: string) => {
    setNurses(prev => prev.filter(n => n.id !== nurseId));
  }, []);

  useRealtimeNurses({
    onNurseCreated: handleNurseCreated,
    onNurseUpdated: handleNurseUpdated,
    onNurseDeleted: handleNurseDeleted,
    showToasts: true,
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingNurse, setEditingNurse] = useState<Nurse | null>(null);
  const [formData, setFormData] = useState<Partial<Nurse>>({
    name: "",
    name_ar: "",
    skill_level: "INTERMEDIATE",
    max_hours_per_week: 48,
  });

  const handleOpenDialog = (nurse?: Nurse) => {
    if (nurse) {
      setEditingNurse(nurse);
      setFormData(nurse);
    } else {
      setEditingNurse(null);
      setFormData({
        name: "",
        name_ar: "",
        skill_level: "INTERMEDIATE",
        max_hours_per_week: 48,
      });
    }
    setDialogOpen(true);
  };

  const handleSave = () => {
    if (!formData.name || !formData.skill_level) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (editingNurse) {
      // Update existing nurse
      const updatedNurse = { ...formData, id: editingNurse.id } as Nurse;
      setNurses(nurses.map(n => n.id === editingNurse.id ? updatedNurse : n));
      emit("nurse:updated", updatedNurse);
      toast.success("Nurse updated successfully");
    } else {
      // Add new nurse
      const newNurse: Nurse = {
        ...formData,
        id: `N${String(nurses.length + 1).padStart(3, '0')}`,
      } as Nurse;
      setNurses([...nurses, newNurse]);
      emit("nurse:created", newNurse);
      toast.success("Nurse added successfully");
    }

    setDialogOpen(false);
    setEditingNurse(null);
  };

  const handleDelete = (id: string) => {
    setNurses(nurses.filter(n => n.id !== id));
    emit("nurse:deleted", id);
    toast.success("Nurse deleted successfully");
  };

  // Filter and sort nurses
  const filteredNurses = nurses
    .filter(nurse => {
      const matchesSearch = searchTerm === "" || 
        nurse.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (nurse.name_ar && nurse.name_ar.includes(searchTerm));
      const matchesSkill = skillFilter === "all" || nurse.skill_level === skillFilter;
      return matchesSearch && matchesSkill;
    })
    .sort((a, b) => {
      if (sortBy === "name") return a.name.localeCompare(b.name);
      if (sortBy === "skill") return a.skill_level.localeCompare(b.skill_level);
      if (sortBy === "hours") return b.max_hours_per_week - a.max_hours_per_week;
      return 0;
    });

  const getSkillBadgeColor = (level: string) => {
    switch (level) {
      case "EXPERT": return "bg-purple-100 text-purple-700 border-purple-200";
      case "SENIOR": return "bg-blue-100 text-blue-700 border-blue-200";
      case "INTERMEDIATE": return "bg-green-100 text-green-700 border-green-200";
      case "JUNIOR": return "bg-orange-100 text-orange-700 border-orange-200";
      default: return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-foreground">Nurses</h1>
            <ConnectionStatus />
          </div>
          <p className="text-muted-foreground">
            Manage nursing staff and their preferences
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => exportNursesToPDF(nurses)}>
            <FileDown className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
          <Button variant="outline" onClick={() => exportNursesToExcel(nurses)}>
            <FileSpreadsheet className="h-4 w-4 mr-2" />
            Export Excel
          </Button>
          <PermissionGuard permission="create:nurse">
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => handleOpenDialog()}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Nurse
                </Button>
              </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>{editingNurse ? "Edit Nurse" : "Add New Nurse"}</DialogTitle>
              <DialogDescription>
                {editingNurse ? "Update nurse information" : "Add a new nurse to the system"}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Name (English) *</Label>
                <Input
                  id="name"
                  value={formData.name || ""}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Ahmed Mohamed"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="name_ar">Name (Arabic)</Label>
                <Input
                  id="name_ar"
                  value={formData.name_ar || ""}
                  onChange={(e) => setFormData({ ...formData, name_ar: e.target.value })}
                  placeholder="e.g., أحمد محمد"
                  dir="rtl"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="skill_level">Skill Level *</Label>
                <Select
                  value={formData.skill_level}
                  onValueChange={(value) => setFormData({ ...formData, skill_level: value as typeof SKILL_LEVELS[number] })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SKILL_LEVELS.map((level) => (
                      <SelectItem key={level} value={level}>
                        {level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="max_hours">Max Hours per Week *</Label>
                <Input
                  id="max_hours"
                  type="number"
                  min="20"
                  max="60"
                  value={formData.max_hours_per_week || 48}
                  onChange={(e) => setFormData({ ...formData, max_hours_per_week: parseInt(e.target.value) })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave}>
                {editingNurse ? "Update" : "Add"} Nurse
              </Button>
            </DialogFooter>
          </DialogContent>
            </Dialog>
          </PermissionGuard>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Nurses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{nurses.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Expert Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {nurses.filter(n => n.skill_level === "EXPERT").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Average Hours/Week
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {Math.round(nurses.reduce((sum, n) => sum + n.max_hours_per_week, 0) / nurses.length)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <Label htmlFor="search">Search Nurses</Label>
              <Input
                id="search"
                placeholder="Search by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="skill-filter">Skill Level</Label>
              <Select value={skillFilter} onValueChange={setSkillFilter}>
                <SelectTrigger id="skill-filter" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="JUNIOR">Junior</SelectItem>
                  <SelectItem value="INTERMEDIATE">Intermediate</SelectItem>
                  <SelectItem value="SENIOR">Senior</SelectItem>
                  <SelectItem value="EXPERT">Expert</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="sort-by">Sort By</Label>
              <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                <SelectTrigger id="sort-by" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="skill">Skill Level</SelectItem>
                  <SelectItem value="hours">Hours/Week</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Nurses Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredNurses.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <User className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-lg font-medium text-foreground">No nurses found</p>
            <p className="text-sm text-muted-foreground mt-1">Try adjusting your filters or search term</p>
          </div>
        ) : (
          filteredNurses.map((nurse) => (
          <Card key={nurse.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{nurse.name}</CardTitle>
                    {nurse.name_ar && (
                      <CardDescription dir="rtl" className="text-sm mt-1">
                        {nurse.name_ar}
                      </CardDescription>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">ID:</span>
                <span className="text-sm font-medium">{nurse.id}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Skill Level:</span>
                <Badge variant="outline" className={getSkillBadgeColor(nurse.skill_level)}>
                  {nurse.skill_level}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Max Hours/Week:</span>
                <span className="text-sm font-medium">{nurse.max_hours_per_week}h</span>
              </div>
              {nurse.preferences?.prefer_friday_off && (
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    Prefers Friday Off
                  </Badge>
                </div>
              )}
              <div className="flex gap-2 pt-2">
                <PermissionGuard permission="edit:nurse">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleOpenDialog(nurse)}
                  >
                    <Edit className="h-3 w-3 mr-1" />
                    Edit
                  </Button>
                </PermissionGuard>
                <PermissionGuard permission="delete:nurse">
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-destructive hover:text-destructive"
                    onClick={() => handleDelete(nurse.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </PermissionGuard>
              </div>
            </CardContent>
          </Card>
        ))
        )}
      </div>

      {/* Empty State */}
      {nurses.length === 0 && (
        <Card className="p-12">
          <div className="text-center">
            <User className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">No nurses yet</h3>
            <p className="text-muted-foreground mb-4">
              Get started by adding your first nurse to the system
            </p>
            <Button onClick={() => handleOpenDialog()}>
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Nurse
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
