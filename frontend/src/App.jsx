import { CssBaseline, ThemeProvider } from "@mui/material";
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAccessibility } from "./context/AccessibilityContext";
import { buildTheme } from "./theme/buildTheme";
import Accessibility from "./pages/Accessibility";
import Analytics from "./pages/Analytics";
import DataQuality from "./pages/DataQuality";
import Forecast from "./pages/Forecast";
import Home from "./pages/Home";
import Interoperability from "./pages/Interoperability";
import Login from "./pages/Login";
import { useMemo } from "react";

export default function App() {
  const { themeMode, fontScale } = useAccessibility();
  const theme = useMemo(() => buildTheme(themeMode, fontScale), [themeMode, fontScale]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Home />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/accessibility" element={<Accessibility />} />
          <Route path="/data-quality" element={<DataQuality />} />
          <Route path="/interoperability" element={<Interoperability />} />
          <Route path="/forecast" element={<Forecast />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ThemeProvider>
  );
}
