import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Save, Mic, Clock, Shield, Volume2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Settings = () => {
  const [settings, setSettings] = useState({
    voiceType: "female-1",
    disclosureEnabled: true,
    fallbackTimeout: [120],
  });
  const [businessHours, setBusinessHours] = useState({
    monday: { open: "11:00", close: "22:00", enabled: true },
    tuesday: { open: "11:00", close: "22:00", enabled: true },
    wednesday: { open: "11:00", close: "22:00", enabled: true },
    thursday: { open: "11:00", close: "22:00", enabled: true },
    friday: { open: "11:00", close: "23:00", enabled: true },
    saturday: { open: "11:00", close: "23:00", enabled: true },
    sunday: { open: "12:00", close: "21:00", enabled: true },
  });
  const { toast } = useToast();

  const handleSave = () => {
    toast({
      title: "Settings saved",
      description: "Your changes have been applied successfully.",
    });
  };

  const days = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
  ] as const;

  return (
    <DashboardLayout
      title="Settings"
      subtitle="Configure your AI voice assistant behavior."
    >
      <div className="max-w-2xl space-y-6">
        {/* Voice Settings */}
        <div className="bg-card rounded-2xl border shadow-card p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Volume2 className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Voice Settings</h3>
              <p className="text-sm text-muted-foreground">
                Customize how your AI sounds
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label>AI Voice</Label>
              <Select
                value={settings.voiceType}
                onValueChange={(value) =>
                  setSettings({ ...settings, voiceType: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a voice" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="female-1">Sarah (Female, Warm)</SelectItem>
                  <SelectItem value="female-2">Emma (Female, Professional)</SelectItem>
                  <SelectItem value="male-1">James (Male, Friendly)</SelectItem>
                  <SelectItem value="male-2">David (Male, Calm)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-xl">
              <div className="flex items-center gap-3">
                <Shield className="w-5 h-5 text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">AI Disclosure</p>
                  <p className="text-sm text-muted-foreground">
                    "You're speaking with an AI assistant"
                  </p>
                </div>
              </div>
              <Switch
                checked={settings.disclosureEnabled}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, disclosureEnabled: checked })
                }
              />
            </div>
          </div>
        </div>

        {/* Fallback Settings */}
        <div className="bg-card rounded-2xl border shadow-card p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-warning/10 flex items-center justify-center">
              <Mic className="w-5 h-5 text-warning" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Human Fallback</h3>
              <p className="text-sm text-muted-foreground">
                When to transfer to staff
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <Label>
              Timeout before transfer:{" "}
              <span className="font-bold text-primary">
                {settings.fallbackTimeout[0]}s
              </span>
            </Label>
            <Slider
              value={settings.fallbackTimeout}
              onValueChange={(value) =>
                setSettings({ ...settings, fallbackTimeout: value })
              }
              min={30}
              max={300}
              step={10}
              className="py-4"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>30 seconds</span>
              <span>5 minutes</span>
            </div>
          </div>
        </div>

        {/* Business Hours */}
        <div className="bg-card rounded-2xl border shadow-card p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-success/10 flex items-center justify-center">
              <Clock className="w-5 h-5 text-success" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Business Hours</h3>
              <p className="text-sm text-muted-foreground">
                When the AI should answer calls
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {days.map((day) => (
              <div
                key={day}
                className="flex items-center justify-between p-3 rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Switch
                    checked={businessHours[day].enabled}
                    onCheckedChange={(checked) =>
                      setBusinessHours({
                        ...businessHours,
                        [day]: { ...businessHours[day], enabled: checked },
                      })
                    }
                  />
                  <span className="font-medium text-foreground capitalize w-24">
                    {day}
                  </span>
                </div>
                {businessHours[day].enabled && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span>{businessHours[day].open}</span>
                    <span>–</span>
                    <span>{businessHours[day].close}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button onClick={handleSave} size="lg">
            <Save className="w-4 h-4" />
            Save Settings
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
