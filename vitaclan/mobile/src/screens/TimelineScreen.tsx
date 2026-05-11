import React from "react";
import { View, StyleSheet, FlatList, RefreshControl, TouchableOpacity } from "react-native";
import { Card, Text, Chip, ActivityIndicator } from "react-native-paper";
import { format } from "date-fns";
import { useDocuments } from "../api/hooks";

const TYPE_COLORS: Record<string, string> = {
  prescription: "#4CAF50",
  lab_report: "#2196F3",
  bill: "#FF9800",
  doctor_note: "#9C27B0",
  other: "#757575",
};

export default function TimelineScreen({ navigation }: any) {
  const { data: documents, isLoading, refetch, isFetching } = useDocuments();

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <FlatList
      data={documents || []}
      keyExtractor={(item: any) => item.id}
      contentContainerStyle={styles.list}
      refreshControl={<RefreshControl refreshing={isFetching} onRefresh={refetch} />}
      ListEmptyComponent={
        <View style={styles.empty}>
          <Text variant="titleMedium">No records yet</Text>
          <Text variant="bodySmall" style={styles.emptyHint}>
            Tap the camera button to scan your first prescription or lab report
          </Text>
        </View>
      }
      renderItem={({ item }: any) => (
        <TouchableOpacity onPress={() => navigation.navigate("DocumentDetail", { docId: item.id })}>
          <Card style={styles.card}>
            <Card.Content>
              <View style={styles.row}>
                <Chip
                  style={[styles.typeChip, { backgroundColor: TYPE_COLORS[item.type] + "22" }]}
                  textStyle={{ color: TYPE_COLORS[item.type], fontSize: 11 }}
                  compact
                >
                  {item.type.replace("_", " ")}
                </Chip>
                <Text variant="bodySmall" style={styles.date}>
                  {item.document_date
                    ? format(new Date(item.document_date), "dd MMM yyyy")
                    : format(new Date(item.created_at), "dd MMM yyyy")}
                </Text>
              </View>
              <Text variant="titleSmall" style={styles.title}>
                {item.doctor_name || "Unknown doctor"}
              </Text>
              <Text variant="bodySmall" style={styles.hospital}>
                {item.hospital_name || "Hospital not specified"}
              </Text>
              {item.ocr_status === "pending" || item.ocr_status === "processing" ? (
                <Chip icon="cog-sync" compact style={styles.statusChip}>
                  Processing...
                </Chip>
              ) : item.ocr_status === "completed" && item.ai_summary ? (
                <Text variant="bodySmall" numberOfLines={2} style={styles.summary}>
                  {item.ai_summary}
                </Text>
              ) : null}
            </Card.Content>
          </Card>
        </TouchableOpacity>
      )}
    />
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  list: { padding: 12 },
  card: { marginBottom: 10, elevation: 2 },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  typeChip: { height: 24 },
  date: { color: "#6b7280" },
  title: { fontWeight: "600", marginTop: 4 },
  hospital: { color: "#6b7280", marginTop: 2 },
  summary: { marginTop: 8, color: "#374151", lineHeight: 18 },
  statusChip: { alignSelf: "flex-start", marginTop: 8 },
  empty: { padding: 40, alignItems: "center" },
  emptyHint: { textAlign: "center", color: "#6b7280", marginTop: 8 },
});
