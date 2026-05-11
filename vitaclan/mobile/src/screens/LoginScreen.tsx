import React, { useState } from "react";
import { View, StyleSheet, Text, KeyboardAvoidingView, Platform } from "react-native";
import { TextInput, Button, Snackbar } from "react-native-paper";
import { useAuthStore } from "../stores/authStore";

export default function LoginScreen() {
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { sendOtp, verifyOtp } = useAuthStore();

  const handleSendOtp = async () => {
    if (phone.length < 10) {
      setError("Enter valid 10-digit phone");
      return;
    }
    setLoading(true);
    try {
      await sendOtp(phone);
      setStep("otp");
    } catch (e: any) {
      setError(e.response?.data?.detail || "Failed to send OTP");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (code.length !== 6) {
      setError("Enter 6-digit OTP");
      return;
    }
    setLoading(true);
    try {
      await verifyOtp(phone, code, name || undefined);
    } catch (e: any) {
      setError(e.response?.data?.detail || "Invalid OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.container}
    >
      <View style={styles.header}>
        <Text style={styles.title}>VitaClan</Text>
        <Text style={styles.tagline}>Vital records for your clan</Text>
      </View>

      <View style={styles.form}>
        {step === "phone" ? (
          <>
            <TextInput
              label="Phone Number"
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
              maxLength={10}
              left={<TextInput.Affix text="+91" />}
              mode="outlined"
              style={styles.input}
            />
            <Button
              mode="contained"
              onPress={handleSendOtp}
              loading={loading}
              disabled={loading}
              style={styles.button}
            >
              Send OTP
            </Button>
          </>
        ) : (
          <>
            <TextInput
              label="Your Name"
              value={name}
              onChangeText={setName}
              mode="outlined"
              style={styles.input}
            />
            <TextInput
              label="6-digit OTP"
              value={code}
              onChangeText={setCode}
              keyboardType="number-pad"
              maxLength={6}
              mode="outlined"
              style={styles.input}
            />
            <Button
              mode="contained"
              onPress={handleVerify}
              loading={loading}
              disabled={loading}
              style={styles.button}
            >
              Verify & Continue
            </Button>
            <Button onPress={() => setStep("phone")}>Change phone number</Button>
          </>
        )}

        <Text style={styles.consent}>
          By continuing, you agree to VitaClan's DPDP-compliant data processing.
          Your medical data is stored in India and never shared without consent.
        </Text>
      </View>

      <Snackbar visible={!!error} onDismiss={() => setError("")} duration={3000}>
        {error}
      </Snackbar>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7fa" },
  header: { alignItems: "center", paddingTop: 80, paddingBottom: 40 },
  title: { fontSize: 36, fontWeight: "800", color: "#1a1a2e" },
  tagline: { fontSize: 14, color: "#6b7280", marginTop: 4 },
  form: { paddingHorizontal: 24 },
  input: { marginBottom: 16, backgroundColor: "white" },
  button: { marginTop: 8, paddingVertical: 6 },
  consent: { fontSize: 11, color: "#9ca3af", textAlign: "center", marginTop: 30 },
});
