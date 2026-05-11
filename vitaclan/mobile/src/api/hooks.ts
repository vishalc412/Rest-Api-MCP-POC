import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";

// --- Documents ---
export const useDocuments = (docType?: string) =>
  useQuery({
    queryKey: ["documents", docType],
    queryFn: async () => {
      const params = docType ? { doc_type: docType } : {};
      const { data } = await apiClient.get("/documents/", { params });
      return data;
    },
  });

export const useDocumentSummary = (docId: string, enabled: boolean) =>
  useQuery({
    queryKey: ["document-summary", docId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/documents/${docId}/summary`);
      return data;
    },
    enabled,
    staleTime: Infinity, // Summary never changes once computed
  });

export const useUploadDocument = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ uri, docType, language }: { uri: string; docType: string; language: string }) => {
      const formData = new FormData();
      formData.append("file", { uri, name: "scan.jpg", type: "image/jpeg" } as unknown as Blob);
      formData.append("doc_type", docType);
      formData.append("language", language);
      const { data } = await apiClient.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
};

// --- Medications ---
export const useMedications = () =>
  useQuery({
    queryKey: ["medications"],
    queryFn: async () => {
      const { data } = await apiClient.get("/medications/");
      return data;
    },
  });

export const useReminders = () =>
  useQuery({
    queryKey: ["reminders"],
    queryFn: async () => {
      const { data } = await apiClient.get("/medications/reminders");
      return data;
    },
  });

// --- Family ---
export const useFamilyMembers = (familyId: string) =>
  useQuery({
    queryKey: ["family-members", familyId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/families/${familyId}/members`);
      return data;
    },
    enabled: !!familyId,
  });

// --- Expenses ---
export const useExpenseSummary = (year?: number, month?: number) =>
  useQuery({
    queryKey: ["expense-summary", year, month],
    queryFn: async () => {
      const { data } = await apiClient.get("/expenses/summary", { params: { year, month } });
      return data;
    },
  });

// --- Voice ---
export const useVoiceQuery = () =>
  useMutation({
    mutationFn: async ({ query, language }: { query: string; language: string }) => {
      const { data } = await apiClient.post("/voice/query", { query, language });
      return data;
    },
  });
