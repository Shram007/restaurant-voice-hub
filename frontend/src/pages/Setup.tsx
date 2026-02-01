import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Check, ArrowRight, ArrowLeft, Upload, Link as LinkIcon } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";

const posProviders = [
  { id: "square", name: "Square", logo: "⬛" },
  { id: "clover", name: "Clover", logo: "🍀" },
  { id: "shift4", name: "Shift4", logo: "💳" },
];

const Setup = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedPOS, setSelectedPOS] = useState<string | null>(null);
  const [settings, setSettings] = useState({
    defaultPickupTime: "20",
    maxOrdersPerSlot: "10",
    enableFallback: true,
  });
  const { toast } = useToast();

  const steps = [
    { number: 1, title: "Connect POS" },
    { number: 2, title: "Upload Menu" },
    { number: 3, title: "Business Rules" },
  ];

  const handleComplete = async () => {
    try {
      await api.setupRestaurant({
        name: "My Restaurant",
        business_rules: JSON.stringify(settings),
      });
      toast({
        title: "Setup complete!",
        description: "Your AI voice assistant is ready to take orders.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save setup data.",
        variant: "destructive",
      });
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      await api.uploadMenu(file);
      toast({
        title: "Success",
        description: "Menu uploaded successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to upload menu",
        variant: "destructive",
      });
    }
  };

  return (
    <DashboardLayout
      title="Setup Wizard"
      subtitle="Get your AI voice assistant up and running in minutes."
    >
      <div className="max-w-3xl mx-auto space-y-8">
        {/* Progress Steps */}
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all",
                    currentStep > step.number
                      ? "bg-success text-success-foreground"
                      : currentStep === step.number
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                  )}
                >
                  {currentStep > step.number ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    step.number
                  )}
                </div>
                <span
                  className={cn(
                    "font-medium hidden sm:block",
                    currentStep >= step.number
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {step.title}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    "w-12 md:w-24 h-0.5 mx-4",
                    currentStep > step.number ? "bg-success" : "bg-muted"
                  )}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="bg-card rounded-2xl border shadow-card p-6 md:p-8 animate-slide-up">
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto">
                  <LinkIcon className="w-7 h-7 text-primary" />
                </div>
                <h2 className="text-xl font-semibold text-foreground">
                  Connect Your POS System
                </h2>
                <p className="text-muted-foreground">
                  Link your point-of-sale to automatically sync orders.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {posProviders.map((provider) => (
                  <button
                    key={provider.id}
                    onClick={() => setSelectedPOS(provider.id)}
                    className={cn(
                      "p-6 rounded-xl border-2 transition-all hover:border-primary/50",
                      selectedPOS === provider.id
                        ? "border-primary bg-primary/5"
                        : "border-border"
                    )}
                  >
                    <div className="text-4xl mb-3">{provider.logo}</div>
                    <p className="font-semibold text-foreground">{provider.name}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {selectedPOS === provider.id ? "Connected" : "Click to connect"}
                    </p>
                  </button>

                ))}
              </div>

              {selectedPOS && (
                <div className="bg-muted p-4 rounded-xl animate-fade-in space-y-3">
                  <Label>
                    Enter your {posProviders.find(p => p.id === selectedPOS)?.name} API Key
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="pos-api-key"
                      type="password"
                      placeholder="sk_test_..."
                      className="font-mono bg-background"
                    />
                    <Button onClick={async () => {
                      const apiKey = (document.getElementById('pos-api-key') as HTMLInputElement)?.value;
                      if (!apiKey) {
                        toast({ title: "Error", description: "Please enter an API key", variant: "destructive" });
                        return;
                      }
                      try {
                        const result = await api.connectPOS(selectedPOS!, apiKey);
                        if (result.success) {
                          toast({ title: "Connected", description: result.message });
                        } else {
                          toast({ title: "Connection Failed", description: result.message, variant: "destructive" });
                        }
                      } catch (error) {
                        toast({ title: "Error", description: "Failed to connect to POS service", variant: "destructive" });
                      }
                    }}>
                      Connect
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    This allows us to sync menu items and push orders directly to your POS.
                  </p>
                </div>
              )}
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto">
                  <Upload className="w-7 h-7 text-primary" />
                </div>
                <h2 className="text-xl font-semibold text-foreground">
                  Upload Menu, Ingredients & FAQs
                </h2>
                <p className="text-muted-foreground">
                  Help your AI understand your full menu including ingredients for allergy checks.
                </p>
              </div>

              <div className="relative border-2 border-dashed border-primary/30 rounded-xl p-8 text-center hover:border-primary/50 transition-colors cursor-pointer">
                <Input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <Upload className="w-10 h-10 mx-auto text-primary/50 mb-4" />
                <p className="font-medium text-foreground">
                  Drop your menu CSV here
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  or click to browse files
                </p>
                <Button variant="outline" size="sm" className="mt-4">
                  Choose File
                </Button>
              </div>

              <div className="bg-muted/50 rounded-xl p-4">
                <p className="text-sm font-medium text-foreground mb-2">
                  Preview
                </p>
                <div className="text-sm text-muted-foreground">
                  No file uploaded yet. Upload a CSV with columns: name, category, price, description, ingredients.
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <h2 className="text-xl font-semibold text-foreground">
                  Configure Business Rules
                </h2>
                <p className="text-muted-foreground">
                  Set default behaviors for your AI assistant.
                </p>
              </div>

              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="pickupTime">Default Pickup Time (minutes)</Label>
                  <Input
                    id="pickupTime"
                    type="number"
                    value={settings.defaultPickupTime}
                    onChange={(e) =>
                      setSettings({ ...settings, defaultPickupTime: e.target.value })
                    }
                  />
                  <p className="text-xs text-muted-foreground">
                    How long before orders are ready for pickup
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="maxOrders">Max Orders Per Time Slot</Label>
                  <Input
                    id="maxOrders"
                    type="number"
                    value={settings.maxOrdersPerSlot}
                    onChange={(e) =>
                      setSettings({ ...settings, maxOrdersPerSlot: e.target.value })
                    }
                  />
                  <p className="text-xs text-muted-foreground">
                    Limit orders to prevent kitchen overload
                  </p>
                </div>

                <div className="flex items-center justify-between p-4 bg-muted/50 rounded-xl">
                  <div>
                    <p className="font-medium text-foreground">
                      Enable Human Fallback
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Transfer complex calls to staff
                    </p>
                  </div>
                  <Switch
                    checked={settings.enableFallback}
                    onCheckedChange={(checked) =>
                      setSettings({ ...settings, enableFallback: checked })
                    }
                  />
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between pt-6 mt-6 border-t border-border">
            <Button
              variant="outline"
              onClick={() => setCurrentStep(currentStep - 1)}
              disabled={currentStep === 1}
            >
              <ArrowLeft className="w-4 h-4" />
              Previous
            </Button>

            {currentStep < 3 ? (
              <Button onClick={() => setCurrentStep(currentStep + 1)}>
                Next Step
                <ArrowRight className="w-4 h-4" />
              </Button>
            ) : (
              <Button onClick={handleComplete}>
                Complete Setup
                <Check className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout >
  );
};

export default Setup;
