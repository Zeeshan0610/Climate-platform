import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import useFetch from "../api/useFetch";
import { ErrorMessage, Loading } from "../components/Loading";
import { useAccessibility } from "../context/AccessibilityContext";
import { chartColors } from "../theme/buildTheme";

const METRICS = [
  { value: "temperature", label: "Temperature (°C)" },
  { value: "rainfall", label: "Rainfall (mm)" },
  { value: "humidity", label: "Humidity (%)" },
];

export default function Forecast() {
  const { colorBlind } = useAccessibility();
  const colors = chartColors(colorBlind);
  const [metric, setMetric] = useState("temperature");
  const [periods, setPeriods] = useState(12);

  const { data, loading, error } = useFetch(
    `/forecast?metric=${metric}&periods=${periods}`,
    [metric, periods]
  );

  const combined = [];
  if (data) {
    data.history.forEach((h) => combined.push({ date: h.date, historical: h.value }));
    data.forecast.forEach((f) => combined.push({ date: f.date, predicted: f.value }));
  }

  return (
    <Box>
      <Typography variant="h4" component="h2" gutterBottom>
        Climate Forecast
      </Typography>

      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 3 }} alignItems="center">
        <TextField
          select
          label="Metric"
          value={metric}
          onChange={(e) => setMetric(e.target.value)}
          sx={{ minWidth: 220 }}
          aria-label="Forecast metric"
        >
          {METRICS.map((m) => (
            <MenuItem key={m.value} value={m.value}>
              {m.label}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          select
          label="Forecast horizon (months)"
          value={periods}
          onChange={(e) => setPeriods(Number(e.target.value))}
          sx={{ minWidth: 220 }}
          aria-label="Forecast horizon in months"
        >
          {[6, 12, 18, 24].map((p) => (
            <MenuItem key={p} value={p}>
              {p} months
            </MenuItem>
          ))}
        </TextField>
        {data && <Chip label={`Model: ${data.model}`} color="primary" />}
      </Stack>

      {loading && <Loading />}
      {error && <ErrorMessage error={error} />}

      {data && (
        <Card>
          <CardHeader
            title="Historical vs Predicted"
            titleTypographyProps={{ variant: "h6", component: "h3" }}
          />
          <CardContent sx={{ height: 420 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={combined}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="historical"
                  name="Historical"
                  stroke={colors[0]}
                  dot={false}
                  connectNulls
                />
                <Line
                  type="monotone"
                  dataKey="predicted"
                  name="Predicted"
                  stroke={colors[3]}
                  strokeDasharray="6 4"
                  dot={false}
                  connectNulls
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
