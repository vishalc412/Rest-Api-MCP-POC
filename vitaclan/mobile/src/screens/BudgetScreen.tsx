import React from "react";
import { View, StyleSheet, ScrollView, Dimensions } from "react-native";
import { Card, Text, ActivityIndicator } from "react-native-paper";
import { PieChart } from "react-native-chart-kit";
import { useExpenseSummary } from "../api/hooks";

const CATEGORY_COLORS: Record<string, string> = {
  doctor_fee: "#4CAF50",
  lab_test: "#2196F3",
  medicine: "#FF9800",
  other: "#9C27B0",
};

const CATEGORY_LABELS: Record<string, string> = {
  doctor_fee: "Doctor Fees",
  lab_test: "Lab Tests",
  medicine: "Medicines",
  other: "Other",
};

export default function BudgetScreen() {
  const now = new Date();
  const { data, isLoading } = useExpenseSummary(now.getFullYear(), now.getMonth() + 1);

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator /></View>;
  }

  const breakdown = data?.breakdown || [];
  const total = data?.grand_total || 0;

  const chartData = breakdown.map((b: any) => ({
    name: CATEGORY_LABELS[b.category] || b.category,
    amount: b.total,
    color: CATEGORY_COLORS[b.category] || "#757575",
    legendFontColor: "#374151",
    legendFontSize: 12,
  }));

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Card style={styles.totalCard}>
        <Card.Content>
          <Text variant="labelLarge" style={styles.dim}>This Month</Text>
          <Text variant="displaySmall" style={styles.total}>
            ₹{total.toLocaleString("en-IN")}
          </Text>
          <Text variant="bodySmall" style={styles.dim}>
            {breakdown.reduce((s: number, b: any) => s + b.count, 0)} transactions
          </Text>
        </Card.Content>
      </Card>

      {chartData.length > 0 ? (
        <Card style={styles.card}>
          <Card.Title title="Spending Breakdown" />
          <Card.Content>
            <PieChart
              data={chartData}
              width={Dimensions.get("window").width - 60}
              height={200}
              chartConfig={{ color: () => "#000" }}
              accessor="amount"
              backgroundColor="transparent"
              paddingLeft="12"
            />
          </Card.Content>
        </Card>
      ) : (
        <Text style={styles.empty}>
          No expenses recorded this month. Scan a bill to track.
        </Text>
      )}

      {breakdown.map((b: any) => (
        <Card key={b.category} style={styles.card}>
          <Card.Content style={styles.row}>
            <View style={[styles.colorDot, { backgroundColor: CATEGORY_COLORS[b.category] }]} />
            <View style={{ flex: 1 }}>
              <Text variant="titleSmall">{CATEGORY_LABELS[b.category] || b.category}</Text>
              <Text variant="bodySmall" style={styles.dim}>{b.count} items</Text>
            </View>
            <Text variant="titleMedium" style={styles.amount}>
              ₹{b.total.toLocaleString("en-IN")}
            </Text>
          </Card.Content>
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fa" },
  content: { padding: 12 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  totalCard: { marginBottom: 12, backgroundColor: "#1a1a2e" },
  total: { color: "white", fontWeight: "700", marginVertical: 6 },
  card: { marginBottom: 10 },
  row: { flexDirection: "row", alignItems: "center" },
  colorDot: { width: 16, height: 16, borderRadius: 8, marginRight: 12 },
  amount: { fontWeight: "600" },
  dim: { color: "#9ca3af" },
  empty: { textAlign: "center", padding: 40, color: "#9ca3af" },
});
