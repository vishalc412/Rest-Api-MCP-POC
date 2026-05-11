import React, { useState, useEffect } from "react";
import { View, StyleSheet, ScrollView, TouchableOpacity } from "react-native";
import { Text, Card, ActivityIndicator, IconButton } from "react-native-paper";
import * as Speech from "expo-speech";
import { useVoiceQuery } from "../api/hooks";

// Note: For production voice input, integrate @react-native-voice/voice (native module)
// or expo-speech-recognition. This screen uses text input as a fallback for Expo Go.
export default function VoiceScreen() {
  const [query, setQuery] = useState("");
  const [conversation, setConversation] = useState<{ role: "user" | "ai"; text: string }[]>([]);
  const { mutateAsync, isPending } = useVoiceQuery();

  const askQuestion = async (text: string) => {
    if (!text.trim()) return;
    setConversation((c) => [...c, { role: "user", text }]);
    setQuery("");
    try {
      const result = await mutateAsync({ query: text, language: "en" });
      setConversation((c) => [...c, { role: "ai", text: result.answer }]);
      Speech.speak(result.answer.split("⚠️")[0], { language: "en-IN", rate: 0.95 });
    } catch (e: any) {
      setConversation((c) => [...c, { role: "ai", text: "Sorry, I couldn't process that." }]);
    }
  };

  const suggestions = [
    "What medicines am I taking?",
    "When was my last blood test?",
    "Show my recent prescriptions",
    "What are my allergies?",
  ];

  return (
    <View style={styles.container}>
      <ScrollView style={styles.chat} contentContainerStyle={styles.chatContent}>
        {conversation.length === 0 && (
          <View>
            <Text variant="titleMedium" style={styles.welcome}>
              Ask me about your health records
            </Text>
            {suggestions.map((s, i) => (
              <TouchableOpacity key={i} onPress={() => askQuestion(s)}>
                <Card style={styles.suggestion}>
                  <Card.Content>
                    <Text>{s}</Text>
                  </Card.Content>
                </Card>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {conversation.map((msg, i) => (
          <View
            key={i}
            style={[styles.bubble, msg.role === "user" ? styles.userBubble : styles.aiBubble]}
          >
            <Text style={msg.role === "user" ? styles.userText : styles.aiText}>{msg.text}</Text>
          </View>
        ))}

        {isPending && (
          <View style={styles.aiBubble}>
            <ActivityIndicator size="small" />
          </View>
        )}
      </ScrollView>

      <View style={styles.inputBar}>
        <Text style={styles.inputText} numberOfLines={1}>
          {query || "Tap mic to speak..."}
        </Text>
        <IconButton
          icon="microphone"
          mode="contained"
          onPress={() => {
            // TODO: integrate native STT — for now use last suggestion
            askQuestion(suggestions[0]);
          }}
          disabled={isPending}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fa" },
  chat: { flex: 1 },
  chatContent: { padding: 12 },
  welcome: { textAlign: "center", marginVertical: 20, color: "#6b7280" },
  suggestion: { marginBottom: 8, backgroundColor: "white" },
  bubble: { padding: 12, borderRadius: 12, marginBottom: 8, maxWidth: "85%" },
  userBubble: { backgroundColor: "#1a1a2e", alignSelf: "flex-end" },
  aiBubble: { backgroundColor: "white", alignSelf: "flex-start", elevation: 1 },
  userText: { color: "white" },
  aiText: { color: "#374151" },
  inputBar: {
    flexDirection: "row",
    alignItems: "center",
    padding: 8,
    backgroundColor: "white",
    borderTopWidth: 1,
    borderColor: "#e5e7eb",
  },
  inputText: { flex: 1, paddingHorizontal: 12, color: "#6b7280" },
});
