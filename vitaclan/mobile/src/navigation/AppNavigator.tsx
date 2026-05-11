import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createStackNavigator } from "@react-navigation/stack";
import { IconButton } from "react-native-paper";
import { useAuthStore } from "../stores/authStore";
import LoginScreen from "../screens/LoginScreen";
import TimelineScreen from "../screens/TimelineScreen";
import ScanScreen from "../screens/ScanScreen";
import FamilyScreen from "../screens/FamilyScreen";
import RemindersScreen from "../screens/RemindersScreen";
import BudgetScreen from "../screens/BudgetScreen";
import VoiceScreen from "../screens/VoiceScreen";
import DocumentDetailScreen from "../screens/DocumentDetailScreen";

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function TabIcon({ name, color }: { name: string; color: string }) {
  return <IconButton icon={name} iconColor={color} size={22} style={{ margin: 0 }} />;
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: "#1a1a2e",
        tabBarInactiveTintColor: "#9ca3af",
        headerStyle: { backgroundColor: "#1a1a2e" },
        headerTintColor: "white",
      }}
    >
      <Tab.Screen
        name="Records"
        component={TimelineScreen}
        options={{
          tabBarIcon: ({ color }) => <TabIcon name="file-document" color={color} />,
        }}
      />
      <Tab.Screen
        name="Scan"
        component={ScanScreen}
        options={{
          tabBarIcon: ({ color }) => <TabIcon name="camera" color={color} />,
        }}
      />
      <Tab.Screen
        name="Voice"
        component={VoiceScreen}
        options={{
          tabBarIcon: ({ color }) => <TabIcon name="microphone" color={color} />,
        }}
      />
      <Tab.Screen
        name="Family"
        component={FamilyScreen}
        options={{
          tabBarIcon: ({ color }) => <TabIcon name="account-group" color={color} />,
        }}
      />
      <Tab.Screen
        name="Reminders"
        component={RemindersScreen}
        options={{
          tabBarIcon: ({ color }) => <TabIcon name="bell" color={color} />,
        }}
      />
      <Tab.Screen
        name="Budget"
        component={BudgetScreen}
        options={{
          tabBarIcon: ({ color }) => <TabIcon name="wallet" color={color} />,
        }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const { isAuthenticated } = useAuthStore();

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: "#1a1a2e" }, headerTintColor: "white" }}>
        {isAuthenticated ? (
          <>
            <Stack.Screen
              name="Main"
              component={MainTabs}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="DocumentDetail"
              component={DocumentDetailScreen}
              options={{ title: "Document" }}
            />
          </>
        ) : (
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{ headerShown: false }}
          />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
