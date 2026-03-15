import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/services/api";
import { Plus, Save, Trash2, Upload, Pencil } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useRestaurant } from "@/restaurant-context";

const Menu = () => {
  const [menuItems, setMenuItems] = useState<any[]>([]);
  const [faqs, setFaqs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingFaqs, setSavingFaqs] = useState(false);
  const [uploadRestaurantId, setUploadRestaurantId] = useState("");
  const { toast } = useToast();
  const { selectedRestaurantId } = useRestaurant();

  useEffect(() => {
    setUploadRestaurantId(selectedRestaurantId);
  }, [selectedRestaurantId]);

  useEffect(() => {
    fetchData();
  }, [selectedRestaurantId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [menuData, faqsData] = await Promise.all([
        api.getMenu(selectedRestaurantId),
        api.getFaqs(selectedRestaurantId)
      ]);
      setMenuItems(menuData);
      setFaqs(faqsData);
    } catch (error) {
      console.error("Error fetching menu data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const targetRestaurantId = (uploadRestaurantId || "").trim() || selectedRestaurantId;

    try {
      const response = await api.uploadMenu(file, targetRestaurantId);
      toast({
        title: "Success",
        description: response.message || "Menu uploaded successfully",
      });
      // Clear the input value so the same file can be selected again if needed
      event.target.value = "";
      fetchData();
    } catch (error) {
      console.error("Upload error:", error);
      toast({
        title: "Error",
        description: "Failed to upload menu",
        variant: "destructive",
      });
    }
  };

  const toggleAvailability = async (id: string) => {
    const item = menuItems.find(i => i.id === id);
    if (!item) return;

    const newStatus = !item.available;

    // Optimistic update
    setMenuItems((items) =>
      items.map((item) =>
        item.id === id ? { ...item, available: newStatus } : item
      )
    );

    try {
      await api.updateItemAvailability(id, newStatus);
      toast({
        title: "Success",
        description: `Item marked as ${newStatus ? "available" : "unavailable"}`,
      });
    } catch (error) {
      console.error("Error updating availability:", error);
      // Revert on error
      setMenuItems((items) =>
        items.map((item) =>
          item.id === id ? { ...item, available: !newStatus } : item
        )
      );
      toast({
        title: "Error",
        description: "Failed to update item availability",
        variant: "destructive",
      });
    }
  };

  const updateFaqField = (faqId: string, field: "question" | "answer", value: string) => {
    setFaqs((prev) =>
      prev.map((faq) => (faq.id === faqId ? { ...faq, [field]: value } : faq))
    );
  };

  const handleSave = async () => {
    try {
      setSavingFaqs(true);
      await api.saveFaqs(faqs, selectedRestaurantId);
      toast({
        title: "Changes saved",
        description: "Your FAQs have been updated successfully.",
      });
      await fetchData();
    } catch (error) {
      console.error("Error saving FAQs:", error);
      toast({
        title: "Error",
        description: "Failed to save FAQs.",
        variant: "destructive",
      });
    } finally {
      setSavingFaqs(false);
    }
  };

  return (
    <DashboardLayout
      title="Menu & FAQs"
      subtitle="Manage your menu items and frequently asked questions for the AI."
    >
      <Tabs defaultValue="menu" className="space-y-6">
        <TabsList className="bg-muted p-1 rounded-xl">
          <TabsTrigger
            value="menu"
            className="rounded-lg data-[state=active]:bg-card data-[state=active]:shadow-soft"
          >
            Menu Items
          </TabsTrigger>
          <TabsTrigger
            value="faqs"
            className="rounded-lg data-[state=active]:bg-card data-[state=active]:shadow-soft"
          >
            FAQs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="menu" className="space-y-6">
          {/* Upload Section */}
          <div className="bg-card rounded-2xl border border-dashed border-primary/30 p-8 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center">
                <Upload className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Upload Menu CSV</p>
                <p className="text-sm text-muted-foreground">
                  Drag and drop or click to browse
                </p>
              </div>
              <div className="w-full max-w-sm text-left">
                <p className="text-xs text-muted-foreground mb-1">Restaurant ID for upload</p>
                <Input
                  value={uploadRestaurantId}
                  onChange={(e) => setUploadRestaurantId(e.target.value)}
                  placeholder="Enter restaurant_id"
                />
              </div>
              <div className="relative">
                <Input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <Button variant="outline" size="sm" disabled={loading}>
                  Choose File
                </Button>
              </div>
            </div>
          </div>

          {/* Menu Table */}
          <div className="bg-card rounded-2xl border shadow-card overflow-hidden">
            <div className="flex items-center justify-between p-5 border-b border-border">
              <h3 className="font-semibold text-foreground">Menu Items</h3>
              <Button size="sm">
                <Plus className="w-4 h-4" />
                Add Item
              </Button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-muted/50">
                    <th className="text-left px-5 py-4 text-sm font-semibold text-foreground">
                      Item Name
                    </th>
                    <th className="text-left px-5 py-4 text-sm font-semibold text-foreground">
                      Category
                    </th>
                    <th className="text-right px-5 py-4 text-sm font-semibold text-foreground">
                      Price
                    </th>
                    <th className="text-center px-5 py-4 text-sm font-semibold text-foreground">
                      Available
                    </th>
                    <th className="text-right px-5 py-4 text-sm font-semibold text-foreground">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="text-center py-10 text-muted-foreground">
                        Loading menu...
                      </td>
                    </tr>
                  ) : menuItems.map((item) => (
                    <tr
                      key={item.id}
                      className="hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-5 py-4">
                        <span className="font-medium text-foreground">
                          {item.name}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm text-muted-foreground">
                          {item.category}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-right">
                        <span className="font-semibold text-foreground">
                          ${item.price.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-center">
                        <Switch
                          checked={item.available}
                          onCheckedChange={() => toggleAvailability(item.id)}
                        />
                      </td>
                      <td className="px-5 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <Pencil className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:text-destructive">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {!loading && menuItems.length === 0 && (
                    <tr>
                      <td colSpan={5} className="text-center py-10 text-muted-foreground">
                        No menu items found for this restaurant.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="faqs" className="space-y-6">
          <div className="bg-card rounded-2xl border shadow-card">
            <div className="flex items-center justify-between p-5 border-b border-border">
              <h3 className="font-semibold text-foreground">
                Frequently Asked Questions
              </h3>
              <Button size="sm">
                <Plus className="w-4 h-4" />
                Add FAQ
              </Button>
            </div>
            <div className="divide-y divide-border">
              {faqs.map((faq) => (
                <div key={faq.id} className="p-5 space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-3">
                      <Input
                        value={faq.question || ""}
                        onChange={(e) => updateFaqField(faq.id, "question", e.target.value)}
                        className="font-medium"
                        placeholder="Question"
                      />
                      <Textarea
                        value={faq.answer || ""}
                        onChange={(e) => updateFaqField(faq.id, "answer", e.target.value)}
                        placeholder="Answer"
                        rows={2}
                      />
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive hover:text-destructive flex-shrink-0"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
              {!loading && faqs.length === 0 && (
                <div className="p-8 text-center text-sm text-muted-foreground">
                  No FAQs found for this restaurant.
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={handleSave} disabled={savingFaqs || loading}>
              <Save className="w-4 h-4" />
              {savingFaqs ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
};

export default Menu;
