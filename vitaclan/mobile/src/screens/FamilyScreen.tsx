import React, { useState } from "react";
import { View, StyleSheet, FlatList, Alert } from "react-native";
import { Card, Text, Chip, FAB, Portal, Dialog, TextInput, Button } from "react-native-paper";
import { useFamilyMembers } from "../api/hooks";
import { apiClient } from "../api/client";

export default function FamilyScreen() {
  const [familyId, setFamilyId] = useState<string | null>(null);
  const [inviteDialog, setInviteDialog] = useState(false);
  const [createDialog, setCreateDialog] = useState(false);
  const [familyName, setFamilyName] = useState("");
  const [invitePhone, setInvitePhone] = useState("");
  const { data: members, refetch } = useFamilyMembers(familyId || "");

  const createFamily = async () => {
    try {
      const { data } = await apiClient.post("/families/", { name: familyName });
      setFamilyId(data.id);
      setCreateDialog(false);
      setFamilyName("");
    } catch (e: any) {
      Alert.alert("Error", e.response?.data?.detail || "Failed to create family");
    }
  };

  const inviteMember = async () => {
    if (!familyId) return;
    try {
      await apiClient.post(`/families/${familyId}/invite`, {
        phone: invitePhone,
        role: "member",
      });
      Alert.alert("Success", "Member added to family");
      setInviteDialog(false);
      setInvitePhone("");
      refetch();
    } catch (e: any) {
      Alert.alert("Error", e.response?.data?.detail || "Failed to invite");
    }
  };

  if (!familyId) {
    return (
      <View style={styles.empty}>
        <Text variant="titleLarge">Your Clan Awaits</Text>
        <Text variant="bodyMedium" style={styles.emptyText}>
          Create a family group to share health records with your loved ones
        </Text>
        <Button mode="contained" onPress={() => setCreateDialog(true)} style={styles.cta}>
          Create Family
        </Button>

        <Portal>
          <Dialog visible={createDialog} onDismiss={() => setCreateDialog(false)}>
            <Dialog.Title>Name your clan</Dialog.Title>
            <Dialog.Content>
              <TextInput
                label="Family Name"
                value={familyName}
                onChangeText={setFamilyName}
                placeholder="e.g., The Sharma Family"
              />
            </Dialog.Content>
            <Dialog.Actions>
              <Button onPress={() => setCreateDialog(false)}>Cancel</Button>
              <Button onPress={createFamily}>Create</Button>
            </Dialog.Actions>
          </Dialog>
        </Portal>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={members || []}
        keyExtractor={(item: any) => item.user_id}
        contentContainerStyle={styles.list}
        renderItem={({ item }: any) => (
          <Card style={styles.card}>
            <Card.Content style={styles.memberRow}>
              <View>
                <Text variant="titleMedium">Member</Text>
                <Text variant="bodySmall" style={styles.dim}>
                  Joined {new Date(item.joined_at).toLocaleDateString()}
                </Text>
              </View>
              <Chip compact mode="outlined">{item.role}</Chip>
            </Card.Content>
          </Card>
        )}
      />

      <FAB icon="account-plus" style={styles.fab} onPress={() => setInviteDialog(true)} />

      <Portal>
        <Dialog visible={inviteDialog} onDismiss={() => setInviteDialog(false)}>
          <Dialog.Title>Invite Family Member</Dialog.Title>
          <Dialog.Content>
            <TextInput
              label="Phone Number (+91)"
              value={invitePhone}
              onChangeText={setInvitePhone}
              keyboardType="phone-pad"
            />
            <Text variant="bodySmall" style={styles.hint}>
              Member must have a VitaClan account already
            </Text>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setInviteDialog(false)}>Cancel</Button>
            <Button onPress={inviteMember}>Invite</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  list: { padding: 12 },
  card: { marginBottom: 10 },
  memberRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  dim: { color: "#6b7280" },
  empty: { flex: 1, justifyContent: "center", alignItems: "center", padding: 40 },
  emptyText: { textAlign: "center", color: "#6b7280", marginTop: 8, marginBottom: 24 },
  cta: { marginTop: 12 },
  fab: { position: "absolute", right: 16, bottom: 16 },
  hint: { color: "#6b7280", marginTop: 8 },
});
