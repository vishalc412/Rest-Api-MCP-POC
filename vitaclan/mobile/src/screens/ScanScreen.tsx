import React, { useState, useRef } from "react";
import { View, StyleSheet, Text, TouchableOpacity, Alert } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { Button, SegmentedButtons, ActivityIndicator } from "react-native-paper";
import * as Haptics from "expo-haptics";
import { useUploadDocument } from "../api/hooks";

const DOC_TYPES = [
  { value: "prescription", label: "Prescription" },
  { value: "lab_report", label: "Lab Report" },
  { value: "bill", label: "Bill" },
];

export default function ScanScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [docType, setDocType] = useState("prescription");
  const [scanning, setScanning] = useState(false);
  const cameraRef = useRef<CameraView>(null);
  const { mutateAsync: uploadDocument, isPending } = useUploadDocument();

  const handleCapture = async () => {
    if (!cameraRef.current || scanning) return;
    setScanning(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: false,
      });

      if (!photo?.uri) throw new Error("No photo captured");

      const result = await uploadDocument({
        uri: photo.uri,
        docType,
        language: "en",
      });

      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      Alert.alert(
        "Scan Successful!",
        `Your ${docType.replace("_", " ")} is being processed. AI summary will be ready shortly.`,
        [{ text: "OK" }]
      );
    } catch (err) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert("Scan Failed", "Please try again with better lighting.");
    } finally {
      setScanning(false);
    }
  };

  if (!permission?.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>Camera access needed to scan documents</Text>
        <Button mode="contained" onPress={requestPermission}>Allow Camera</Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} facing="back">
        {/* Scan guide overlay */}
        <View style={styles.overlay}>
          <View style={styles.scanGuide} />
          <Text style={styles.guideText}>Align document within frame</Text>
        </View>
      </CameraView>

      <View style={styles.controls}>
        <Text style={styles.label}>Document Type</Text>
        <SegmentedButtons
          value={docType}
          onValueChange={setDocType}
          buttons={DOC_TYPES}
          style={styles.segmented}
        />
        <TouchableOpacity
          style={[styles.captureBtn, (scanning || isPending) && styles.captureBtnDisabled]}
          onPress={handleCapture}
          disabled={scanning || isPending}
        >
          {isPending ? (
            <ActivityIndicator color="white" />
          ) : (
            <View style={styles.captureInner} />
          )}
        </TouchableOpacity>
        <Text style={styles.hint}>
          {isPending ? "Processing..." : "Tap to scan"}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  camera: { flex: 1 },
  message: { color: "white", textAlign: "center", margin: 20 },
  overlay: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  scanGuide: {
    width: 280,
    height: 360,
    borderWidth: 2,
    borderColor: "#4CAF50",
    borderRadius: 12,
    backgroundColor: "transparent",
  },
  guideText: {
    color: "white",
    marginTop: 12,
    fontSize: 14,
    opacity: 0.8,
  },
  controls: {
    backgroundColor: "#1a1a2e",
    padding: 20,
    paddingBottom: 40,
    alignItems: "center",
  },
  label: { color: "white", marginBottom: 10, fontSize: 14, fontWeight: "600" },
  segmented: { marginBottom: 20, width: "100%" },
  captureBtn: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: "#4CAF50",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 4,
    borderColor: "white",
  },
  captureBtnDisabled: { backgroundColor: "#888" },
  captureInner: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "white",
  },
  hint: { color: "rgba(255,255,255,0.6)", marginTop: 10, fontSize: 12 },
});
