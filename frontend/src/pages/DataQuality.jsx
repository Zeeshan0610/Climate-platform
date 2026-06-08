import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import useFetch from "../api/useFetch";
import StatCard from "../components/StatCard";
import { ErrorMessage, Loading } from "../components/Loading";
import { useAccessibility } from "../context/AccessibilityContext";
import { chartColors } from "../theme/buildTheme";

export default function DataQuality() {
  const { colorBlind } = useAccessibility();
  const colors = chartColors(colorBlind);
  const { data, loading, error } = useFetch("/quality-metrics");
  const { data: reliability } = useFetch("/reliability-score");

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} />;

  const datasets = data.datasets || [];
  const radarData = ["completeness", "consistency", "validity", "accuracy", "timeliness"].map(
    (dim) => {
      const row = { dimension: dim };
      datasets.forEach((d) => {
        row[d.dataset_name] = d[dim];
      });
      return row;
    }
  );

  return (
    <Box>
      <Typography variant="h4" component="h2" gutterBottom>
        Data Quality
      </Typography>

      <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, mb: 3 }}>
        <StatCard
          title="Overall Data Quality Score"
          value={data.overall_score}
          unit="%"
          color="success.main"
        />
        <StatCard
          title="Average Reliability Score"
          value={reliability?.overall_score ?? "-"}
          unit="%"
          color="info.main"
        />
      </Box>

      <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { xs: "1fr", lg: "1fr 1fr" }, mb: 3 }}>
        <Card>
          <CardHeader title="Quality Dimensions by Dataset" titleTypographyProps={{ variant: "h6", component: "h3" }} />
          <CardContent sx={{ height: 340 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={datasets}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dataset_name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="completeness" name="Completeness" fill={colors[0]} />
                <Bar dataKey="consistency" name="Consistency" fill={colors[1]} />
                <Bar dataKey="validity" name="Validity" fill={colors[2]} />
                <Bar dataKey="accuracy" name="Accuracy" fill={colors[3]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title="Quality Heatmap (Radar)" titleTypographyProps={{ variant: "h6", component: "h3" }} />
          <CardContent sx={{ height: 340 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="dimension" />
                <PolarRadiusAxis domain={[0, 100]} />
                {datasets.map((d, i) => (
                  <Radar
                    key={d.dataset_name}
                    name={d.dataset_name}
                    dataKey={d.dataset_name}
                    stroke={colors[i % colors.length]}
                    fill={colors[i % colors.length]}
                    fillOpacity={0.3}
                  />
                ))}
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Box>

      <Card>
        <CardHeader title="Per-Dataset Quality Metrics" titleTypographyProps={{ variant: "h6", component: "h3" }} />
        <CardContent>
          <Table size="small" aria-label="Per dataset data quality metrics">
            <TableHead>
              <TableRow>
                <TableCell>Dataset</TableCell>
                <TableCell align="right">Completeness</TableCell>
                <TableCell align="right">Consistency</TableCell>
                <TableCell align="right">Validity</TableCell>
                <TableCell align="right">Accuracy</TableCell>
                <TableCell align="right">Timeliness</TableCell>
                <TableCell align="right">Overall</TableCell>
                <TableCell align="right">Dups Removed</TableCell>
                <TableCell align="right">Outliers</TableCell>
                <TableCell align="right">Imputed</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {datasets.map((d) => (
                <TableRow key={d.dataset_name}>
                  <TableCell component="th" scope="row">
                    {d.dataset_name}
                  </TableCell>
                  <TableCell align="right">{d.completeness}</TableCell>
                  <TableCell align="right">{d.consistency}</TableCell>
                  <TableCell align="right">{d.validity}</TableCell>
                  <TableCell align="right">{d.accuracy}</TableCell>
                  <TableCell align="right">{d.timeliness}</TableCell>
                  <TableCell align="right">{d.overall}</TableCell>
                  <TableCell align="right">{d.duplicates_removed}</TableCell>
                  <TableCell align="right">{d.outliers_detected}</TableCell>
                  <TableCell align="right">{d.missing_imputed}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}
