import React from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import { Card, Text, Chip, Divider, ActivityIndicator, Banner } from "react-native-paper";
import { useDocumentSummary } from "../api/hooks";

export default function DocumentDetailScreen({ route }: any) {
  const { docId } = route.params;
  const { data, isLoading } = useDocumentSummary(docId, true);

  if (isLoading) {
    return <View style={styles.center}><ActivityIndicator size="large" /></View>;
  }

  if (!data || data.status === "pending" || data.status === "processing") {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text style={{ marginTop: 12 }}>Document is being processed...</Text>
      </View>
    );
  }

  const structured = data.structured_data || {};
  const medicines = structured.medicines || [];
  const tests = structured.tests || [];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Banner visible icon="alert-circle">
        AI summary below is for educational purposes only. Always consult your doctor.
      </Banner>

      <Card style={styles.card}>
        <Card.Title title="AI Summary" subtitle={`Confidence: ${Math.round((data.confidence || 0) * 100)}%`} />
        <Card.Content>
          <Text>{data.summary}</Text>
          {data.sources && data.sources.length > 0 && (
            <View style={styles.sources}>
              <Text variant="labelSmall">Sources:</Text>
              {data.sources.map((s: string, i: number) => (
                <Chip key={i} compact style={styles.sourceChip}>{s}</Chip>
              ))}
            </View>
          )}
        </Card.Content>
      </Card>

      {medicines.length > 0 && (
        <Card style={styles.card}>
          <Card.Title title="💊 Medicines" />
          <Card.Content>
            {medicines.map((m: any, i: number) => (
              <View key={i} style={styles.medItem}>
                <Text variant="titleSmall">{m.name}</Text>
                <Text variant="bodySmall" style={styles.dim}>
                  {m.dosage} • {m.frequency}
                </Text>
                {m.instructions && <Text variant="bodySmall">{m.instructions}</Text>}
                {i < medicines.length - 1 && <Divider style={styles.divider} />}
              </View>
            ))}
          </Card.Content>
        </Card>
      )}

      {tests.length > 0 && (
        <Card style={styles.card}>
          <Card.Title title="🧪 Test Results" />
          <Card.Content>
            {tests.map((t: any, i: number) => (
              <View key={i} style={styles.testRow}>
                <View style={styles.testInfo}>
                  <Text variant="titleSmall">{t.name}</Text>
                  <Text variant="bodySmall" style={styles.dim}>
                    Normal: {t.normal_range || "N/A"}
                  </Text>
                </View>
                <Chip mode="outlined" compact>
                  {t.result} {t.unit}
                </Chip>
              </View>
            ))}
          </Card.Content>
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fa" },
  content: { padding: 12 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  card: { marginBottom: 12 },
  medItem: { paddingVertical: 8 },
  dim: { color: "#6b7280" },
  divider: { marginTop: 8 },
  testRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 8 },
  testInfo: { flex: 1 },
  sources: { flexDirection: "row", flexWrap: "wrap", marginTop: 12, gap: 6 },
  sourceChip: { marginRight: 6 },
});
