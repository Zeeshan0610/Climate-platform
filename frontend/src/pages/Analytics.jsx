import {
  Box,
  Card,
  CardContent,
  CardHeader,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import {
  Bar,
  BarChart,
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

function ChartCard({ title, children }) {
  return (
    <Card>
      <CardHeader title={title} titleTypographyProps={{ variant: "h6", component: "h3" }} />
      <CardContent sx={{ height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export default function Analytics() {
  const { colorBlind } = useAccessibility();
  const colors = chartColors(colorBlind);
  const [country, setCountry] = useState("");
  const [year, setYear] = useState("");

  const { data: countries } = useFetch("/countries");
  const query = `/analytics?${country ? `country=${encodeURIComponent(country)}&` : ""}${
    year ? `year=${year}` : ""
  }`;
  const { data, loading, error } = useFetch(query, [country, year]);
  const { data: ml } = useFetch("/analytics/ml");

  const trends = data?.trends?.series || [];
  const distribution = data?.distribution?.distribution || [];
  const stats = data?.statistics?.stats || {};

  return (
    <Box>
      <Typography variant="h4" component="h2" gutterBottom>
        Climate Analytics
      </Typography>

      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 3 }}>
        <TextField
          select
          label="Country"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          sx={{ minWidth: 200 }}
          aria-label="Filter by country"
        >
          <MenuItem value="">All Countries</MenuItem>
          {(countries || []).map((c) => (
            <MenuItem key={c} value={c}>
              {c}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          select
          label="Year"
          value={year}
          onChange={(e) => setYear(e.target.value)}
          sx={{ minWidth: 160 }}
          aria-label="Filter by year"
        >
          <MenuItem value="">All Years</MenuItem>
          {[2022, 2023].map((y) => (
            <MenuItem key={y} value={y}>
              {y}
            </MenuItem>
          ))}
        </TextField>
      </Stack>

      {loading && <Loading />}
      {error && <ErrorMessage error={error} />}

      {!loading && !error && (
        <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { xs: "1fr", lg: "1fr 1fr" } }}>
          <ChartCard title="Temperature & Humidity Trend">
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="temperature" name="Temp (°C)" stroke={colors[0]} dot={false} />
              <Line type="monotone" dataKey="humidity" name="Humidity (%)" stroke={colors[1]} dot={false} />
            </LineChart>
          </ChartCard>

          <ChartCard title="Rainfall Trend">
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="rainfall" name="Rainfall (mm)" stroke={colors[2]} dot={false} />
            </LineChart>
          </ChartCard>

          <ChartCard title="Average Temperature by Country">
            <BarChart data={distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="country" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_temperature" name="Avg Temp (°C)" fill={colors[0]} />
              <Bar dataKey="avg_humidity" name="Avg Humidity (%)" fill={colors[1]} />
            </BarChart>
          </ChartCard>

          <Card>
            <CardHeader
              title="Statistical Summary"
              titleTypographyProps={{ variant: "h6", component: "h3" }}
            />
            <CardContent>
              <Table size="small" aria-label="Statistical summary of climate metrics">
                <TableHead>
                  <TableRow>
                    <TableCell>Metric</TableCell>
                    <TableCell align="right">Mean</TableCell>
                    <TableCell align="right">Median</TableCell>
                    <TableCell align="right">Std Dev</TableCell>
                    <TableCell align="right">Variance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(stats).map(([metric, s]) => (
                    <TableRow key={metric}>
                      <TableCell component="th" scope="row">
                        {metric}
                      </TableCell>
                      <TableCell align="right">{s.mean}</TableCell>
                      <TableCell align="right">{s.median}</TableCell>
                      <TableCell align="right">{s.std}</TableCell>
                      <TableCell align="right">{s.variance}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Box>
      )}

      {ml && ml.models && ml.models.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardHeader
            title="Machine Learning Model Comparison (Temperature Prediction)"
            titleTypographyProps={{ variant: "h6", component: "h3" }}
          />
          <CardContent>
            <Table size="small" aria-label="Machine learning model metrics">
              <TableHead>
                <TableRow>
                  <TableCell>Model</TableCell>
                  <TableCell align="right">MAE</TableCell>
                  <TableCell align="right">RMSE</TableCell>
                  <TableCell align="right">R²</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {ml.models.map((m) => (
                  <TableRow key={m.model} selected={m.model === ml.best_model}>
                    <TableCell component="th" scope="row">
                      {m.model}
                      {m.model === ml.best_model ? " (best)" : ""}
                    </TableCell>
                    <TableCell align="right">{m.mae}</TableCell>
                    <TableCell align="right">{m.rmse}</TableCell>
                    <TableCell align="right">{m.r2}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
