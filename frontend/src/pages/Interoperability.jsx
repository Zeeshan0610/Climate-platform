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

export default function Interoperability() {
  const { colorBlind } = useAccessibility();
  const colors = chartColors(colorBlind);
  const { data, loading, error } = useFetch("/interoperability-score");

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} />;

  const pairs = (data.pairs || []).map((p) => ({ ...p, pair: `${p.source_a} ↔ ${p.source_b}` }));

  return (
    <Box>
      <Typography variant="h4" component="h2" gutterBottom>
        Interoperability
      </Typography>

      <Box sx={{ mb: 3, maxWidth: 360 }}>
        <StatCard
          title="Overall Integration Score"
          value={data.overall_score}
          unit="%"
          color="info.main"
        />
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardHeader
          title="Source Compatibility Scores"
          titleTypographyProps={{ variant: "h6", component: "h3" }}
        />
        <CardContent sx={{ height: 360 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={pairs}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="pair" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="schema_compatibility" name="Schema" fill={colors[0]} />
              <Bar dataKey="semantic_compatibility" name="Semantic" fill={colors[1]} />
              <Bar dataKey="mapping_success_rate" name="Mapping Success" fill={colors[2]} />
              <Bar dataKey="integration_score" name="Integration" fill={colors[3]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader
          title="Compatibility Matrix"
          titleTypographyProps={{ variant: "h6", component: "h3" }}
        />
        <CardContent>
          <Table size="small" aria-label="Interoperability compatibility matrix">
            <TableHead>
              <TableRow>
                <TableCell>Source Pair</TableCell>
                <TableCell align="right">Schema %</TableCell>
                <TableCell align="right">Semantic %</TableCell>
                <TableCell align="right">Mapping Success %</TableCell>
                <TableCell align="right">Integration Score</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pairs.map((p) => (
                <TableRow key={p.pair}>
                  <TableCell component="th" scope="row">
                    {p.pair}
                  </TableCell>
                  <TableCell align="right">{p.schema_compatibility}</TableCell>
                  <TableCell align="right">{p.semantic_compatibility}</TableCell>
                  <TableCell align="right">{p.mapping_success_rate}</TableCell>
                  <TableCell align="right">{p.integration_score}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}
