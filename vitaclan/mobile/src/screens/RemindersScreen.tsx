import React from "react";
import { View, StyleSheet, FlatList } from "react-native";
import { Card, Text, Chip, Switch, ActivityIndicator } from "react-native-paper";
import { useMedications, useReminders } from "../api/hooks";

export default function RemindersScreen() {
  const { data: medications, isLoading: medsLoading } = useMedications();
  const { data: reminders, isLoading: remLoading } = useReminders();

  if (medsLoading || remLoading) {
    return <View style={styles.center}><ActivityIndicator /></View>;
  }

  return (
    <View style={styles.container}>
      <Text variant="titleMedium" style={styles.section}>Active Medications</Text>
      <FlatList
        data={medications || []}
        keyExtractor={(item: any) => item.id}
        ListEmptyComponent={
          <Text style={styles.empty}>No active medications. Scan a prescription to add.</Text>
        }
        renderItem={({ item }: any) => {
          const reminderList = (reminders || []).filter((r: any) => r.medication_id === item.id);
          return (
            <Card style={styles.card}>
              <Card.Content>
                <Text variant="titleMedium">{item.name}</Text>
                <Text variant="bodyMedium" style={styles.dim}>
                  {item.dosage} • {item.frequency}
                </Text>
                {item.instructions && (
                  <Text variant="bodySmall" style={styles.instructions}>
                    {item.instructions}
                  </Text>
                )}
                <View style={styles.reminderRow}>
                  {reminderList.length > 0 ? (
                    reminderList.map((r: any) => (
                      <Chip key={r.id} icon="bell" compact style={styles.reminderChip}>
                        {r.schedule_time.slice(0, 5)}
                      </Chip>
                    ))
                  ) : (
                    <Text variant="bodySmall" style={styles.dim}>
                      No reminders set
                    </Text>
                  )}
                </View>
              </Card.Content>
            </Card>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 12 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  section: { marginBottom: 8, fontWeight: "600" },
  card: { marginBottom: 10 },
  dim: { color: "#6b7280" },
  instructions: { marginTop: 4, fontStyle: "italic" },
  reminderRow: { flexDirection: "row", flexWrap: "wrap", marginTop: 10, gap: 6 },
  reminderChip: { marginRight: 6 },
  empty: { color: "#9ca3af", textAlign: "center", padding: 20 },
});
